#!/usr/bin/env python3

import requests
import click
import pandas as pd
import numpy as np
import sys
from datetime import datetime

NO_DATA_CHAR = "NA"
rate_limit_url = "https://api.github.com/rate_limit"
base_url = "https://api.github.com/repos/cov-lineages/pango-designation/issues"
params = "?state=all&per_page=100&page={page_num}"
query_url = base_url + params

# These issues have problems, and are manually curated in the breakpoints file
EXCLUDE_ISSUES = [808]


@click.command()
@click.option("--token", help="Github API Token", required=False)
@click.option(
    "--breakpoints",
    help=(
        "TSV of curated breakpoints with columns 'lineage', 'issue', and 'breakpoints'"
    ),
    required=False,
)
def main(token, breakpoints):
    """Fetch pango-designation issues"""

    breakpoints_curated = breakpoints

    # Construct the header
    header_cols = [
        "issue",
        "lineage",
        "status",
        "status_description",
        "countries",
        "breakpoints",
        "title",
        "date_created",
        "date_updated",
        "date_closed",
    ]
    df = pd.DataFrame(columns=header_cols)

    # Iterate through the pages of issues
    pages = range(1, 100)
    for page_num in pages:

        # Is the user supplied an API token, use it
        headers = ""
        if token:
            headers = {"Authorization": "token {}".format(token)}

        # Check the current rate limt
        r = requests.get(rate_limit_url, headers=headers)
        api_stats = r.json()
        requests_limit = api_stats["resources"]["core"]["limit"]
        requests_remaining = api_stats["resources"]["core"]["remaining"]

        reset_time = api_stats["resources"]["core"]["reset"]
        reset_date = datetime.fromtimestamp(reset_time)

        if requests_remaining == 0:
            msg = "ERROR: Hourly API limit of {} requests exceeded,".format(
                requests_limit
            )
            msg += " rate limit will reset after {}.".format(reset_date)
            print(msg, file=sys.stderr)
            sys.exit(1)

        # We're under the rate limit, and can proceed
        r = requests.get(query_url.format(page_num=page_num), headers=headers)
        issues_json = r.json()

        # The issues json will be empty if we ran out of pages
        if len(issues_json) == 0:
            break

        # Iterate through issues
        for issue in issues_json:

            # Assume not a recombinant
            recombinant = False
            number = issue["number"]

            # Check for excluded issues
            if number in EXCLUDE_ISSUES:
                continue

            # sanitize quotes out of title
            title = issue["title"].replace('"', "")
            # sanitize markdown formatters
            title = title.replace("*", "")

            # If title includes recombinant or recombinantion
            if "recombinant" in title.lower() or "recombination" in title.lower():
                recombinant = True

            # Designated lineages are stored under the milestone title
            lineage = ""
            milestone = issue["milestone"]
            if milestone:
                lineage = milestone["title"]

            # Detect recombinant by lineage nomenclature (X)
            if lineage:
                if lineage.startswith("X"):
                    recombinant = True
                else:
                    continue

            # Parse labels
            labels = issue["labels"]

            # labels are a our last chance, so if it doesn't have any skip
            if not recombinant and len(labels) == 0:
                continue

            status = ""
            status_description = ""
            if len(labels) > 0:
                status = labels[0]["name"]
                status_description = labels[0]["description"]

            # Check if the label (status) includes recombinant
            if "recombinant" in status.lower():
                recombinant = True

            # Skip to the next record if this is not a recombinant issue
            if not recombinant:
                continue

            # If a lineage hasn't been assigned,
            # use the propose# nomenclature from UShER
            if not lineage:
                lineage = "proposed{}".format(number)

            # Try to extract info from the body
            body = issue["body"]
            breakpoints = []
            countries = []

            # Skip issues without a body
            if not body:
                continue

            for line in body.split("\n"):

                line = line.strip().replace("*", "")

                # Breakpoints
                if "breakpoint:" in line.lower():
                    breakpoints.append(line)
                elif "breakpoint" in line.lower():
                    breakpoints.append(line)

                # Countries (nicely structures)
                if "countries circulating" in line.lower():
                    line = line.replace("Countries circulating:", "")
                    countries.append(line)

            breakpoints = ";".join(breakpoints)
            countries = ";".join(countries)

            # Dates
            date_created = issue["created_at"]
            date_updated = issue["updated_at"]
            date_closed = issue["closed_at"]

            if not date_closed:
                date_closed = NO_DATA_CHAR

            # Create the output data
            data = {col: "" for col in header_cols}
            data["issue"] = number
            data["lineage"] = lineage
            data["status"] = status
            data["status_description"] = status_description
            data["title"] = title
            data["countries"] = countries
            data["breakpoints"] = breakpoints
            data["date_created"] = date_created
            data["date_updated"] = date_updated
            data["date_closed"] = date_closed

            # Change data vals to lists for pandas
            data = {k: [v] for k, v in data.items()}
            # Convert dict to dataframe
            df_data = pd.DataFrame(data)
            # Add data to the main dataframe
            df = pd.concat([df, df_data], ignore_index=True)

    # -------------------------------------------------------------------------
    # Curate breakpoints

    if breakpoints_curated:
        df_breakpoints = pd.read_csv(breakpoints_curated, sep="\t")

        if (
            "breakpoints" in df_breakpoints.columns
            and "breakpoints_curated" not in df.columns
        ):
            df.insert(5, "breakpoints_curated", [""] * len(df))

        if "parents" in df_breakpoints.columns and "parents_curated" not in df.columns:
            df.insert(5, "parents_curated", [""] * len(df))

        for rec in df.iterrows():
            issue = rec[1]["issue"]
            lineage = rec[1]["lineage"]

            if issue not in list(df_breakpoints["issue"]):
                continue

            match = df_breakpoints[df_breakpoints["issue"] == issue]
            bp = list(match["breakpoints"])[0]
            parents = list(match["parents"])[0]

            if bp != np.nan:
                df.at[rec[0], "breakpoints_curated"] = bp
            if parents != np.nan:
                df.at[rec[0], "parents_curated"] = parents

        # Check for lineages with curated breakpoints that are missing
        # Ex. "XAY" and "XBA" were grouped into one issue
        for rec in df_breakpoints.iterrows():
            lineage = rec[1]["lineage"]

            if lineage in list(df["lineage"]):
                continue

            issue = rec[1]["issue"]
            breakpoints = rec[1]["breakpoints"]
            parents = rec[1]["parents"]

            row_data = {col: [""] for col in df.columns}
            row_data["lineage"][0] = lineage
            row_data["issue"][0] = rec[1]["issue"]
            row_data["breakpoints_curated"][0] = rec[1]["breakpoints"]
            row_data["parents_curated"][0] = rec[1]["parents"]

            row_df = pd.DataFrame(row_data)
            df = pd.concat([df, row_df])

    # -------------------------------------------------------------------------
    # Sort the final dataframe
    status_order = {"designated": 0, "recombinant": 1, "monitor": 2, "not accepted": 3}

    # Change empty cells to NaN so they'll be sorted to the end
    df = df.replace({"lineage": "", "status": ""}, np.nan)
    df.sort_values(
        [
            "status",
            "lineage",
        ],
        inplace=True,
        key=lambda x: x.map(status_order),
    )
    df.to_csv(sys.stdout, sep="\t", index=False)


if __name__ == "__main__":
    main()
