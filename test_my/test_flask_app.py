import pytest

from helpers import *
from committee.committee import __configure_flask_app


@pytest.mark.parametrize("path", ["/invalid/path/absolute/config.cfg", "invalid/path/relative/config.cfg"])
def test_configure_flask_app_with_invalid_configuration_path(testapp, path, capsys):
    with env(COMMITTEE_CONFIG=path):
        with pytest.raises(SystemExit):
            __configure_flask_app(testapp)
        out, err = capsys.readouterr()
        assert "Invalid config file path." in out

