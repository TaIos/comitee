import click
import configparser


def load_cfg(data):
    """Load and validate configuration file and return it"""
    config = configparser.ConfigParser()
    config.read_string(data)
    if not config.has_option("github", "token"):
        raise click.BadParameter("Configuration file does not contain github token.")
    if not config.has_option("committee", "context"):
        raise click.BadParameter("Configuration file does not contain comittee context context.")
    return config


def validate_reposlug(ctx, param, value):
    sp = value.split("/")
    if len(sp) == 2 and len(sp[0]) != 0 and len(sp[1]) != 0:
        return value
    else:
        raise click.BadParameter(f"Reposlug \"{value}\" is not valid!")


@click.command()
@click.version_option(version="0.1")
@click.option("-c", "--config", help="Committee configuration file.", metavar="FILENAME",
              type=click.File('r'))
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


if __name__ == "__main__":
    comitee()
