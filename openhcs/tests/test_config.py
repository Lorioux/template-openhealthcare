import pytest


@pytest.mark.run(order=1)
def test_config(app):
    assert app.testing == True
    assert app.config["DEBUG"] == True
