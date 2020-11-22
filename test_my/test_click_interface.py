import pytest
from click.testing import CliRunner

from committee.committee import comitee


@pytest.fixture
def runner():
    return CliRunner()


@pytest.mark.parametrize("file", ["non/existing/file.cfg"])
def test_non_existing_config_file(runner, file):
    result = runner.invoke(comitee, ["--config", file])
    assert result.exit_code == 2  # Click UsageError
    assert f"Could not open file: {file}: No such file or directory" in result.output


@pytest.mark.parametrize("arg", ["--invalid-argument", "-i"])
def test_invalid_argument(runner, arg):
    """Test correct response to undefined command line parameter"""
    result = runner.invoke(comitee, [arg])
    assert result.exit_code == 2  # Click UsageError
    assert f"Error: no such option: {arg}" in result.output
