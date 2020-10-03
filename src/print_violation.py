import click


def print_violation(commit, reposlug, output_format):
    if output_format == "none":
        return

    form = '''
- {sha}: {message}
~> {commit_status_change}
=> {result_for_commit}
'''

    params = {
        "sha": click.style(commit["sha"], bold=True),
        "message": click.style("Some message", bold=True),
        "commit_status_change": click.style("OK", fg="green"),
        "result_for_commit": click.style("SUCCESS - No rules are violated by this commit.", fg="green")
    }

    # name = click.style(name, fg="green", bold=True)

    s = form.format(**params)
    print(s)
    if output_format == "commits ":
        pass
    if output_format == "rules":
        pass
