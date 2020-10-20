import click

from committee.util.helpers import sort_and_concat, get_failed_rule_names
from committee.util.constants import *


def print_to_term(sha, commit_msg, violations, commit_status_change, result_for_commit, output_format):
    str_sha_message = "- " + click.style(f'{sha}: {commit_msg}', bold=True)
    str_commit_status_change = click.style("  ~> ", bold=True) + __get_commit_status_change_string(commit_status_change)
    str_result_for_commit = click.style("  => ", bold=True) + __get_result_for_commit_string(
        get_failed_rule_names(violations), result_for_commit)
    str_rules = __get_rule_text(violations)

    if output_format == "none":
        return

    click.echo(str_sha_message)
    if result_for_commit == RESULT_SKIPPED:
        click.echo(str_result_for_commit)
        return

    if output_format == "rules":
        click.echo(str_rules)

    click.echo(str_commit_status_change)
    click.echo(str_result_for_commit)


def __get_commit_status_change_string(commit_status_change):
    change = ""
    if commit_status_change == COMMIT_STATUS_DRY_RUN:
        change = "{}".format(click.style("DRY-RUN", fg="yellow"))
    elif commit_status_change == COMMIT_STATUS_OK:
        change = "{}".format(click.style("OK", fg="green"))
    elif commit_status_change == COMMIT_STATUS_ERROR:
        change = "{}".format(click.style("ERROR", fg="magenta"))
    return "Updating commit status: " + change


def __get_result_for_commit_string(violation_names, result_for_commit):
    result = ""
    if result_for_commit == RESULT_SKIPPED:
        result = "{}".format(click.style("SKIPPED", fg="yellow")) \
                 + " - This commit already has status with the same context."
    elif result_for_commit == RESULT_SUCCESS:
        result = "{}".format(click.style("SUCCESS", fg="green")) \
                 + " - No rules are violated by this commit."
    elif result_for_commit == RESULT_FAILURE:
        result = "{}".format(click.style("FAILURE", fg="red")) \
                 + f" - The commit violates rules: {sort_and_concat(violation_names)}."
    elif result_for_commit == RESULT_ERROR:
        result = "{}".format(click.style("ERROR", fg="magenta")) \
                 + " - Failed to check the commit."
    return result


def __get_rule_text(violations):
    rule_text = []
    for violation in sorted(violations, key=lambda x: x["name"]):
        if violation["status"] == RULE_OK:
            rule_text.append("  -> " + violation["name"] + ": " + click.style("PASS", fg="green"))
        elif violation["status"] == RULE_FAIL:
            if "failed_filenames" in violation["meta"] and len(violation["meta"]["failed_filenames"]) != 0:
                text = "  -> " + violation["name"] + ": " + click.style("FAIL", fg="red")
                for filename in violation["meta"]["failed_filenames"]:
                    text += "\n     - " + filename + ": " + violation["rule"].get("text")
                rule_text.append(text)
            else:
                rule_text.append(
                    "  -> " + violation["name"] + ": " + click.style("FAIL", fg="red") + "\n     - " + violation[
                        "rule"].get("text"))

    return "\n".join(rule_text)
