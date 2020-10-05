import configparser

from src.constants import INVALID_INPUT, VALID_INPUT


def input_validate_section_github(section):
    if section.get("token") is None or len(section.get("token")) != 40:
        return INVALID_INPUT

    return VALID_INPUT
