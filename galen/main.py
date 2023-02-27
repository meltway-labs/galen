import datetime
import signal
import sys
import time

import click
import requests


def warning(msg):
    click.secho(msg, fg="yellow", err=True)


def error(msg):
    click.secho(msg, fg="red", err=True)


def handler(signum, frame):
    sys.exit(0)


@click.command()
@click.argument("filter", metavar="filter_query", required=True)
@click.option(
    "--endpoint", help="Elasticsearch endpoint with index pattern", required=True
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
@click.version_option()
def main(filter_query, endpoint, extra_filter, number, ticker, delta):
    """Like `tail -f` but for ElasticSearch."""
    signal.signal(signal.SIGINT, handler)

    elasticsearch_endpoint = f"{endpoint}/_search"

    if extra_filter:
        filter_query += extra_filter

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
