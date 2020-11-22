import pytest

from committee.helpers import is_int


@pytest.mark.parametrize("value", (0, -1, 5, 1000, "5", "-5"))
def test_is_int_with_valid_integer_values(value):
    """Test if integer is classified as integer"""
    assert is_int(value)


@pytest.mark.parametrize("value", (0.0, -1.0, 5.0, 1000.0, "5.0", "-5.0"))
def test_is_int_with_valid_float_values(value):
    """Test if float is not classified as integer"""
    assert not is_int(value)


@pytest.mark.parametrize("value", ("abc", "5a", None, ["a", "b"], list(), dict()))
def test_is_int_with_not_numeric_values(value):
    """Test if not numeric value is not classified as integer"""
    assert not is_int(value)
