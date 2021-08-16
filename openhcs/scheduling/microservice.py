from __future__ import absolute_import


from logging import Logger
from flask import Blueprint, json, jsonify, request, abort
from flask.helpers import url_for
from sqlalchemy.sql.elements import and_
from werkzeug.utils import redirect

from openhcs.scheduling.models import Schedule
from openhcs.authentication import token_required

LOG = Logger("SCHEDULING", 50)
schedules = Blueprint("schedules", __name__, url_prefix="/v1/schedules")


@schedules.route("/createSchedule", methods=["POST"])
@token_required
def create_schedule(current_user):
    if current_user.role == "doctor":

        if len(current_user.access_keys) > 0:
            private_key = current_user.access_keys[0].private_key
            data = json.loads(request.data)
            count = data.__len__()
            schedules = [
                Schedule(
                    year=schedule["year"],
                    weeks=schedule["weeks"],
                    month=schedule["month"],
                    doctor_nif=private_key,
                ).save()
                for schedule in data
                if schedule is not None
            ]

            if not None in schedules and len(schedules) == count:
                return jsonify({"message": "Schedule created successfully."})
        return (
            jsonify(
                {
                    "Error": "Create a practitioner profile to be able of adding schedules"
                }
            ),
            401,
        )
    abort(403, jsonify({"Error": "Not authorized to add schedules"}))


@schedules.route("/updateSchedule", methods=["PUT"])
@token_required
def update_schedule(current_user):
    data = json.loads(request.data)
    old = None
    for schedule in data:
        private_key = current_user.access_keys[0].private_key
        if schedule is not None:
            old = Schedule.query.filter(
                and_(
                    Schedule.month.like(schedule["month"]),
                    Schedule.year == schedule["year"],
                ),
                Schedule.doctor_nif == private_key,
            ).one_or_none()
            if old is None:
                redirect(url_for(".create", schedule=schedule))
            old.weeks.update(schedule["weeks"])

    return jsonify(old.weeks)


# @schedules.errorhandler(401)
# def create_error(code):
#     return "Not Allowed"


@schedules.errorhandler(403)
def wrong_schedule_data(code):
    return jsonify({"Error": "Provided data is not supported"})


@schedules.route("/all")
def get_all():
    return jsonify({""})


@schedules.route("/<date>", methods=["GET"])
def getby_date():
    return jsonify({""})


@schedules.route("/weeks/<number>/<year>")
def getby_week():
    return jsonify({""})
