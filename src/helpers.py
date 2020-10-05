from src.constants import RULE_FAIL
from os import access, R_OK
from os.path import isfile
import re


def sort_and_concat(obj):
    return ', '.join(sorted(obj))


def get_failed_rule_names(violations):
    return [x["name"] for x in violations if x["status"] == RULE_FAIL]


def is_rule_name(name):
    s = name.split(":")
    return len(s) == 2 and s[0] == "rule"


def get_rule_name(name):
    return name.split(":")[1]


def is_int(value):
    if isinstance(value, int):
        return True

    if isinstance(value, str):
        try:
            int(value)
            return True
        except ValueError:
            return False
    return False


def can_read_file(file):
    return isfile(file) and access(file, R_OK)


def is_valid_regex(regex):
    try:
        re.compile(regex)
        return True
    except re.error:
        return False
