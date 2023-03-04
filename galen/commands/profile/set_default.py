import click
import sys

from galen.main import main
from galen.utils import error


@main.command()
@click.argument("name", required=True)
@click.pass_context
def set_default(ctx, name):
    """Set default profile."""

    if name not in ctx.obj["config"]["profiles"]:
        error(f"profile '{name}' does not exist")
        ctx.abort()

    ctx.obj["config"]["default_profile"] = name
