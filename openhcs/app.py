#!/bin/env python
from __future__ import absolute_import
import os
from pathlib import Path
import logging
from flasgger import Swagger
from flask import Flask
from flask import jsonify
from flask  import json
from openhcs import initialize_dbase, dbase, settings
from openhcs.registration.microservice import profiles
from openhcs.booking.microservice import bookings
from openhcs.scheduling.microservice import schedules
from openhcs.authentication.microservice import auth

__here__ = os.path.abspath(os.path.dirname(__file__))
Base_path = Path(__here__).parent


def configure_swagger(app: Flask, template):
    servers = [
        {
            "url": "{protocol}://{hostname}:{port}/{basePath}/",
            "description": "Production secure server",
            "variables": {
                "protocol": {"default": "https", "enum": ["https", "http"]},
                "hostname": {"default": "127.0.0.1"},
                "port": {"default": "80", "enum": ["8080", "443", "80"]},
                "basePath": {"default": "v1"},
            },
        }
    ]

    app.config["SWAGGER"] = {
        "title": "OHCS API",
        "uiversion": 3,
        "openapi": "3.0.1",
        "basePath": "/v1",
    }
    # template["servers"] = servers
    oauth2 = {
        "description": "TOBE Implemented. DON'T USE",
        "type": "oauth2",
        "flows": {
            "implicit": {
                "authorizationUrl": "http://members.donatecare.io/auth/dialog",
                "scopes": {
                    "write": "Grants write access",
                    "read": "Grants read access",
                    "admin": "Grants admin access",
                },
            }
        },
        "x-tokenInfoFunc": "swagger_server.controllers.authorization_controller.check_oauth2",
    }
    if not app.debug:
        servers[0]["variables"]["hostname"]["default"] = os.environ.get(
            "FLASK_RUN_HOST", "127.0.0.1"
        )
        port = os.getenv("FLASK_RUN_PORT", "80")
        servers[0]["variables"]["port"]["default"] = port
        if port in ["80", "8080"]:
            servers[0]["variables"]["protocol"]["default"] = "http"
        template["components"]["securitySchemes"].__delitem__("api_key")
        template["servers"] = servers

    Swagger(app, template=template)
    pass


def make_app(environment=None):
    app = Flask(__name__, instance_relative_config=True)

    if environment:
        app.config.from_object(environment)
    else:
        app.config.from_object(settings.DevelopmentConfig)

    try:
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)
    except OSError as error:
        logging.exception(error, stack_info=True)

    with open(f"{__here__}/swagger/openapi.json") as file:
        template = json.loads(file.read())
        configure_swagger(app, template)
        file.close()

    # initialize databases
    dbase.init_app(app)

    with app.app_context():
        initialize_dbase(app)
        app.register_blueprint(profiles)
        app.register_blueprint(bookings)
        app.register_blueprint(schedules)
        app.register_blueprint(auth)

    @app.route("/")
    def index():
        environment=os.getenv("DEPLOYMENT_ENVIRONMENT", '')
        domain_name=os.getenv("FLASK_RUN_HOST", '')
        version = os.getenv("VERSION", 1)
        return jsonify({
            "status": "ok", 
            "apiversion": version, 
            "summaries": {
                "apiName": "The open heathcare services",
                "environment":  environment,
                "domainName": domain_name
        }})

    return app


if __name__ == "__main__":
    make_app()
