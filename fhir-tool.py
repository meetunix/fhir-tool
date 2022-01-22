import argparse
import json
import os
import sys
from pathlib import Path

import requests as rq
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def create_resource(ctx: dict, resource: str) -> tuple:

    url = ctx["base"]
    if ctx["credentials"] is not None:
        response = rq.post(
            url,
            headers=ctx["http_header"],
            data=resource.encode("utf-8"),
            verify=False,
            auth=ctx["credentials"],
        )
    else:
        response = rq.post(
            url, headers=ctx["http_header"], data=resource.encode("utf-8"), verify=False
        )
    # print(response.text)
    return response.status_code, response.text


def create_all(ctx: dict):

    for resource_file in ctx["resources"]:
        print(f"{resource_file.name}:", end="")
        resource = resource_file.read_text()
        status, response = create_resource(ctx, resource)
        if 200 <= status <= 300:
            rjson = json.loads(response)
            fhir_resource = rjson["resourceType"]
            # bundles have no id
            # fhir_id = rjson["id"]
            print(f" {fhir_resource} was uploaded")

        else:
            sys.stderr.write(
                f"\nunable to execute query for {resource_file.name} due to:\n{response}\n"
            )
            print()


def get_resources(ctx: dict) -> list:
    """Request metadata (CapabilityStatement) from FHIR-Server and return list of supported FHIR-Resources."""

    resources = []

    url = ctx["base"] + "/metadata"
    if ctx["credentials"] is not None:
        response = rq.get(
            url, headers=ctx["http_header"], verify=False, auth=ctx["credentials"]
        )
    else:
        response = rq.get(url, headers=ctx["http_header"], verify=False)

    if 200 <= response.status_code <= 300:
        rjson = json.loads(response.text)
        for resource in rjson["rest"][0]["resource"]:
            resources.append(resource["type"])

    else:
        sys.stderr.write(f"unable to execute query due to:\n{response}\n")
        sys.exit(1)

    return resources


def print_summary(ctx: dict) -> None:
    available_resources = get_resources(ctx)

    # collect count for each resource
    counts = {}
    with rq.session() as session:
        for res in available_resources:
            if ctx["credentials"] is not None:
                response = session.get(
                    f"{ctx['base']}/{res}?_summary=count",
                    verify=False,
                    auth=ctx["credentials"],
                )
            else:
                response = session.get(
                    f"{ctx['base']}/{res}?_summary=count", verify=False
                )
            rjson = json.loads(response.text)
            counts[res] = rjson["total"]
            # print(f"{rjson['total']:5} {res}")

    # sort dict by value
    counts = dict(sorted(counts.items(), key=lambda x: x[1]))

    for res, count in counts.items():
        if count > 0:
            print(f"{count:<7} {res}")


def main():

    rq.packages.urllib3.disable_warnings(InsecureRequestWarning)

    ctx = {}
    parser = argparse.ArgumentParser(
        description="FHIR-Tool mass import and statistics for FHIR servers"
    )
    parser.add_argument(
        "-b",
        "--base-path",
        type=str,
        help="base path of the FHIR-Server (in case of https: certs will not be verified)",
        required=True,
    )
    parser.add_argument(
        "-r",
        "--resource-directory",
        type=str,
        help="directory with resource files (json) for mass import.",
    )
    parser.add_argument(
        "-a",
        "--basic-authentication",
        type=str,
        help="use basic authentication: -a <USER>:<PASSWORD>",
    )
    parser.add_argument(
        "-s",
        "--summary",
        action="store_true",
        help="Print amount of instances for every resource type.",
    )

    args = parser.parse_args()
    ctx["base"] = args.base_path

    ctx["http_header"] = {
        "Accept": "application/fhir+json",
        "Content-Type": "application/fhir+json",
    }

    ctx["credentials"] = None
    if args.basic_authentication is not None:
        # TODO check for valid format
        username, password = args.basic_authentication.split(":")
        ctx["credentials"] = username, password

    if args.resource_directory is not None:
        query_path = Path(args.resource_directory)
        if not query_path.is_absolute():
            query_path = Path(os.getcwd()) / query_path
        # collect all resource file paths
        ctx["resources"] = sorted(query_path.glob("*.json"))
        create_all(ctx)
    elif args.summary:
        print_summary(ctx)


if __name__ == "__main__":
    main()
