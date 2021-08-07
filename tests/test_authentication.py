from __future__ import absolute_import
import json

import pytest


@pytest.mark.run(order=3)
def test_practitioner_signup(credencials, subscriber):
    rv = credencials.create(subscriber[0])

    assert "success" in str(rv.data)


@pytest.mark.run(order=4)
def test_practitioner_login(credencials, subscriber):
    user = {
        "role": subscriber[0]["role"],
        "userid": subscriber[0]["username"],
        "password": subscriber[0]["password"],
    }

    rv = credencials.authenticate(user)

    assert "success" in str(rv.data)


@pytest.mark.run(order=14)
def test_beneficiary_signup(credencials, subscriber):
    rv = credencials.create(subscriber[1])

    assert "success" in str(rv.data)


@pytest.mark.run(order=20)
def test_logout(credencials):
    rv = credencials.deauthenticate()

    assert "success" in str(rv.data)


@pytest.mark.run(order=21)
def test_access_without_login(client, url_caller):
    url = url_caller.get_url(
        "profiles.licences", publicid="mkkbjnkoiguvbjnibjvgubjnkhibj"
    )
    rv = client.get(url)

    assert "Invalid" in str(rv.data)
