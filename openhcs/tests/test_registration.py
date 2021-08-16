from __future__ import absolute_import

from flask import json
from flask.helpers import url_for
import pytest

# from registration.models import Doctor, Speciality
# from openhcs.tests.conftest import delete_tables
public_id = None


@pytest.mark.run(order=5)
def test_add_practitioner(client, doctor):
    url = url_for("profiles.create_practitioner_profile")
    rv = client.post(
        url,
        data=json.dumps(doctor),
        content_type="application/json",
        follow_redirects=True,
    )

    assert "successful" in str(rv.data)


@pytest.mark.run(order=6)
def test_find_practitioners(client, app, processor):

    criteria = [
        "speciality-only",
        "location-only" "speciality-location",
        "speciality-location-mode",
        "mode-only",
        "none",
    ]

    # for c in criteria:
    url = url_for("profiles.find_practtioners_by_criteria", criteria="speciality-only")
    # if c == "speciality-only":
    rv = client.get(
        url,  # f"/members/doctors?",
        data=json.dumps({"speciality": "Nutritionist"}),
        content_type="application/json",
        follow_redirects=True,
    )
    # print(rv.data)
    data = rv.get_json()
    processor.set_publicid(data.get("summary")[0].get("publicid"))
    assert "speciality" in str(rv.data)

    # if "speciality-location".__eq__(c):^
    url = url_for(
        "profiles.find_practtioners_by_criteria", criteria="speciality-location"
    )
    rv = client.get(
        url,  # f"/members/doctors?criteria={c}",
        data=json.dumps({"speciality": "Nutritionist", "location": "Lisbon"}),
        content_type="application/json",
        follow_redirects=True,
    )
    assert "speciality" in str(rv.data)

    # if "mode-only".__eq__(c):
    url = url_for("profiles.find_practtioners_by_criteria", criteria="mode-only")
    rv = client.get(
        url,  # f"/members/doctors?criteria={c}",
        data=json.dumps({"mode": "video"}),
        content_type="application/json",
        follow_redirects=True,
    )

    assert "speciality" in str(rv.data)

    # if "location-only".__eq__(c):
    url = url_for("profiles.find_practtioners_by_criteria", criteria="location-only")
    rv = client.get(
        url,  # f"/members/doctors?criteria={c}",
        data=json.dumps({"mode": "video"}),
        content_type="application/json",
        follow_redirects=True,
    )

    assert "speciality" in str(rv.data)

    # if "speciality-location-mode".__eq__(c):
    url = url_for(
        "profiles.find_practtioners_by_criteria", criteria="speciality-location-mode"
    )
    rv = client.get(
        url,  # f"/members/doctors?criteria={c}",
        data=json.dumps(
            {
                "speciality": "Nutritionist",
                "location": "Lisbon",
                "mode": "video",
            }
        ),
        content_type="application/json",
        follow_redirects=True,
    )

    assert "speciality" in str(rv.data)

    # if "none".__eq__(c):
    url = url_for("profiles.find_practtioners_by_criteria", criteria="none")
    rv = client.get(url, follow_redirects=True)  # f"/members/doctors?criteria={c}",

    assert "speciality" in str(rv.data)


@pytest.mark.run(order=7)
def test_list_licences_by_practitioner(client, license, processor):

    url = url_for("profiles.licences", publicid=processor.get_publicid())

    print(url)

    rv = client.get(url, follow_redirects=True)

    assert license[0]["code"] in str(rv.data)


@pytest.mark.run(order=8)
def test_list_specialities(client):
    url = url_for("profiles.specialities")
    rv = client.get(url, follow_redirects=True)  # "/members/allSpecialities",
    assert "title" in str(rv.data)

    url = url_for("profiles.specialities", title="Nutritionist")
    rv = client.get(
        url, follow_redirects=True  # "/members/findSpeciality?title=Nutritionist",
    )
    assert "title" in str(rv.data)


@pytest.mark.run(order=12)
def test_add_beneficiary_by_practitioner(client, beneficiary):
    url = url_for("profiles.create_beneficiary_profile")
    rv = client.post(
        url,
        data=json.dumps(beneficiary),
        content_type="application/json",
        follow_redirects=True,
    )

    assert "success" in str(rv.data)


@pytest.mark.run(order=13)
def test_remove_beneficiary_by_practitioner(
    client, beneficiary, url_caller, credencials
):

    url = url_caller.get_url("profiles.disassociate_beneficiary")
    rv = client.post(
        url,
        data=json.dumps(beneficiary),
        content_type="application/json",
        follow_redirects=True,
    )
    credencials.deauthenticate()
    assert "success" in str(rv.data)


@pytest.mark.run(order=16)
def test_add_beneficiary(client, beneficiary, credencials, subscriber, processor):
    user = {
        "role": subscriber[1]["role"],
        "userid": subscriber[1]["username"],
        "password": subscriber[1]["password"],
    }
    rv = credencials.authenticate(user)
    data = rv.get_json()
    processor.set_publicid(data["token"])

    assert "success" in str(rv.data)

    url = url_for("profiles.create_beneficiary_profile")
    rv = client.post(
        url,
        data=json.dumps(beneficiary),
        content_type="application/json",
        follow_redirects=True,
    )

    assert "success" in str(rv.data)
