import pytest
import configparser
import os

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
