from committee.util.constants import INVALID_INPUT, VALID_INPUT


def input_validate_rule_path(section):
    if section.get("match") is None:
        return INVALID_INPUT
    match = section.get("match")
    s = match.split(":", 1)
    if len(s) != 2 or s[0] not in ["plain", "regex", "wordlist"]:
        return INVALID_INPUT

    if section.get("status") is not None and section.get("status") not in ["modified", "added", "removed", "*"]:
        return INVALID_INPUT

    return VALID_INPUT
