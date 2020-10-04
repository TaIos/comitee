import requests
from src.constants import *
from src.helpers import sort_and_concat
from src.printing import print_to_term


def apply_validation_result(violations, session, commit, dry_run, output_format, force, reposlug):
    commit_status_change = __set_status(violations, session, force, reposlug, commit["sha"], dry_run)
    result_for_commit = __get_result_for_commit(violations, commit_status_change)
    print_to_term(commit["sha"], commit["message"], violations, commit_status_change, result_for_commit, output_format)


def __set_status(violations, session, force, reposlug, sha, dry_run):
    if dry_run:
        return COMMIT_STATUS_DRY_RUN

    owner, repo = reposlug.split("/")
    violated = False if len(violations) == 0 else True
    violation_names = list(map(lambda x: x[0], violations))
    description = "No rules are violated by this commit." if not violated \
        else f"The commit violates rules: {sort_and_concat(violation_names)}. "
    state = "success" if violated else "failure"

    try:
        if force or not __is_status_present(session, sha, reposlug):
            session.post(f'https://api.github.com/repos/{owner}/{repo}/statuses/{sha}/',
                         params={"state": state, "description": description, "context": reposlug}).raise_for_status()
        else:
            return COMMIT_STATUS_SKIPPED

    except requests.HTTPError:
        return COMMIT_STATUS_ERROR

    return COMMIT_STATUS_OK


def __is_status_present(session, sha, reposlug):
    owner, repo = reposlug.split("/")
    response = session.get(f'https://api.github.com/repos/{owner}/{repo}/commits/{sha}/statuses')
    response.raise_for_status()
    return reposlug in list(map(lambda x: x["context"], response))


def __get_result_for_commit(violations, commit_status_change):
    if commit_status_change == COMMIT_STATUS_SKIPPED:
        return RESULT_SKIPPED
    elif commit_status_change == COMMIT_STATUS_ERROR:
        return RESULT_ERROR
    elif RULE_FAIL in list(map(lambda x: x[2], violations)):
        return RESULT_FAILURE
    else:
        return RESULT_SUCCESS
