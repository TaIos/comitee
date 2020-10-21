from committee.constants import INVALID_INPUT
from committee.input_validator.input_validate_rule_message import input_validate_rule_message
from committee.input_validator.input_validate_rule_path import input_validate_rule_path
from committee.input_validator.input_validate_rule_stats import input_validate_rule_stats


def input_validate_rule(section):
    if section.get("type") is None:
        return INVALID_INPUT

    if section.get("type") == "message":
        return input_validate_rule_message(section)
    elif section.get("type") == "path":
        return input_validate_rule_path(section)
    elif section.get("type") == "stats":
        return input_validate_rule_stats(section)

    return INVALID_INPUT
