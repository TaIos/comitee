from src.helpers import OK, BAD
import functools


def apply_rule_stats(rule, session, sha, reposlug):
    owner, repo = reposlug.split("/")
    response = session.get(f'https://api.github.com/repos/{owner}/{repo}/commits/{sha}')
    scope, stat, = rule.get("scope", fallback="commit"), rule.get("stat"),

    value = 0
    if scope == "commit":
        value = response.json()["stats"][stat]
    elif scope == "file":
        value = functools.reduce(lambda a, b: a + b, map(lambda x: int(x[stat]), response.json()["files"]), 0)

    min_allowed, max_allowed = rule.getint("min", fallback=0), rule.getint("max", fallback=value)
    return OK if min_allowed <= value <= max_allowed else BAD
