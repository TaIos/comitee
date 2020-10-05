from src.rules.apply_rule_message import apply_rule_message
from src.constants import RULE_OK, RULE_FAIL


def apply_rule_path(rule, session, sha, reposlug, config_path, meta):
    owner, repo = reposlug.split("/")
    response = session.get(f'https://api.github.com/repos/{owner}/{repo}/commits/{sha}')
    status_wanted = rule.get("status")

    failed_filenames = []
    for file in response.json()["files"]:
        if status_wanted in [None, "*", file["status"]]:
            if apply_rule_message(rule, file["filename"], config_path) != RULE_OK:
                failed_filenames.append(file["filename"])

    meta["failed_filenames"] = failed_filenames
    return RULE_OK if len(failed_filenames) == 0 else RULE_FAIL
