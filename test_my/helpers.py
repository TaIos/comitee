import pytest
import configparser
import os
import contextlib

from betamax import Betamax
from committee.committee import __create_auth_github_session

with Betamax.configure() as config:
    config.cassette_library_dir = "test_my/fixtures/cassette_library"

    if "GH_TOKEN" in os.environ:
        # If the tests are invoked with an GH_TOKEN environ variable
        TOKEN = os.environ["GH_TOKEN"]
        # Always re-record the cassetes
        # https://betamax.readthedocs.io/en/latest/record_modes.html
        config.default_cassette_options["record_mode"] = "all"
    else:
        TOKEN = "<40 characters long false token xxxxxxx>"
        # Do not attempt to record sessions with bad fake token
        config.default_cassette_options["record_mode"] = "none"

    # Hide the token in the cassettes
    config.define_cassette_placeholder("<TOKEN>", TOKEN)


@pytest.fixture
def cfg():
    path = "test_my/fixtures/config/config_basic.cfg"
    cfg = configparser.ConfigParser()
    cfg.read(path)
    cfg.set("github", "token", TOKEN)
    cfg.config_path = os.path.dirname(os.path.abspath(path))
    return cfg


@pytest.fixture
def session(cfg, betamax_parametrized_session):
    return __create_auth_github_session(cfg, betamax_parametrized_session)


@pytest.fixture
def testapp(cfg, session):
    from committee.committee import create_app
    os.environ["COMMITTEE_CONFIG"] = "test_my/fixtures/config/config_basic.cfg"
    app = create_app(cfg, session)
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def testapp_with_config(cfg, session):
    """
    Return FUNCTION that returns testing app, but with additional config set.
    It is useful when parametrizing application secret.
    """
    from committee.committee import create_app
    os.environ["COMMITTEE_CONFIG"] = "test_my/fixtures/config/config_basic.cfg"
    app = create_app(cfg, session)
    app.config["TESTING"] = True

    def testapp_with_config_wrapper(**kwargs):
        for key, val in kwargs.items():
            app.config[key] = val
        return app.test_client()

    return testapp_with_config_wrapper


@contextlib.contextmanager
def env(**kwargs):
    original = {key: os.getenv(key) for key in kwargs}
    os.environ.update({key: str(value) for key, value in kwargs.items()})
    try:
        yield
    finally:
        for key, value in original.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value
