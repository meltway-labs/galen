import os
from gettext import gettext as _
import signal

import click
from galen.utils import get_config, error, signal_handler

cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))


class GalenGroup(click.Group):
    def format_commands(self, ctx, formatter):
        commands = []
        for subcommand in self.list_commands(ctx):
            if subcommand.startswith("GROUP_"):
                cmd = self.get_command(ctx, subcommand[6:])
            else:
                cmd = self.get_command(ctx, subcommand)
            # Ignore non-existing commands
            if cmd is None:
                continue
            if cmd.hidden:
                continue

            commands.append((subcommand, cmd))

        # allow for 3 times the default spacing
        if len(commands) == 0:
            return

        limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)

        rows = []
        groups = []
        for subcommand, cmd in commands:
            help = cmd.get_short_help_str(limit)
            if subcommand.startswith("GROUP_"):
                groups.append((subcommand[6:], help))
            else:
                rows.append((subcommand, help))

        if groups:
            with formatter.section(_("Command Groups")):
                formatter.write_dl(groups)

        if rows:
            with formatter.section(_("Commands")):
                formatter.write_dl(rows)

    def list_commands(self, ctx):
        commands = []
        groups = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and not filename.startswith("__init__"):
                commands.append(filename[:-3])
            if not filename.endswith(".py"):
                for group_filename in os.listdir(os.path.join(cmd_folder, filename)):
                    if group_filename == "__init__.py":
                        groups.append(f"GROUP_{filename}")

        commands.sort()
        groups.sort()
        return groups + commands

    def get_command(self, ctx, name):
        try:
            mod = __import__(f"galen.commands.{name}", None, None, [name])
        except ImportError as e:
            print(f"Can't import command {name}. Exception: {e}")
            return
        return getattr(mod, name)


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(
    cls=GalenGroup,
    context_settings=CONTEXT_SETTINGS,
)
@click.version_option()
@click.option(
    "--profile",
    default=None,
    type=str,
    help="Pick the profile to use.",
)
@click.pass_context
def main(ctx, profile):
    """Like `tail -f` but for ElasticSearch."""
    signal.signal(signal.SIGINT, signal_handler)

    ctx.ensure_object(dict)

    user_config = get_config()

    if ctx.invoked_subcommand != "profile" and user_config["default_profile"] == "":
        error("No default profile set. Use `galen profile new` to create one.")
        ctx.abort()

    ctx.obj["config"] = user_config

    if profile is None:
        ctx.obj["profile"] = user_config["default_profile"]
    elif profile not in user_config["profiles"]:
        error(f"Profile {profile} not found.")
        ctx.abort()
    else:
        ctx.obj["profile"] = profile
