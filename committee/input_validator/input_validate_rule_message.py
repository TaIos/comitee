from committee.constants import INVALID_INPUT, VALID_INPUT
from committee.helpers import can_read_file, is_valid_regex


def input_validate_rule_message(section):
    if section.get("match") is None:
        return INVALID_INPUT

    match = section.get("match")
    s = match.split(":", 1)
    if len(s) != 2 or s[0] not in ["plain", "regex", "wordlist"]:
        return INVALID_INPUT

    if s[0] == "wordlist" and not can_read_file(s[1]):
        return INVALID_INPUT
    if s[0] == "regex" and not is_valid_regex(s[1]):
        return INVALID_INPUT

    return VALID_INPUT
