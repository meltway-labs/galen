import click
import sys

from galen.main import main
from galen.utils import write_config


@main.command()
@click.pass_context
def list(ctx):
    """List profiles."""

    for profile in ctx.obj["config"]["profiles"]:
        if profile == ctx.obj["config"]["default_profile"]:
            click.secho(profile + " (default)")
        else:
            click.secho(profile)

