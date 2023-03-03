import click
import datetime
import base64
import time
import urllib.parse

import requests
from galen.utils import error


@click.command()
@click.argument("filter_query", required=True)
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
@click.pass_context
def tail(ctx, filter_query, extra_filter, number, ticker, delta):
    """Like `tail -f` but for ElasticSearch."""

    if extra_filter:
        filter_query += extra_filter

    chosen_profile = ctx.obj["profile"]

    profile = ctx.obj["config"]["profiles"][chosen_profile]

    endpoint = profile["endpoint"]
    number = profile["number"]
    ticker = profile["ticker"]
    delta = profile["delta"]
    index = urllib.parse.quote(profile["index"])

    elasticsearch_endpoint = f"{endpoint}/{index}/_search"

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

    headers = {}
    if "username" in profile:
        auth = profile["username"] + ":" + profile["password"]
        auth_enc = base64.b64encode(auth.encode("utf-8")).decode("utf-8")
        headers = {"Authorization": "Basic " + auth_enc}

    first = True
    response = {}

    while True:
        if first:
            first = False
        elif len(response["hits"]["hits"]):
            payload["search_after"] = response["hits"]["hits"][-1]["sort"]

        r = requests.post(elasticsearch_endpoint, json=payload, headers=headers)

        if r.status_code != 200:
            error(f"http error (status {r.status_code}): {r.text}")
            ctx.abort()

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
            # convert string to datetime timestamp
            timestamp = datetime.datetime.strptime(
                item["_source"]["@timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).isoformat(timespec="milliseconds")

            # print timestamp in milliseconds using iso format
            click.secho(timestamp + "\t- ", fg="blue", nl=False)
            click.echo(item["_source"]["message"].strip())

        time.sleep(ticker)
