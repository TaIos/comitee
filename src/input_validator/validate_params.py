import click

from src.constants import VALID_INPUT
from src.input_validator.input_validate_reposlug import input_validate_reposlug


def validate_params(config, author, path, ref, force, dry_run, output_format, reposlug):
    if input_validate_reposlug(reposlug) != VALID_INPUT:
        raise click.BadParameter(f'Reposlug "{reposlug}" is not valid!')
