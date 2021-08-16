#!/bin/bash python
from __future__ import absolute_import
import sys
import os

sys.path.append("..")
from waitress import serve
from logs import *
from app import make_app
from backend import settings

app = make_app(settings.ProductionConfig)

set_logger_handlers(app)

PORT = os.environ.get("FLASK_RUN_PORT", 80)

serve(app, port=PORT)
