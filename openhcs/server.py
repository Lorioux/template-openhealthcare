#!/bin/bash python
from __future__ import absolute_import
import sys
import os

sys.path.append("..")
from waitress import serve
from openhcs.logs import *
from openhcs.app import make_app
from openhcs import settings

app = make_app(settings.ProductionConfig)

set_logger_handlers(app)

PORT = os.environ.get("FLASK_RUN_PORT", 80)

serve(app, port=PORT)
