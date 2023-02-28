import datetime
import signal
import sys
import time
import os

import click
import requests
import appdirs
import tomli

def warning(msg):
    click.secho(msg, fg="yellow", err=True)


def error(msg):
    click.secho(msg, fg="red", err=True)


def handler(signum, frame):
    sys.exit(0)


def get_config():
    user_config = appdirs.user_config_dir("galen")
    if not os.path.exists(user_config):
        # create empty config dir
        os.makedirs(user_config)
        # create empty config file
        with open(os.path.join(user_config, "config.toml"), "w") as f:
            pass

    # read toml config from file
    with open(os.path.join(user_config, "config.toml"), "r") as f:
        config = tomli.loads(f.read())

    return config


@click.group()
def main():
    pass

@click.command()
def profile():
    pass

@click.command()
@click.argument("filter_query", required=True)
@click.option(
    "--endpoint",
    help="Elasticsearch endpoint with index pattern",
    required=True,
)
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
    "--extra-filter",
    default=None,
    type=str,
    help="Extra filter appended to filter.",
)
@click.version_option()
def tail(filter_query, endpoint, extra_filter, number, ticker, delta):
    """Like `tail -f` but for ElasticSearch."""
    signal.signal(signal.SIGINT, handler)

    elasticsearch_endpoint = f"{endpoint}/_search"

    if extra_filter:
        filter_query += extra_filter

    user_config = get_config()

    payload = {
        "size": number,
        "query": {
            "bool": {
                "must": [
                    {"query_string": {"query": filter_query}},
                    {
                        "range": {
                            "@timestamp": {
                                "gte": (
                                    datetime.datetime.now()
                                    - datetime.timedelta(seconds=delta)
                                ).isoformat()
                            }
                        }
                    },
                ]
            }
        },
        "sort": [{"@timestamp": "asc"}],
    }

    first = True
    response = {}
    while True:
        if first:
            r = requests.post(elasticsearch_endpoint, json=payload)
            first = False
        else:
            if len(response["hits"]["hits"]):
                payload["search_after"] = response["hits"]["hits"][-1]["sort"]
            r = requests.post(elasticsearch_endpoint, json=payload)

        response = r.json()

        if not len(response["hits"]["hits"]):
            time.sleep(ticker)
            continue

        if r.status_code != 200:
            error("Error %d querying Kibana." % r.status_code)
            error(r.text)
            time.sleep(ticker)
            continue

        if response["hits"]["total"]["value"] == 0:
            time.sleep(ticker)
            continue

        for item in response["hits"]["hits"]:
            click.secho(item["_source"]["@timestamp"] + "\t- ", fg="blue", nl=False)
            click.echo(item["_source"]["message"].strip())
        time.sleep(ticker)

if __name__ == "__main__":
    main.add_command(tail)
    main()