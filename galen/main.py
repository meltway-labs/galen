import datetime
import signal
import sys
import time
import os

import click
import requests
import appdirs
import toml

CONFIG_FOLDER_NAME = "galen"
CONFIG_FILE_NAME = "config.toml"

def warning(msg):
    click.secho(msg, fg="yellow", err=True)


def error(msg):
    click.secho(msg, fg="red", err=True)


def handler(signum, frame):
    sys.exit(0)


def create_empty_config():
    config_dir = appdirs.user_config_dir(CONFIG_FOLDER_NAME)
    # create empty config dir
    os.makedirs(config_dir)
    # create empty config file
    with open(os.path.join(config_dir, CONFIG_FILE_NAME), "w") as f:
        pass


def read_config():
    config_dir = appdirs.user_config_dir(CONFIG_FOLDER_NAME)
    # read toml config from file
    with open(os.path.join(config_dir, CONFIG_FILE_NAME), "r") as f:
        config = toml.loads(f.read())

    return config


def write_config(config):
    config_dir = appdirs.user_config_dir(CONFIG_FOLDER_NAME)
    # create empty config file
    with open(os.path.join(config_dir, CONFIG_FILE_NAME), "w") as f:
        tomli.dump(config, f)


def get_config():
    config_dir = appdirs.user_config_dir(CONFIG_FOLDER_NAME)
    if not os.path.exists(config_dir):
        create_empty_config()

    return read_config()


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
    print("config", user_config)

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