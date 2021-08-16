from __future__ import absolute_import

from enum import Enum
import logging
import uuid
from datetime import timedelta, datetime
from functools import wraps
from logging import Logger

import jwt
from sqlalchemy.sql.elements import and_
from flask import Blueprint, request, jsonify, json, session, make_response, current_app
from werkzeug.security import *

from openhcs.authentication.models import Subscriber, AuthenticationKey


auth = Blueprint("auth", __name__, url_prefix="/v1/members")


class KeyType(Enum):
    TYPE_ONE = (1, "USER_NAME")
    TYPE_TWO = (2, "PUBLIC_ID")
    TYPE_THREE = (3, "PASSWD")


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        autho = request.cookies.get("token")

        if autho is None:
            return jsonify({"error": "Not authenticated! Try to login again."})

        try:
            data = jwt.decode(
                autho, current_app.config["SECRET_KEY"], algorithms="HS256"
            )
            current_user = retrieve_subscriber(data)
            if current_user is None:
                raise jwt.InvalidTokenError
        except RuntimeError as error:
            Logger("AUTH").error(error)
            return jsonify({"message": "Token is invalid"})

        except jwt.ExpiredSignatureError as error:
            Logger("AUTH").error(error)
            return make_response(
                {"Error": "Session expired", "message": "Try to login again"},
                403,
                {"WWW-Authenticate": 'Bearer realm="Login required"'},
            )
        except jwt.InvalidTokenError as error:
            Logger("AUTH").error(error)
            return make_response(
                {"Error": "Invalid credentials", "message": "Try to login again"},
                403,
                {"WWW-Authenticate": 'Bearer realm="Login required"'},
            )

        return f(current_user, *args, **kwargs)

    return decorator


@auth.route("/createCredentials", methods=["POST"])
def create_credencials():
    try:
        data = json.loads(request.data)

        passwd = generate_password_hash(data["password"], method="sha256")
        username = data["phone"]
        fullname = generate_password_hash(data["fullname"], method="sha256")
        public_id = uuid.uuid3(
            uuid.NAMESPACE_URL, "{}-{}".format(data["phone"], data["role"])
        )
        data["password"] = passwd
        data["username"] = username
        data["fullname"] = fullname
        data["publicid"] = str(public_id)

        subscriber = Subscriber(data=data)
        exists, user = subscriber.validate()

        if exists:
            print(exists, user)
            return make_response(
                {"response": "Failed to register with provided data."}, 403
            )

        user = subscriber.save()

        if user is not None:
            token = jwt.encode(
                {
                    "public_id": user.public_id,
                    "user_name": user.user_name,
                    "exp": datetime.utcnow() + timedelta(minutes=30),
                    "iat": datetime.utcnow(),
                },
                current_app.config["SECRET_KEY"],
                algorithm="HS256",
            )
            response = make_response({"response": "Subscribed successfully"}, 200)
            response.set_cookie("token", token)
            response.headers.set("Authorization", token)
            return response
    except RuntimeError as error:
        logging.exception(error, stack_info=True)


@auth.route("/authenticate", methods=["POST"])
def authenticate():
    data = request.args.to_dict(flat=True)
    if data is None or data == {}:
        data = json.loads(request.data)

    if not data or not data["userid"] or not data["password"] or not data["role"]:

        return make_response(
            {
                "Error": "Could not verify",
                "message": "Either role, or phone or password is missing!",
            },
            401,
        )

    user = Subscriber(data={}).get_one(data["userid"], data["role"])
    # print(current_app.config.get("SQLALCHEMY_BINDS"))
    if user is None:
        return make_response(
            {"Error": "Could not verify", "message": "Subscribe to get started!"}, 403
        )

    if check_password_hash(user.password, data["password"]):

        token = jwt.encode(
            {
                "public_id": user.public_id,
                "user_name": user.user_name,
                "exp": datetime.utcnow() + timedelta(minutes=30),
                "iat": datetime.utcnow(),
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        response = make_response({"response": "Logged in successfully", "token": token})
        response.set_cookie("token", token)
        response.headers.add_header("Authentication", f"Bearer {token}")
        return response


@auth.route("/deauthenticate")
@token_required
def deauthenticate(currentuser: Subscriber = None):
    # user = currentuser.full_name
    session.clear()
    response = make_response({"response": "Logged out successfully"})
    response.headers.add("WWW-Authenticate", 'Bearer realm="Loggin required"')
    response.set_cookie("token", "")
    return response, 200


@auth.route("/retrievePublicKeys", methods=["POST"])
def retrieve_safe_public_keys(data=None):
    """Retrieve public keys from users to send encrypted data.
    Public keys are produced from users authentication perivate keys.
    Request could be made prior submitting any form or query with sensitive data
    """

    return make_response({"NOT implemented!"})


@auth.route("/addAuthenticationKeys", methods=["POST"])
@token_required
def add_authentication_keys(current_user: Subscriber, data=None):

    if data is None:
        data = json.loads(request.args.get("data", type=str))

    if "private_key" in data:
        status, auth_key = AuthenticationKey(
            private_key=data["private_key"]
        ).link_keys_to_subscriber(current_user)

        if status:
            public_key = jwt.encode(
                {
                    "private_key": auth_key.private_key,
                },
                current_app.secret_key,
            )
            return jsonify(
                {"message": "Profile keys added successfully", "public_key": public_key}
            )

        return jsonify({"Error": "Failed to create authentication keys"}), 500


def retrieve_subscriber(data: dict):
    return Subscriber().retrieve_subscriber(data["public_id"], data["user_name"])
