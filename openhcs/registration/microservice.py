from __future__ import absolute_import

from datetime import datetime
import logging
import uuid

from flask import Blueprint, json, request, jsonify, current_app
from flask.helpers import flash, make_response, url_for
from flask.wrappers import Response
import jwt
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect

from flasgger import swag_from

from openhcs.registration.models import (
    Beneficiary,
    Doctor,
    Address,
    License,
    Speciality,
)

from openhcs.authentication import token_required
from openhcs import Subscriber

profiles = Blueprint(
    "profiles",
    __name__,
    static_url_path="/media/uploads/",
    static_folder="media/uploads",
    url_prefix="/v1",
)


@profiles.route("/practitioner/createProfile", methods=["POST", "PUT"])
@token_required
def create_practitioner_profile(current_user: Subscriber = None):

    if not current_user.role in ["doctor"]:
        error = "Only authenticated practitioners can create a practitioner's profile"
        flash(error, category="error")
        return jsonify({"Error": "Not allowed", "message": error}), 403

    profile: dict = request.get_json()
    role = "practitioner"

    # validate the request
    if validate_profile_entries(profile, role):
        for addr in profile.get("addresses"):
            validkeys, check = validate_address_entries(addr)
            if not check:
                return (
                    make_response(
                        {"Error": "Wrong address keys", "Valid keys": validkeys}
                    ),
                    403,
                )

        for specialiy in profile.get("specialities"):
            validkeys, check = validate_speciality_entries(specialiy)
            if not check:
                return (
                    make_response(
                        {"Error": "Wrong speciality keys", "Valid keys": validkeys}
                    ),
                    403,
                )

        for license in profile.get("licences"):
            validkeys, check = validate_license_entries(license)
            if not check:
                return (
                    make_response(
                        {"Error": "Wrong license keys", "Valid keys": validkeys}
                    ),
                    403,
                )

    return create_profile(data=profile)


@profiles.route("/beneficiary/createProfile", methods=["POST", "PUT"])
@token_required
def create_beneficiary_profile(current_user: Subscriber = None):

    # proceed only if current user role is beneficiary, or doctor
    if not current_user.role in ["beneficiary", "doctor"]:
        error = "Only practitioners or a beneficiary can create a profile"
        flash(error, category="error")
        return jsonify({"Error": error}), 405

    profile = request.get_json()

    if profile is None:
        return jsonify({"Error": "Couldn't proceed with invalid data"})

    # validate the request
    if validate_profile_entries(profile, "beneficiary"):
        for address in profile.get("addresses"):
            validkeys, check = validate_address_entries(address)
            if not check:
                return (
                    make_response(
                        {"Error": "Wrong address keys", "Valid keys": validkeys}
                    ),
                    403,
                )

    return create_profile(data=profile)


@token_required
def create_profile(current_user: Subscriber = None, data: dict = None):

    if data is None:
        data = request.get_json()

    role = data["role"]

    if role in ["doctor", "beneficiary", "caregiver"]:
        result = handle_subscriptions(role, data)

        if result is not None and not isinstance(result, Response):
            phone = data["phone"]
            print(result)
            return redirect(
                url_for(
                    "auth.add_authentication_keys",
                    data=json.dumps(
                        {
                            "private_key": result.nif,
                            "public_key": uuid.uuid3(
                                uuid.NAMESPACE_URL, f"{phone}-{role}"
                            ),
                        }
                    ),
                ),
                code=307,
            )

        if result:
            return result

    return make_response({"Error": "Couldn't proceed with provided data"}, 405)

    # return make_response({"Error":"Too many errors", "message":"Check your inputs"}), 403


@token_required
def add_practitioner(current_user: Subscriber = None, data: dict = None):

    # private_key = current_user.access_keys

    doctor = Doctor(
        fullname=data["fullname"],
        taxid=generate_password_hash(data["taxid"], method="SHA256"),
        phone=generate_password_hash(data["phone"], method="SHA256"),
        # photo=data["photo"],
        gender=data["gender"],
        mode=data["mode"],
        birthdate=data["birthdate"],
    )

    entity = doctor.check_uniqueness(data["phone"], data["taxid"])

    if entity:
        return entity

    if doctor.save() is None:
        return make_response({"Error": "Failed to add practitioner"}, 403)

    # handle specialities addition
    if not add_speciality(doctor, data.get("specialities")):
        doctor.delete()
        return make_response({"Error": "Failed to add specialities"}, 403)

    if not add_license(doctor, data.get("licences")):
        doctor.delete()
        return make_response({"Error": "Failed to add licences"}, 403)

    if not add_residence(doctor, data.get("addresses")):
        doctor.delete()
        return make_response({"Error": "Failed to add addresses"}, 403)

    return doctor


@token_required
def add_beneficiary(current_user: Subscriber = None, data=dict()):

    entity = Beneficiary(
        fullname=data["fullname"],
        birthdate=data["birthdate"],
        phone=generate_password_hash(data["phone"], method="SHA256"),
        gender=data["gender"],
        taxid=generate_password_hash(data["taxid"], method="SHA256"),
        # address=data["address"],
    ).save()
    beneficiary = entity.save()

    if beneficiary is None:
        return make_response({"Error": "Failed to add beneficiary"}, 403)

    if not add_residence(beneficiary, data.get("addresses")):
        beneficiary.delete()
        return make_response({"Error": "Failed to add addresses"}, 403)

    if current_user.role in ["doctor", "caregiver"]:
        # call associate beneficiary to current user:
        result = associate_beneficiary_to_carer(beneficiary)
        if not result:

            return make_response({"Error": "Failed to associate beneficiary to care."})

    return beneficiary


@profiles.route("/", methods=["GET"])
def subscribers():
    return jsonify({"response": "Not Implemented"})


@profiles.route("/practitioners")
@profiles.route("/practitioners/findByCriteria", methods=["GET"])
def find_practtioners_by_criteria(criteria=None):

    request_time = datetime.now()
    try:

        data = request.args.to_dict()
        if criteria is None:
            criteria = request.args.get("criteria")

        # validate criteria
        if criteria not in [
            "speciality-location",
            "speciality-only",
            "speciality-location-mode",
            "mode-only",
            "location-only",
            "none",
        ]:
            criteria = "none"
            flash(
                "Use speciality or location to search for practitioners",
                category="info",
            )
        # find by speciality and location together
        keys = data.keys()

        if criteria == "speciality-location":

            if "speciality" not in keys or "location" not in keys:

                criteria = "none"
            else:
                if data["speciality"].__eq__("") or data["location"].__eq__(""):
                    criteria = "none"
                else:
                    doctors = Doctor().find_all(
                        criteria=criteria,
                        title=data["speciality"],
                        city=data["location"],
                    )

        if criteria == "speciality-only":
            if "speciality" not in keys:
                criteria = "none"
            else:
                if data["speciality"].__eq__(""):
                    criteria = "none"
                else:
                    doctors = Doctor().find_all(
                        criteria=criteria, title=data["speciality"]
                    )

        if criteria == "speciality-location-mode":
            if "speciality" not in keys or "location" not in keys or "mode" not in keys:
                criteria = "none"
            else:
                if (
                    data["location"].__eq__("")
                    or data["speciality"].__eq__("")
                    or data["mode"].__eq__("")
                ):
                    criteria = "none"
                else:
                    doctors = Doctor().find_all(
                        criteria=criteria,
                        speciality=data["speciality"],
                        city=data["location"],
                        mode=data["mode"],
                    )

        if criteria == "mode-only":
            if "mode" not in keys:
                criteria = "none"
            else:
                if data["mode"].__eq__(""):
                    criteria = "none"
                else:
                    doctors = Doctor().find_all(criteria=criteria, mode=data["mode"])

        if criteria == "location-only":
            if "location" not in keys:
                criteria = "none"
            else:
                if data["location"].__eq__(""):
                    criteria = "none"
                else:
                    doctors = Doctor().find_all(
                        criteria=criteria, city=data["location"]
                    )

        if criteria == "none":
            doctors = Doctor().find_all(criteria=criteria)

    except RuntimeError as error:
        logging.exception(error, stack_info=True)
        return None

    if doctors is None:
        return jsonify({"Error": "NOT Found"}), 403

    template = {
        "metadata": {
            "requestTime": request_time,
            "domain": "practitioners",
            "responseTime": datetime.now(),
            "speciality": "Nutritionist",
            "location": "all",
            "responses": doctors.count(),
        },
        "summary": [],
    }
    # print(doctors)
    for doctor in doctors:
        addresses = list(
            dict(
                street_name=addr.street_name,
                door_number=addr.door_num,
                zipcode=addr.zipcode,
                state=addr.state,
                city=addr.city,
                country=addr.country.name,
            )
            for addr in doctor.addresses
            if addr is not None or addr.city == "Lisbon"
        )
        # print(address)
        specialities = list(s.title for s in doctor.specialities[0:])
        # print(specialities)
        licences = list(l.code for l in doctor.licences[0:])
        # print(licenses)
        public_id = jwt.encode(
            {"private_key": doctor.nif}, current_app.secret_key, algorithm="HS256"
        )
        template["summary"].append(
            {
                "fullname": doctor.full_name,
                "publicid": public_id,
                "speciality": specialities,
                "licences": licences,
                "addresses": addresses,
                "mode": doctor.mode,
            }
        )
    template["metadata"]["responseTime"] = datetime.now()

    return jsonify(template)


@profiles.route(
    "/beneficiaries?criteria=<string:criteria>&cityname=<string:city_name>",
    methods=["GET"],
)
@token_required
def find_beneficiaries(
    current_user: Subscriber = None, criteria="city", city_name="Lisbon"
):
    request_time = datetime.now()
    beneficiaries = Beneficiary().find_all(criterion=criteria, name=city_name)
    # if beneficiaries is None or beneficiaries == []:
    #     print(beneficiaries)
    #     return None
    template = {
        "metadata": {
            "requestTime": request_time,
            "responseTime": datetime.now(),
            "domain": "beneficiary",
            "location": "Lisbon",
            "responses": beneficiaries.count(),
        },
        "summary": [],
    }

    for beneficiary in beneficiaries.all():

        addresses = list(
            dict(
                road=address.road,
                flat=address.flat,
                zipcode=address.zipcode,
                city=address.city,
                country=address.country.name,
            )
            for address in beneficiary.addresses
            if address is not None and address.city == "Lisbon"
        )
        template["summary"].append(
            dict(
                id=beneficiary.id,
                name=beneficiary.name,
                age=beneficiary.age,
                gender=beneficiary.gender,
                photo=beneficiary.photo,
                phone=beneficiary.phone,
                nif=beneficiary.nif,
                addresses=addresses,
            )
        )
    template["metadata"]["responseTime"] = datetime.now()
    return jsonify(template)


@profiles.route("/updateMemberAddress")
@token_required
def add_member_address(current_user: Subscriber = None, data=dict()):
    address_id = Address(
        road=data["road"],
        flat=data["flat"],
        zipcode=data["zipcode"],
        state=data["state"],
        city=data["city"],
        country=data["country"],
    ).save()
    return address_id


@profiles.route("/licences/<string:publicid>")
@profiles.route("practitioner/<string:publicid>/licences")
@token_required
def licences(current_user: Subscriber = None, publicid=None):

    request_time = datetime.now()

    doctor_nif = jwt.decode(publicid, current_app.secret_key, algorithms="HS256").get(
        "private_key"
    )

    doctor = Doctor.query.filter(Doctor.nif.ilike(doctor_nif)).one_or_none()

    if doctor is None:
        return jsonify({"Error": "NOT found."}), 403

    if doctor.licences is None or doctor.licences == []:
        return jsonify({"response": "Doctor has NO Licence"})

    template = {
        "metadata": {
            "requestTime": request_time,
            "domain": "practitioners",
            "responseTime": datetime.now(),
            "requestTyle": "licences",
            "responses": len(doctor.licences),
        },
        "summary": [],
    }

    for license in doctor.licences:
        template["summary"].append(
            dict(
                code=license.code,
                issue_date=license.issue_date,
                end_date=license.end_date,
                issuingorg=license.issuingorg,
                issuingcountry=license.issuingcountry,
                certificate=license.certificate,
            )
        )

    return jsonify(template)


@profiles.route("/specialities/fetchAll", methods=["GET"])
@profiles.route("/specialities/searchPerTitle", methods=["GET"])
def specialities(title=None):
    request_time = datetime.now()
    specs = None

    if title is None:
        title = request.args.get("title")

    if title is not None:
        specs = [Speciality().getby_title(title)]
        # at least we retrieving one
        count = len(specs)
    else:
        count, specs = Speciality().get_all()

    if specs is None:
        return jsonify({"message": "NO speciality found"})

    print(specs)
    template = {
        "metadata": {
            "requestTime": request_time,
            "domain": "practitioners",
            "responseTime": datetime.now(),
            "requestType": "specialities",
            "responses": count,
        },
        "summary": [],
    }

    for speciality in specs:
        template["summary"].append(
            dict(title=speciality.title, description=speciality.description)
        )

    response_time = datetime.now()
    template["metadata"]["responseTime"] = response_time
    return jsonify(template)


@profiles.route("/updateSpeciality", methods=["POST", "PUT"])
@token_required
def handle_speciality_update(current_user: Subscriber = None, content: dict = None):
    """TODO"""
    # validate content
    if content and "title" in content and "description" in content:
        pass


def handle_subscriptions(role, data):
    if role == "doctor":
        return add_practitioner(data=data)
    if role == "beneficiary":
        return add_beneficiary(data=data)
    return None


def add_speciality(practitioner: Doctor, specialities: list):
    for spec in specialities:
        speciality = Speciality(
            title=spec.get("title"), description=spec.get("description")
        ).save_with_practitioner(practitioner)
        if speciality is None:
            return False
    return True


def add_license(practitioner: Doctor, licences: list):
    for lic in licences:
        license = License(
            code=lic.get("code"),
            enddate=lic.get("enddate"),
            issuedate=lic.get("issuedate"),
            issuingcountry=lic.get("issuingcountry"),
            issuingorg=lic.get("issuingorg"),
            certificate=lic.get("certificate"),
        ).save_with_licensee(practitioner)
        if license is None:
            return False
    return True


def add_residence(resindent: any, addresses: list):
    for addr in addresses:
        address = Address(
            city=addr.get("city"),
            country=addr.get("country"),
            doornumber=addr.get("doornumber"),
            zipcode=addr.get("zipcode"),
            state=addr.get("state"),
            streetname=addr.get("streetname"),
        ).save_with_resident(resindent)
        if address is None:
            return False
    return True


@token_required
def associate_beneficiary_to_carer(
    current_user: Subscriber, beneficiary: Beneficiary = None
):
    carer: Doctor = current_user.retrieve_profile_owner()
    if carer is None:

        return None

    return carer.associate_beneficiary(beneficiary)


@profiles.route("/disassociateBeneficiary", methods=["POST"])
@token_required
def disassociate_beneficiary(current_user: Subscriber, beneficiary: dict = None):
    carer: Doctor = current_user.retrieve_profile_owner()

    if beneficiary is None:
        beneficiary = request.get_json()

    keys, valid = validate_beneficiary_entries(beneficiary)

    if not valid:
        return make_response(
            {
                "Error": "Invalid beneficiary data entries",
                "message": f"Valid entries are: {keys}",
            },
            403,
        )

    if carer is None:
        return make_response({"Error": "Invalid practitioner"}, 403)

    if carer.disassociate_beneficiary(beneficiary):
        return make_response(
            {
                "message": "Beneficiary disassociated from practitioners profile successfully"
            }
        )

    return make_response({"Error": "Beneficiary NOT disassociated."}, 403)


def validate_address_entries(address: dict):
    keys = {"city", "country", "doornumber", "zipcode", "state", "streetname"}
    # print(list(address.keys()))
    return list(keys), set(address.keys()).difference(keys) == set()


def validate_speciality_entries(speciality: dict):
    keys = {"description", "title"}

    return keys, set(speciality.keys()).difference(keys) == set()


def validate_license_entries(license: dict):
    keys = {
        "code",
        "enddate",
        "issuedate",
        "issuingcountry",
        "issuingorg",
        "certificate",
    }
    return list(keys), set(license.keys()).difference(keys) == set()


# def validate_mode_entry(mode)


def validate_profile_entries(profile_entry: dict, role: str):
    if role == "practitioner":
        keys = {
            "addresses",
            "birthdate",
            "licences",
            "fullname",
            "phone",
            "role",
            "specialities",
            "taxid",
            "mode",
            "gender",
        }
    keys = {"addresses", "birthdate", "fullname", "phone", "role", "taxid", "gender"}
    return list(keys), set(profile_entry.keys()).difference(keys) == set()


def validate_beneficiary_entries(beneficiary: dict):
    keys = {
        "role",
        "fullname",
        "birthdate",
        "gender",
        "photo",
        "phone",
        "taxid",
        "addresses",
    }
    return keys, set(beneficiary.keys()).difference(keys) == set()
