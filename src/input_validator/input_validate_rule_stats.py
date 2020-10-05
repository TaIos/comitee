import configparser

from src.constants import INVALID_INPUT, VALID_INPUT


def input_validate_rule_stats(section):
    if not isinstance(section, configparser.SectionProxy):
        return INVALID_INPUT

    if section.get("scope") is not None and section.get("scope") not in ["commit", "file"]:
        return INVALID_INPUT
    else:
        scope = "file"

    if section.get("stat ") is None:
        return INVALID_INPUT
    stat = section.get("stat")
    if scope == "commit" and stat not in ["total", "additions", "deletions"]:
        return INVALID_INPUT
    if scope == "file" and stat not in ["changes", "additions", "deletions"]:
        return INVALID_INPUT

    if section.get("min") is None and section.get("max") is None:
        return INVALID_INPUT

    return VALID_INPUT