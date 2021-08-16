from __future__ import absolute_import
from functools import wraps

import jwt
from flask import Blueprint, request, jsonify, json
from flask.globals import current_app, g, session
from flask.helpers import make_response, url_for
from werkzeug.utils import redirect


from openhcs import Beneficiary, Appointment, Subscriber
from openhcs.authentication.microservice import retrieve_subscriber

bookings = Blueprint("booking", __name__, url_prefix="/v1/booking")


@bookings.route("/")
def booking():
    appointment = Appointment.query.all()
    print(appointment)

    return jsonify(
        {
            "periodFrom": "01/20/2021",
            "periodTo": "30/06/2021",
            "specialities": {
                "nutrition": {
                    "02/05/2021": {
                        "appointments": {
                            "slot": {
                                "12:00": [
                                    {
                                        "doctor": "Dr. John Doe",
                                        "doctorId": "xascascascac",
                                        "beneficiary": "Jose Melo",
                                        "beneficiaryId": "cmnsnadsdap",
                                    }
                                ]
                            }
                        }
                    }
                },
                "pediatric": {},
            },
        }
    )


def require_registration(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        # chechen if token was provided
        token = request.cookies.get("token")

        try:

            # appointment = session.get('appointment_info')

            if not token:
                # save user session into user
                data = json.loads(request.args.to_dict().get("data"))
                session["appointment_info"] = data

                raise PermissionError

            payload = jwt.decode(token, current_app.secret_key, algorithms="HS256")
            beneficiary = retrieve_subscriber(data=payload)

            return f(beneficiary, *args, **kwargs)

        except KeyError as error:
            data = json.loads(request.data)
            session["appointment_info"] = data
            return make_response({"Error": "Subscription or login required 1"}, 401)
        except PermissionError:

            return make_response({"Error": "Subscription or login required 2"}, 401)

    return decorator


@bookings.route("/appointments/makeAppointment", methods=["POST"])
@require_registration
def make_appointment(beneficiary: Subscriber = None, appointment: dict = None):

    if beneficiary.role not in ["beneficiary", "caregiver"]:
        return make_response(
            {
                "Error": "Not authorized",
                "message": "Only beneficiaries or care givers are allowed to make appointments.",
            },
            403,
        )
    data = appointment
    if data is None or data is {}:
        data = request.get_json()
    # check if beneficiary is already registered

    keys, valid = validate_appointment_entries(data)
    if not valid:

        return make_response(
            {
                "Error": "Provided invalid data",
                "message": f"Supported entries are: {keys}",
            },
            403,
        )

    appointmt = Appointment(
        date=data["date"],
        time=data["time"],
        doctor_name=data["doctor_name"],
        doctor_speciality=data["doctor_speciality"],
        doctor_id=data["doctor_id"],
        beneficiary_phone=data["beneficiary_phone"],
        beneficiary_name=data["beneficiary_name"],
        beneficiary_id=data["beneficiary_id"],
        remarks=data["remarks"],
    )

    if appointmt.save():
        return make_response({"message": "Appointment made successfully"})
    return make_response({"Error": "Failed to fulfill the requested operation"})


def validate_appointment_entries(appointmt: dict):
    keys = {
        "date",
        "time",
        "doctor_name",
        "doctor_speciality",
        "doctor_id",
        "beneficiary_phone",
        "beneficiary_name",
        "beneficiary_id",
        "remarks",
    }

    return keys, set(appointmt.keys()).difference(keys) == set()
