from src.constants import RULE_FAIL


def sort_and_concat(violations):
    return ', '.join(sorted(violations))


def get_failed_rule_names(violations):
    return [x[0] for x in violations if x[2] == RULE_FAIL]


def is_rule_name(name):
    s = name.split(":")
    return len(s) == 2 and s[0] == "rule"


def get_rule_name(name):
    return name.split(":")[1]
