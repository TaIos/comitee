import pytest

from helpers import *
from committee.committee import __configure_flask_app
import hashlib
import hmac


@pytest.mark.parametrize("path", ["/invalid/path/absolute/config.cfg", "invalid/path/relative/config.cfg"])
def test_configure_flask_app_with_invalid_configuration_path(testapp, path, capsys):
    """Test creating application with incorrect configuration file"""
    with env(COMMITTEE_CONFIG=path):
        with pytest.raises(SystemExit):
            __configure_flask_app(testapp)
        out, err = capsys.readouterr()
        assert "Invalid config file path." in out


def test_empty_post_post(testapp):
    """Test correct error code and returned json for empty POST"""
    r = testapp.post("/", data=dict(), headers={})
    assert r.status_code == 400
    js = r.json
    assert "success" in js
    assert js["success"] == False


def test_empty_data_post(testapp):
    """Test correct error code and returned json for empty data part with correct headers"""
    r = testapp.post("/", data=dict(), headers={"X-Github-Event": None})
    assert r.status_code == 200
    js = r.json
    assert js
    assert "success" in js
    assert js["success"] == False


@pytest.mark.parametrize(["data", "secret", "github_event"], [("abc", "42", "invalid")])
def test_valid_signature_ping(testapp_with_config, secret, data, github_event):
    """Test if the app correctly responses to ping with valid signature"""
    payload = {
        "headers": {
            "X-Hub-Signature": "sha1=" + hmac.new(secret.encode(), data.encode(), hashlib.sha1).hexdigest(),
            "X-Github-Event": "ping"
        },
        "data": data
    }

    testapp = testapp_with_config(secret=secret)
    r = testapp.post("/", **payload)

    assert r.status_code == 200
    js = r.json
    assert js
    assert len(js) == 1
    assert "success" in js
    assert js["success"] == True


def test_invalid_signature_ping(testapp):
    """Test if the app correctly responses to ping with valid signature"""
    payload = {
        "headers": {
            "X-Hub-Signature": "sha1=invalid",
            "X-Github-Event": "ping"
        },
        "data": "abcdef"
    }
    r = testapp.post("/", **payload)

    assert r.status_code == 400
    js = r.json
    assert js
    assert len(js) == 2
    assert "success" in js
    assert js["success"] == False
    assert "error" in js
    assert js["error"] == "invalid signature"


@pytest.mark.parametrize(["data", "secret", "github_event"], [("abc", "42", "invalid_github_event")])
def test_invalid_github_event(testapp_with_config, data, secret, github_event):
    """Test if the app responses to invalid github event, but with everything else set correctly"""
    payload = {
        "headers": {
            "X-Hub-Signature": "sha1=" + hmac.new(secret.encode(), data.encode(), hashlib.sha1).hexdigest(),
            "X-Github-Event": github_event
        },
        "data": data
    }

    testapp = testapp_with_config(secret=secret)
    r = testapp.post("/", **payload)

    assert r.status_code == 400
    js = r.json
    assert js
    assert len(js) == 2
    assert "success" in js
    assert js["success"] == False
    assert "error" in js
    assert js["error"] == "invalid github event"
