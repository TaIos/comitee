import configparser
import os
import requests
import pytest

from betamax import Betamax

from committee.committee import __create_auth_github_session, __fetch_all_commits

with Betamax.configure() as config:
    config.cassette_library_dir = "test_my/fixtures/cassette_library"

    if "GH_TOKEN" in os.environ:
        # If the tests are invoked with an GH_TOKEN environ variable
        TOKEN = os.environ["GH_TOKEN"]
        # Always re-record the cassetes
        # https://betamax.readthedocs.io/en/latest/record_modes.html
        config.default_cassette_options["record_mode"] = "all"
    else:
        TOKEN = "false_token"
        # Do not attempt to record sessions with bad fake token
        config.default_cassette_options["record_mode"] = "none"

    # Hide the token in the cassettes
    config.define_cassette_placeholder("<TOKEN>", TOKEN)


@pytest.fixture
def cfg():
    cfg = configparser.ConfigParser()
    cfg.read("test_my/fixtures/config/config_basic.cfg")
    cfg.set("github", "token", TOKEN)
    return cfg


@pytest.fixture
def session(cfg, betamax_parametrized_session):
    return __create_auth_github_session(cfg, betamax_parametrized_session)


@pytest.mark.parametrize(["reposlug", "author", "path", "ref"], [("LQpKH20/committee-basic", None, None, None)])
def test_fetch_all_commits(session, reposlug, author, path, ref):
    r = __fetch_all_commits(session, reposlug, author, path, ref)
    assert r
