from src.constants import RULE_OK, RULE_FAIL
import math


def apply_rule_stats(rule, session, sha, reposlug, meta):
    owner, repo = reposlug.split("/")
    response = session.get(f'https://api.github.com/repos/{owner}/{repo}/commits/{sha}')
    scope, stat, = rule.get("scope", fallback="commit"), rule.get("stat"),
    min_allowed, max_allowed = rule.getint("min", fallback=0), rule.getint("max", fallback=math.inf)

    if scope == "commit":
        return RULE_OK if min_allowed <= response.json()["stats"][stat] <= max_allowed else RULE_FAIL
    elif scope == "file":
        failed_filenames = []
        for file in response.json()["files"]:
            if not (min_allowed <= file[stat] <= max_allowed):
                failed_filenames.append(file["filename"])
        meta["failed_filenames"] = failed_filenames
        return RULE_OK if len(failed_filenames) == 0 else RULE_FAIL
