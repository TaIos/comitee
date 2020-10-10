import os
import sys

import click
import configparser
import requests

from flask import Flask, request, jsonify, render_template

from src.apply_validation_result import apply_validation_result
from src.constants import RULE_OK, VALID_INPUT, INVALID_INPUT
from src.helpers import is_rule_name, get_rule_name
from src.input_validator.input_validate_reposlug import input_validate_reposlug
from src.input_validator.input_validate_rule import input_validate_rule
from src.input_validator.input_validate_section_committee import input_validate_section_committee
from src.input_validator.input_validate_section_github import input_validate_section_github
from src.rules.apply_rule_message import apply_rule_message
from src.rules.apply_rule_path import apply_rule_path
from src.rules.apply_rule_stats import apply_rule_stats


def __load_cfg(ctx, param, value):
    cfg = configparser.ConfigParser()
    try:
        cfg.read_string(value.read())
        cfg.config_path = os.path.dirname(value.name)  # add file path dir to config
    except configparser.Error:
        raise click.BadParameter("Failed to load the configuration!")
    if __validate_cfg(cfg) != VALID_INPUT:
        raise click.BadParameter("Failed to load the configuration!")
    return cfg


def __validate_cfg(cfg):
    if "github" not in cfg.sections() or "committee" not in cfg.sections():
        return INVALID_INPUT

    for section_name in cfg.sections():
        status = VALID_INPUT
        if section_name == "github":
            status = input_validate_section_github(cfg[section_name])
        elif section_name == "committee":
            status = input_validate_section_committee(cfg[section_name])
        elif is_rule_name(section_name):
            owd = os.getcwd()
            os.chdir(cfg.config_path)
            status = input_validate_rule(cfg[section_name])
            os.chdir(owd)

        if status != VALID_INPUT:
            return status

    return VALID_INPUT


def __load_rules(cfg):
    """Load validated rules from configuration object and return them as dictionary by rule name"""
    res = {}
    for section_name in cfg.sections():
        if is_rule_name(section_name):
            res[get_rule_name(section_name)] = cfg[section_name]
    return res


def __create_auth_github_session(cfg):
    """Create and return GitHub session authorized with token in configuration object"""
    session = requests.Session()
    token = cfg["github"]["token"]

    def token_auth(req):
        req.headers["Authorization"] = f"token {token}"
        return req

    session.auth = token_auth
    return session


def __validate_reposlug(ctx, param, value):
    if input_validate_reposlug(value) != VALID_INPUT:
        raise click.BadParameter(f'Reposlug "{value}" is not valid!')
    return value


def __fetch_all_commits(session, reposlug, author, path, ref):
    owner, repo = reposlug.split("/")
    try:
        commit_list = []
        while True:
            response = session.get(f'https://api.github.com/repos/{owner}/{repo}/commits',
                                   params={"author": author, "path": path, "sha": ref, "page": page})
            response.raise_for_status()

            js = response.json()
            if len(js) == 0:
                break

            # response can be either one commit (json object) or multiple commits (json array)
            if isinstance(js, list):
                commit_list = commit_list + js
            else:
                commit_list.append(js)

        return commit_list
    except requests.HTTPError:
        print(f"Failed to retrieve commits from repository {reposlug}.", file=sys.stderr)


@click.command()
@click.version_option(version="0.1")
@click.option("-c", "--config", help="Committee configuration file.", metavar="FILENAME",
              type=click.File('r'), required=True, callback=__load_cfg)
@click.option("-a", "--author", help="GitHub login or email address of author for checking commits.", metavar="AUTHOR",
              default=None)
@click.option("-p", "--path", help="Only commits containing this file path will be checked.", metavar="PATH",
              default=None)
@click.option("-r", "--ref", help="SHA or branch to check commits from (default is the default branch).", metavar="REF",
              default=None)
@click.option("-f", "--force", help="Check even if commit has already status with the same context.", is_flag=True,
              default=False)
@click.option("-o", "--output-format", help="Verbosity level of the output.  [default: commits]",
              type=click.Choice(["none", "commits", "rules"], case_sensitive=False), default="commits")
@click.option("-d", "--dry-run", help="No changes will be made on GitHub.", is_flag=True, default=False)
@click.argument("REPOSLUG", required=True, callback=__validate_reposlug)
def comitee(config, author, path, ref, force, dry_run, output_format, reposlug):
    """An universal tool for checking commits on GitHub"""
    rules = __load_rules(config)
    session = __create_auth_github_session(config)
    commits = __fetch_all_commits(session, reposlug, author, path, ref)
    context = config["committee"]["context"]

    for commit in commits:
        violations = []
        for name, rule in rules.items():
            status = RULE_OK
            meta = {}
            if rule["type"] == "message":
                status = apply_rule_message(rule, commit["commit"]["message"], config.config_path)
            elif rule["type"] == "path":
                status = apply_rule_path(rule, session, commit["sha"], reposlug, config.config_path, meta)
            elif rule["type"] == "stats":
                status = apply_rule_stats(rule, session, commit["sha"], reposlug, meta)
            violations.append({"name": name, "rule": rule, "status": status, "meta": meta})
        apply_validation_result(violations, session, commit, dry_run, output_format, force, reposlug, context)


if __name__ == "__main__":
    comitee()


def create_app(config=None):
    app = Flask(__name__)

    @app.route('/', methods=['POST'])
    def post_github_webhook():
        return request.json

    @app.route('/', methods=['GET'])
    def get_github_webhook():
        return render_template('settings_page.html', context='LQpKH20/657757dd', username='LQpKH20',
                               rules=[{'rule': 'polite-message', 'text': 'Commit message contains dirty words.',
                                       'match': 'wordlist:tests/fixtures/wordlists/forbidden.txt'},
                                      {'rule': 'keep-license', 'text': 'LICENSE should not be removed.',
                                       'type': 'path', 'status': 'removed', 'match': 'plain:LICENSE'}])

    return app
