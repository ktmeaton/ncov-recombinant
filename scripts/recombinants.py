#!/usr/bin/env python3
import click
import os
import pandas as pd
import copy

# Hard-coded constants

NO_DATA_CHAR = "NA"


# Select and rename columns from linelist
RECOMBINANTS_COLS = [
    "cluster_id",
    "status",
    "lineage",
    "parents",
    "breakpoints",
    "issue",
    "subtree",
    "sequences",
    "growth",
    "earliest_date",
    "latest_date",
]


@click.command()
@click.option("--linelist", help="Linelist (tsv).", required=True)
@click.option(
    "--prev-linelist",
    help="Previous linelist (TSV) for growth calculation",
    required=False,
)
@click.option(
    "--geo",
    help="Geography column to use for summary",
    required=False,
    default="country",
)
def main(
    linelist,
    prev_linelist,
    geo,
):
    """Create a table of recombinant lineages"""

    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------

    # Misc variables
    outdir = os.path.dirname(linelist)

    linelist_df = pd.read_csv(linelist, sep="\t")
    linelist_df.fillna(NO_DATA_CHAR, inplace=True)

    linelist_df["datetime"] = pd.to_datetime(linelist_df["date"], format="%Y-%m-%d")

    if prev_linelist:
        prev_linelist_df = pd.read_csv(prev_linelist, sep="\t")
    else:
        prev_linelist_df = copy.deepcopy(linelist_df)

    # -------------------------------------------------------------------------
    # Create the recombinants table (recombinants.tsv)
    # -------------------------------------------------------------------------

    recombinants_data = {col: [] for col in RECOMBINANTS_COLS}
    recombinants_data[geo] = []

    for cluster_id in set(linelist_df["cluster_id"]):

        match_df = linelist_df[linelist_df["cluster_id"] == cluster_id]

        # TBD majority vote on disagreement
        recombinants_data["cluster_id"].append(cluster_id)
        recombinants_data["status"].append(match_df["status"].values[0])
        recombinants_data["lineage"].append(match_df["lineage"].values[0])
        recombinants_data["parents"].append(match_df["parents"].values[0])
        recombinants_data["breakpoints"].append(match_df["breakpoints"].values[0])
        recombinants_data["issue"].append(match_df["issue"].values[0])
        recombinants_data["subtree"].append(match_df["subtree"].values[0])
        recombinants_data["sequences"].append(len(match_df))
        recombinants_data["earliest_date"].append(min(match_df["datetime"]))
        recombinants_data["latest_date"].append(max(match_df["datetime"]))

        geo_list = list(set(match_df[geo]))
        geo_list.sort()
        geo_counts = []
        for loc in geo_list:
            loc_df = match_df[match_df[geo] == loc]
            num_sequences = len(loc_df)
            geo_counts.append("{} ({})".format(loc, num_sequences))

        recombinants_data[geo].append(", ".join(geo_counts))

        # Growth Calculation
        if "cluster_id" not in prev_linelist_df.columns:
            growth = 0
        else:
            prev_match_df = prev_linelist_df[
                prev_linelist_df["cluster_id"] == cluster_id
            ]
            growth = len(match_df) - len(prev_match_df)
            if growth > 0:
                growth = "+{}".format(growth)
            elif growth == 0:
                growth = "{}".format(growth)
            else:
                growth = "-{}".format(growth)

        recombinants_data["growth"].append(growth)

    recombinants_df = pd.DataFrame(recombinants_data)
    recombinants_df.sort_values(by="sequences", ascending=False, inplace=True)

    outpath = os.path.join(outdir, "recombinants.tsv")
    recombinants_df.to_csv(outpath, index=False, sep="\t")


if __name__ == "__main__":
    main()
