import configparser
import hashlib
import hmac
import itertools
import os
import sys
import pathlib

import click
import requests
from flask import Flask, request, jsonify, render_template

from committee.rules.apply_validation_result import apply_validation_result
from committee.constants import RULE_OK, VALID_INPUT, INVALID_INPUT
from committee.helpers import is_rule_name, get_rule_name
from committee.input_validator.input_validate_reposlug import input_validate_reposlug
from committee.input_validator.input_validate_rule import input_validate_rule
from committee.input_validator.input_validate_section_committee import input_validate_section_committee
from committee.input_validator.input_validate_section_github import input_validate_section_github
from committee.rules.apply_rule_message import apply_rule_message
from committee.rules.apply_rule_path import apply_rule_path
from committee.rules.apply_rule_stats import apply_rule_stats


def __load_cfg(ctx, param, value):
    cfg = configparser.ConfigParser()
    try:
        cfg.read_string(value.read())
        cfg.config_path = os.path.dirname(os.path.abspath(value.name))  # add file path dir to config
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


def __create_auth_github_session(cfg, session=None):
    """Create and return GitHub session authorized with token in configuration object"""
    session = session or requests.Session()
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
        for page in itertools.count(start=1):
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
        exit(1)


@click.command()
@click.version_option(prog_name='committee')
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
    return comitee_run(config, author, path, ref, force, dry_run, output_format, reposlug)


def comitee_run(config, author, path, ref, force, dry_run, output_format, reposlug, target_url=None):
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
        apply_validation_result(violations, session, commit, dry_run, output_format, force, reposlug, context,
                                target_url)


def main():
    comitee(prog_name='committee')


def __verify_signature(payload_body, signature, secret):
    calculated_signature = 'sha1=' + hmac.new(secret, payload_body, hashlib.sha1).hexdigest()
    return hmac.compare_digest(signature, calculated_signature)


def __github_ping():
    return jsonify({'success': True})


def __github_push(json_payload, config, target_url):
    reposlug = json_payload['repository']['full_name']

    response_commits = []
    for commit in json_payload['commits']:
        sha = commit['id']
        comitee_run(config=config, author=None, path=None, ref=sha, force=False, dry_run=False, output_format=None,
                    reposlug=reposlug, target_url=target_url)
        response_commits.append({"sha": sha})

    return jsonify({'success': True, 'target_url': request.base_url, 'commits': response_commits})


def __invalid_request_header():
    return jsonify({'error': 'invalid request header', 'success': False})


def __invalid_signature():
    return jsonify({'error': 'invalid signature', 'success': False})


def __invalid_github_event():
    return jsonify({'error': 'invalid github event', 'success': False})


def __empty_data():
    return jsonify({'error': 'no data', 'success': False})


def __configure_flask_app(app, cfg=None, session=None):
    committee_config_rel = os.environ.get('COMMITTEE_CONFIG', None)
    if committee_config_rel is None:
        print('COMMITTEE_CONFIG is not set.')
        exit(1)

    if not pathlib.Path(committee_config_rel).is_file():
        print('Invalid config file path.')
        exit(1)

    app.config['config_path'] = os.path.abspath(committee_config_rel)

    if cfg is None:
        try:
            with open(app.config['config_path'], 'r') as file:
                data = file.read()
        except OSError:
            app.logger.error(f'Could not open/read file: {app.config["config_path"]}')
            exit(1)
        cfg = configparser.ConfigParser()
        cfg.read_string(data)
    cfg.config_path = os.path.dirname(app.config['config_path'])

    if __validate_cfg(cfg) != VALID_INPUT:
        app.logger.error('Failed to load the configuration!')
        exit(1)

    app.config['cfg_object'] = cfg
    app.config['token'] = cfg['github']['token']
    app.config['context'] = cfg['committee']['context']
    app.config['rules'] = __load_rules(cfg)
    app.config['secret'] = cfg['github'].get('secret')  # None if missing

    session = session or __create_auth_github_session(cfg)
    r = session.get(f'https://api.github.com/user')
    app.config['username'] = r.json()['name']
    app.config['login'] = r.json()['login']

    app.logger.debug(
        f'Initialized flask with:  context={app.config["context"]}, username={app.config["username"]}')


def create_app(cfg=None, session=None):
    app = Flask(__name__)
    __configure_flask_app(app, cfg, session)

    @app.route('/', methods=['POST'])
    def post_github_webhook():

        if 'X-Github-Event' not in request.headers:
            return __invalid_request_header(), 400

        if not request.data:
            return __empty_data(), 200

        if app.config['secret'] and not __verify_signature(request.get_data(), request.headers.get('X-Hub-Signature'),
                                                           app.config['secret'].encode()):
            return __invalid_signature(), 400

        if request.headers.get('x-github-event') == 'ping':
            return __github_ping(), 200
        elif request.headers.get('x-github-event') == 'push':
            return __github_push(request.json, app.config['cfg_object'], request.base_url), 200
        else:
            return __invalid_github_event(), 400

    @app.route('/', methods=['GET'])
    def get_github_webhook():
        return render_template('settings_page.html', context=app.config['context'],
                               username=app.config['username'] + ", " + app.config['login'],
                               rules=app.config['rules']), 200

    return app
