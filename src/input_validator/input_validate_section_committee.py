import configparser

from src.constants import INVALID_INPUT, VALID_INPUT


def input_validate_section_committee(section):
    if section.get("context") is None:
        return INVALID_INPUT

    return VALID_INPUT
