import logging
from logging.handlers import SMTPHandler
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from flask.logging import default_handler


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

mail_handler = SMTPHandler(
    mailhost="127.0.0.1",
    fromaddr="server-error@ohc.io",
    toaddrs=["admin@ohc.io"],
    subject="Application Error",
)

mail_handler.setLevel(logging.ERROR)
mail_handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
)

filehandler = RotatingFileHandler("./.logs/app.log", maxBytes=10000000, backupCount=1)


def set_logger_handlers(app):
    for logger in (
        app.logger,
        logging.getLogger("werkzeug"),
        logging.getLogger("sqlalchemy"),
    ):
        if not app.debug:

            logger.addHandler(filehandler)
            logger.addHandler(mail_handler)
        else:
            logger.addHandler(default_handler)
            logger.addHandler(mail_handler)
