import requests
from src.constants import *
from src.helpers import sort_and_concat, get_failed_rule_names
from src.printing import print_to_term


def apply_validation_result(violations, session, commit, dry_run, output_format, force, reposlug, context):
    commit_status_change = __set_status(violations, session, force, reposlug, commit["sha"], dry_run, context)
    result_for_commit = __get_result_for_commit(violations, commit_status_change)
    print_to_term(commit["sha"], commit["commit"]["message"], violations, commit_status_change, result_for_commit,
                  output_format)


def __set_status(violations, session, force, reposlug, sha, dry_run, context):
    if dry_run:
        return COMMIT_STATUS_DRY_RUN

    owner, repo = reposlug.split("/")
    violation_names = get_failed_rule_names(violations)
    violated = False if len(violation_names) == 0 else True

    description = "No rules are violated by this commit." if violated == 0 \
        else f"The commit violates rules: {sort_and_concat(violation_names)}. "
    state = "failure" if violated else "success"

    try:
        if force or not __is_status_present(session, sha, reposlug, context):
            session.post(f'https://api.github.com/repos/{owner}/{repo}/statuses/{sha}',
                         json={"state": state, "description": description,
                               "context": reposlug}).raise_for_status()
        else:
            return COMMIT_STATUS_SKIPPED

    except requests.HTTPError as e:
        print(e)
        return COMMIT_STATUS_ERROR

    return COMMIT_STATUS_OK


def __is_status_present(session, sha, reposlug, context):
    owner, repo = reposlug.split("/")
    response = session.get(f'https://api.github.com/repos/{owner}/{repo}/commits/{sha}/statuses')
    response.raise_for_status()
    return context in list(map(lambda x: x["context"], response.json()))


def __get_result_for_commit(violations, commit_status_change):
    if commit_status_change == COMMIT_STATUS_SKIPPED:
        return RESULT_SKIPPED
    elif commit_status_change == COMMIT_STATUS_ERROR:
        return RESULT_ERROR
    elif RULE_FAIL in list(map(lambda x: x[2], violations)):
        return RESULT_FAILURE
    else:
        return RESULT_SUCCESS
