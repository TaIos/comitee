import configparser

from src.constants import INVALID_INPUT, VALID_INPUT


def input_validate_section_github(section):
    if not isinstance(section, configparser.SectionProxy):
        return INVALID_INPUT

    if section.get("token") is None or len(section.get("token")) != 40:
        return INVALID_INPUT

    return VALID_INPUT
