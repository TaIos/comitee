import re

from src.helpers import OK, BAD


def apply_rule_message(rule, name, session, commit):
    match_type, match_target = rule["match"].split(":")
    commit_msg = commit["commit"]["message"]

    status = OK
    if match_type == "plain":
        status = __plain(commit_msg, match_target)
    elif match_type == "regex":
        status = __regex(commit_msg, match_target)
    elif match_type == "wordlist":
        status = __word_list(commit_msg, match_target)

    return status


def case_insensitive(func):
    def func_wrapper(a, b):
        return func(a.lower(), b.lower())

    return func_wrapper


@case_insensitive
def __plain(text, substr):
    return OK if text.find(substr) == -1 else BAD


@case_insensitive
def __regex(text, pattern):
    return OK if not re.search(text, pattern) else BAD


def __word_list(text, path):
    with open(path, encoding="utf-8") as file:
        lines = [s.rstrip("\n") for s in file]
    return BAD if BAD in map(lambda x: __plain(text, x), lines) else OK
