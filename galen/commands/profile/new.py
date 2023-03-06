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
    required=True,
)
@click.option(
    "--index",
    help="Elasticsearch index pattern.",
    required=True,
)
@click.option(
    "--username",
    help="Username for basic authentication, reads password from stdin.",
)
@click.pass_context
def new(ctx, name, number, ticker, delta, endpoint, index, username, password):
    """Create a new profile."""

    profile = {
        "number": number,
        "ticker": ticker,
        "delta": delta,
        "endpoint": endpoint,
        "index": index,
    }

    if username is not None:
        profile["username"] = username
        for line in sys.stdin:
            profile["password"] = line.strip()

    if ctx.obj["config"]["default_profile"] == "":
        ctx.obj["config"]["default_profile"] = name

    ctx.obj["config"]["profiles"][name] = profile

    write_config(ctx.obj["config"])
