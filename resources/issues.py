#!/usr/bin/env python3

import requests
import click
import pandas as pd
import numpy as np


base_url = "https://api.github.com/repos/cov-lineages/pango-designation/issues"
params = "?state=all&per_page=100&page={page_num}"
query_url = base_url + params


@click.command()
@click.option("--token", help="Github API Token", required=True)
@click.option("--output", help="Output path", required=True)
def main(
    token,
    output,
):
    """Fetch pango-designation issues"""

    # Construct the header
    header_cols = [
        "issue",
        "lineage",
        "status",
        "status_description",
        "title",
        "countries",
        "breakpoint",
        "date_created",
        "date_updated",
        "date_closed",
    ]
    df = pd.DataFrame(columns=header_cols)

    # Iterate through the pages of issues
    pages = range(1, 100)
    for page_num in pages:

        print("Fetching page: {}".format(page_num))

        # Fetch the issue page
        headers = {"Authorization": "token {}".format(token)}
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
            # sanitize quotes out of title
            title = issue["title"].replace('"', "")

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
            breakpoint = ""
            countries = ""

            for line in body.split("\n"):

                line = line.strip().replace("*", "")

                # Breakpoints
                if "breakpoint:" in line.lower():
                    breakpoint = line
                    break
                elif "breakpoint" in line.lower():
                    breakpoint = line

                # Countries (nicely structures)
                if "countries circulating" in line.lower():
                    countries = line.replace("Countries circulating:", "")

            # Dates
            date_created = issue["created_at"]
            date_updated = issue["updated_at"]
            date_closed = issue["closed_at"]

            # Create the output data
            data = {col: "" for col in header_cols}
            data["issue"] = number
            data["lineage"] = lineage
            data["status"] = status
            data["status_description"] = status_description
            data["title"] = title
            data["countries"] = countries
            data["breakpoint"] = breakpoint
            data["date_created"] = date_created
            data["date_updated"] = date_updated
            data["date_closed"] = date_closed

            # Change data vals to lists for pandas
            data = {k: [v] for k, v in data.items()}
            # Convert dict to dataframe
            df_data = pd.DataFrame(data)
            # Add data to the main dataframe
            df = pd.concat([df, df_data], ignore_index=True)

        break

    # Change empty cells to NaN so they'll be sorted to the end
    df = df.replace("", np.nan)
    df.sort_values(["lineage", "status"], inplace=True)
    # Restore the nan values to empty string
    df.fillna("", inplace=True)

    df.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    main()
