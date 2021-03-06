import os
import sys

from dotenv.main import load_dotenv

sys.path.append("..")

from dotenv import get_key, set_key

__here__ = os.path.abspath(os.path.dirname(__file__))


class VARIABLES(object):
    def __init__(self) -> None:
        super().__init__()

        self.PSQL_CONNECT_TIMEOUT = os.environ.get("PSQL_CONNECT_TIMEOUT", 10)
        self.PSQL_SERVER_PORT = os.environ.get("PSQL_SERVER_PORT", 5432)

        self.BOOKING = {
            "PSQL_USERNAME": os.environ.get("PSQL_USERNAME", "postgres"),
            "PSQL_PASSWORD": os.environ.get("PSQL_PASSWORD", "password"),
            "PSQL_SERVER_PORT": self.PSQL_SERVER_PORT,
            "PSQL_HOSTNAME": os.environ.get("PSQL_HOSTNAME", "localhost"),
            "PSQL_DATABASE": os.environ.get("PSQL_DB_BOOKING", "postgres"),
            "PSQL_CONNECT_TIMEOUT": self.PSQL_CONNECT_TIMEOUT,
        }

        self.PROFILES = self.BOOKING.copy()
        self.PROFILES["PSQL_DATABASE"] = os.environ.get("PSQL_DB_PROFILES", "postgres")

        self.SCHEDULES = self.BOOKING.copy()
        self.SCHEDULES["PSQL_DATABASE"] = os.environ.get(
            "PSQL_DB_SCHEDULES", "postgres"
        )

        self.SUBSCRIBERS = self.BOOKING.copy()
        self.SUBSCRIBERS["PSQL_DATABASE"] = os.environ.get(
            "PSQL_DB_SUBSCRIBERS", "postgres"
        )

        self.set_secret()

    def set_secret(self):
        if load_dotenv("./.env"):
            environ = os.getenv("FLASK_ENV", '').__eq__("production")
            secret = os.getenv("SECRET_KEY", '').__eq__("")
        if secret:
            SECRET_KEY = os.urandom(64).hex("-")
            os.environ["SECRET_KEY"] = SECRET_KEY

            if environ:
                # if environ is in production
                set_key(f"{__here__}.env", "SECRET_KEY", SECRET_KEY)

        # print(os.environ.get('FLASK_PORT'))
        pass


class Config:
    """
    Base configuration class. Contains default configuration settings +
     configuration settings applicable to all environments.
    """

    VARIABLES = VARIABLES()

    # Default settings
    ENV = "development"
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True

    # Settings applicable to all environments
    SECRET_KEY = os.environ.get("SECRET_KEY")

    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", default="")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", default="")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME", default="")
    MAIL_SUPPRESS_SEND = False

    JSONIFY_PRETTYPRINT_REGULAR = True

    # PSQL_CONNECT_TO = os.environ.get('PSQL_CONNECT_TOUT', 10)
    # PSQL_SERVER_PO = os.environ.get('POSL_SERVER_PORT', 5432)

    BOOKING = VARIABLES.BOOKING

    PROFILES = VARIABLES.PROFILES
    # PROFILES['PSQL_DATABASE'] = os.environ.get('PSQL_DB_PROFILES', 'donatecare')

    SCHEDULES = VARIABLES.SCHEDULES
    # SCHEDULES['PSQL_DATABASE'] = os.environ.get('PSQL_DB_SCHEDULES', 'donatecare')

    SUBSCRIBERS = VARIABLES.SUBSCRIBERS
    # SUBSCRIBERS['PSQL_DATABASE'] = os.environ.get('PSQL_DB_SUBSCRIBERS', 'donatecare')

    PSQL_CONNECT_URL = "postgresql://%(PSQL_USERNAME)s:%(PSQL_PASSWORD)s@%(PSQL_HOSTNAME)s:%(PSQL_SERVER_PORT)s/%(PSQL_DATABASE)s?connect_timeout=%(PSQL_CONNECT_TIMEOUT)s&application_name=OHCS"

    SQLALCHEMY_BINDS = {
        "booking": f"{PSQL_CONNECT_URL}" % BOOKING,
        "profiles": f"{PSQL_CONNECT_URL}" % PROFILES,
        "schedules": f"{PSQL_CONNECT_URL}" % SCHEDULES,
        "subscribers": f"{PSQL_CONNECT_URL}" % SUBSCRIBERS,
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True

    SESSION_REFRESH_EACH_REQUEST = True

    SESSION_COOKIE_NAME = "openhealthcare"

    JSONIFY_PRETTYPRINT_REGULAR = True
    # SERVER_NAME = "openhcs.localhost"


class TestingConfig(Config):

    SECRET_KEY = "ncamcajdansdkasaiskdaslfaljfoanjoakpmsdpadnaojfoamfanfo"

    ENV = "development"

    TESTING = True

    DEBUG = True

    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True

    SESSION_REFRESH_EACH_REQUEST = True

    SESSION_COOKIE_NAME = "openhealthcare"

    JSONIFY_PRETTYPRINT_REGULAR = True

    # SQLALCHEMY_BINDS = {
    #     "booking": "sqlite:///databases/booking.db",
    #     "profiles": "sqlite:///databases/profiles.db",
    #     "schedules": "sqlite:///databases/schedules.db",
    #     "subscribers": "sqlite:///databases/subscribers.db",
    # }
    # SERVER_NAME = "openhcs.localhost"


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False
    WTF_CSRF_ENABLED = True
    MAIL_SUPPRESS_SEND = True

    SESSION_REFRESH_EACH_REQUEST = True
