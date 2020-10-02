from rules.apply_rule_message import apply_rule_message
from src.helpers import OK, BAD


def apply_rule_path(rule, session, commit, reposlug):
    owner, repo = reposlug.split("/")
    response = session.get(f'https://api.github.com/repos/{owner}/{repo}/commits/{commit["sha"]}')
    status_wanted = rule.get("status")

    for file in response.json()["files"]:
        if status_wanted in [None, "*", file["status"]]:
            if apply_rule_message(rule, file["filename"]) != OK:
                return BAD

    return OK
