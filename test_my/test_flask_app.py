import pytest
import os

from helpers import *


@pytest.fixture
def testapp(cfg, session):
    from committee.committee import create_app
    os.environ["COMMITTEE_CONFIG"] = "test_my/fixtures/config/config_basic.cfg"
    app = create_app(cfg, session)
    app.config["TESTING"] = True
    return app.test_client()


def test_hello(testapp):
    assert "Hello" in testapp.get('/').get_data(as_text=True)
