import os

import click

from galen.main import main

cmd_folder = os.path.abspath(os.path.dirname(__file__))


class ProfileGroup(click.Group):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and not filename.startswith("__init__"):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            mod = __import__(f"galen.commands.profile.{name}", None, None, [name])
        except ImportError:
            return
        return getattr(mod, name)


@main.group(cls=ProfileGroup)
@click.pass_context
def profile(ctx):
    """Handle Galen Profile"""
    return
