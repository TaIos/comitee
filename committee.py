import click
import configparser
import requests


def load_cfg(data):
    """Load and validate configuration file from string and return it as a configuration object"""
    cfg = configparser.ConfigParser()
    cfg.read_string(data)
    if not cfg.has_option("github", "token"):
        raise click.BadParameter("Configuration file does not contain github token.")
    if not cfg.has_option("committee", "context"):
        raise click.BadParameter("Configuration file does not contain comittee context.")
    return cfg


def validate_reposlug(ctx, param, value):
    sp = value.split("/")
    if len(sp) == 2 and len(sp[0]) != 0 and len(sp[1]) != 0:
        return value
    else:
        raise click.BadParameter(f"Reposlug \"{value}\" is not valid!")


def load_rules(cfg):
    """Load and validate rules from configuration object and return them as dictionary by rule name"""
    res = {}
    for section_name in cfg.sections():
        sp = section_name.split(":")
        if len(sp) == 2 and sp[0] == "rule":
            if not cfg.has_option(section_name, "text"):
                raise click.BadParameter(f"Rule {section_name} does not contain mandatory 'text' attribute.")
            if not cfg.has_option(section_name, "type"):
                raise click.BadParameter(f"Rule {section_name} does not contain mandatory 'type' attribute.")
            res[sp[1]] = cfg[section_name]
    return res


def create_github_session(cfg):
    """Create and return GitHub session authorized with token in configuration object"""
    session = requests.Session()
    token = cfg["github"]["token"]

    def token_auth(req):
        req.headers["Authorization"] = f"token {token}"
        return req

    session.auth = token_auth
    session.get(f"https://api.github.com").raise_for_status()
    return session


@click.command()
@click.version_option(version="0.1")
@click.option("-c", "--config", help="Committee configuration file.", metavar="FILENAME",
              type=click.File('r'), default="committee.cfg")
@click.option("-a", "--author", help="GitHub login or email address of author for checking commits.", metavar="AUTHOR")
@click.option("-p", "--path", help="Only commits containing this file path will be checked.", metavar="PATH")
@click.option("-r", "--ref", help="SHA or branch to check commits from (default is the default branch).", metavar="REF")
@click.option("-f", "--force", help="Check even if commit has already status with the same context.", is_flag=True,
              default=False)
@click.option("-o", "--output-format", help="Verbosity level of the output.  [default: commits]",
              type=click.Choice(["none", "commits", "rules"], case_sensitive=False), default="commits")
@click.option("-d", "--dry-run", help="No changes will be made on GitHub.", is_flag=True, default=False)
@click.argument("REPOSLUG", required=True, callback=validate_reposlug)
def comitee(config, author, path, ref, force, dry_run, output_format, reposlug):
    """An universal tool for checking commits on GitHub"""
    cfg = load_cfg(config.read())
    rules = load_rules(cfg)
    session = create_github_session(cfg)

    # TODO
    for name, rule in rules.items():
        if name == "polite-message":
            pass
        elif name == "keep-license":
            pass
        elif name == "no-dummy-files":
            pass
        elif name == "atomic-commits":
            pass
        else:
            raise click.BadParameter(f"Rule '{name}' in configuration file is not supported.")


if __name__ == "__main__":
    comitee()
