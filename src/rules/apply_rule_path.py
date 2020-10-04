from src.rules.apply_rule_message import apply_rule_message
from src.constants import RULE_OK, RULE_FAIL


def apply_rule_path(rule, session, sha, reposlug):
    owner, repo = reposlug.split("/")
    response = session.get(f'https://api.github.com/repos/{owner}/{repo}/commits/{sha}')
    status_wanted = rule.get("status")

    for file in response.json()["files"]:
        if status_wanted in [None, "*", file["status"]]:
            if apply_rule_message(rule, file["filename"]) != RULE_OK:
                return RULE_FAIL

    return RULE_OK
