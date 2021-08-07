import json

import pytest


@pytest.mark.run(order=17)
def test_appoitment_adding(client, appointment, url_caller, subscriber, credencials):
    # rv = credencials.authenticate(subscriber[])
    url = url_caller.get_url(
        "booking.make_appointment", appointment=json.dumps(appointment)
    )

    rv = client.post(
        url,
        data=json.dumps(appointment),
        content_type="application/json",
        follow_redirects=True,
    )

    assert "success" in str(rv.data)
