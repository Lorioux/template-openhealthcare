#!/bin/env python
from __future__ import absolute_import


import os
import logging
from flasgger import Swagger
from flask import Flask, jsonify, json


from backend import initialize_dbase, dbase, settings
from backend.registration.microservice import profiles
from backend.booking.microservice import bookings
from backend.scheduling.microservice import schedules
from backend.authentication.microservice import auth


def api_configurations(app: Flask, template):
    template["servers"][0]["variables"]["port"]["default"] = os.environ.get(
        "FLASK_RUN_PORT"
    )
    app.config["SWAGGER"] = {
        "title": "OHC API",
        "uiversion": 3,
        "openapi": "3.0.1",
        "basePath": "/v1",
    }
    swagger = Swagger(app, template=template)
    # print(swagger.template['servers'][0]['variables'])
    pass


def make_app(environment=None, log_handler=None):
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

    with open("./swagger/openapi.json") as file:
        template = json.loads(file.read())
        api_configurations(app, template)
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
        return jsonify({"status": "ok", "apiversion": "1.0.0"})

    return app


if __name__ == "__main__":
    make_app()
