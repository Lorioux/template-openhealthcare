import pytest

from openhcs.app import make_app


@pytest.mark.run(order=21)
def test_makeapp():
    app = make_app()
    assert "development" == app.config["ENV"]


def test_index(client, url_caller):
    url = url_caller.get_url("index")

    rv = client.get(url)

    assert "apiversion" in str(rv.data)
