import os
import re

from src.constants import RULE_OK, RULE_FAIL


def apply_rule_message(rule, message, config_path):
    match_type, match_target = rule["match"].split(":", 1)

    status = RULE_OK
    if match_type == "plain":
        status = __plain(message, match_target)
    elif match_type == "regex":
        status = __regex(message, match_target)
    elif match_type == "wordlist":
        owd = os.getcwd()
        os.chdir(config_path)
        status = __word_list(message, match_target)
        os.chdir(owd)

    return status


def case_insensitive(func):
    def func_wrapper(a, b):
        return func(a.lower(), b.lower())

    return func_wrapper


@case_insensitive
def __plain(text, substr):
    return RULE_OK if text.find(substr) == -1 else RULE_FAIL


@case_insensitive
def __regex(text, pattern):
    return RULE_OK if re.match(pattern, text) is None else RULE_FAIL


def __word_list(text, path):
    with open(path, encoding="utf-8") as file:
        lines = [s.rstrip("\n") for s in file]
    return RULE_FAIL if RULE_FAIL in map(lambda x: __plain(text, x), lines) else RULE_OK
