import configparser

from src.constants import INVALID_INPUT, VALID_INPUT


def input_validate_rule_message(section):
    if not isinstance(section, configparser.SectionProxy):
        return INVALID_INPUT

    if section.get("match") is None:
        return INVALID_INPUT

    match = section.get("match")
    s = match.split(":")
    if len(s) != 2 or s[0] not in ["plain", "regex", "wordlist"]:
        return INVALID_INPUT

    return VALID_INPUT
