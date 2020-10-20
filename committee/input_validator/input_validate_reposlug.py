from committee.constants import INVALID_INPUT, VALID_INPUT


def input_validate_reposlug(reposlug):
    s = reposlug.split("/")
    if reposlug.count("/") != 1 or len(s) != 2 or len(s[0]) == 0 or len(s[1]) == 0:
        return INVALID_INPUT

    return VALID_INPUT
