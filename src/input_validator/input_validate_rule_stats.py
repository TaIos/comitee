import configparser

from src.constants import INVALID_INPUT, VALID_INPUT
from src.helpers import is_int


def input_validate_rule_stats(section):
    scope = section.get("scope")
    if scope is None:
        scope = "commit"
    elif scope not in ["commit", "file"]:
        return INVALID_INPUT

    if section.get("stat") is None:
        return INVALID_INPUT
    if scope == "commit" and section.get("stat") not in ["total", "additions", "deletions"]:
        return INVALID_INPUT
    if scope == "file" and section.get("stat") not in ["changes", "additions", "deletions"]:
        return INVALID_INPUT
    if section.get("min") is None and section.get("max") is None:
        return INVALID_INPUT
    if not is_int(section.get("min")) or not is_int(section.get("max")):
        return INVALID_INPUT

    return VALID_INPUT
