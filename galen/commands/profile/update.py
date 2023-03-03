import click
import sys

from galen.main import main
from galen.utils import write_config


@main.command()
@click.argument("name", required=True)
@click.option(
    "-n",
    "--number",
    default=100,
    show_default=True,
    help="Number of lines to fetch on each iteration.",
)
@click.option(
    "-t",
    "--ticker",
    default=3,
    show_default=True,
    type=float,
    help="Interval in seconds to call ElasticSearch API.",
)
@click.option(
    "-d",
    "--delta",
    default=30,
    show_default=True,
    help="Number of seconds in the past to start querying data.",
)
@click.option(
    "--endpoint",
    help="Elasticsearch endpoint.",
)
@click.option(
    "--index",
    help="Elasticsearch index pattern.",
)
@click.option(
    "--username",
    help="Username for basic authentication.",
)
@click.option(
    "--password",
    default=False,
    type=bool,
    help="Password for basic authentication, reads from stdin.",
)
@click.pass_context
def update(ctx, name, number, ticker, delta, endpoint, index, username, password):
    """Update an existing profile."""

    profile = ctx.obj["config"]["profiles"][name]

    if number is not None:
        profile["number"] = number

    if ticker is not None:
        profile["ticker"] = ticker

    if delta is not None:
        profile["delta"] = delta

    if endpoint is not None:
        profile["endpoint"] = endpoint

    if index is not None:
        profile["index"] = index

    if username is not None:
        profile["username"] = username

    if password is not None:
        for line in sys.stdin:
            profile["password"] = line.strip()

    ctx.obj["config"]["profiles"][name] = profile

    write_config(ctx.obj["config"])
