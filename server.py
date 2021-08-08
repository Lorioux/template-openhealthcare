#!/bin/bash python

from __future__ import absolute_import


import sys
import logging
from logging.handlers import RotatingFileHandler
from waitress import serve
from flask import request

sys.path.append("..")

from backend.settings import ProductionConfig
from app import make_app



log = logging.getLogger("werkzeug")
logging.basicConfig(
    level=logging.INFO,
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler = RotatingFileHandler("./.logs/app.log", maxBytes=1000000, backupCount=1)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logger = logging.Logger("werkzeug", logging.DEBUG)

app = make_app(ProductionConfig, handler)


@app.before_first_request
def setup_logging():
    if app.debug:
        log.addHandler(logging.StreamHandler(stream=sys.stdout))
    else:
        log.addHandler(handler)


@app.after_request
def log_request(response):
    logging.log(
        logging.DEBUG,
        msg="REQ: {} {} {}".format(request.method, request.path, response.status_code),
    )
    return response


serve(app, port=80)
