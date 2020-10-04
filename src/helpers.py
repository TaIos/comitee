from src.constants import RULE_FAIL


def sort_and_concat(violations):
    return ', '.join(sorted(violations))


def get_failed_rule_names(violations):
    return [x[0] for x in violations if x[2] == RULE_FAIL]
