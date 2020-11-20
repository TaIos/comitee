import pytest


@pytest.mark.parametrize("value", (0, -1, 5, 1000, "5", "-5"))
def test_is_int_with_valid_integer_values(value):
    assert is_int(value)


@pytest.mark.parametrize("value", (0.0, -1.0, 5.0, 1000.0, "5.0", "-5.0"))
def test_is_int_with_valid_float_values(value):
    assert not is_int(value)


@pytest.mark.parametrize("value", ("abc", "5a", None, ["a", "b"], list(), dict()))
def test_is_int_with_not_numeric_values(value):
    assert not is_int(value)
