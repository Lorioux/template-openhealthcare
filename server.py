#!/bin/bash python
from __future__ import absolute_import
from waitress import serve
from backend.settings import ProductionConfig
from logs import *
from app import make_app


app = make_app(ProductionConfig)

set_logger_handlers(app)

serve(app, port=80)
