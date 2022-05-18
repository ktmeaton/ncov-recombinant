#!/usr/bin/env python3
import click
import os
import pandas as pd

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
    "growth_score",
    "earliest_date",
    "latest_date",
]


@click.command()
@click.option("--linelist", help="Linelist (tsv).", required=True)
@click.option("--geo", help="Geography column", required=False, default="country")
def main(
    linelist,
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

    # -------------------------------------------------------------------------
    # Create the recombinants table (recombinants.tsv)
    # -------------------------------------------------------------------------

    recombinants_data = {col: [] for col in RECOMBINANTS_COLS}
    recombinants_data[geo] = []

    for cluster_id in set(linelist_df["cluster_id"]):

        match_df = linelist_df[linelist_df["cluster_id"] == cluster_id]

        earliest_date = min(match_df["datetime"])
        latest_date = max(match_df["datetime"])
        sequences = len(match_df)

        # TBD majority vote on disagreement
        recombinants_data["cluster_id"].append(cluster_id)
        recombinants_data["status"].append(match_df["status"].values[0])
        recombinants_data["lineage"].append(match_df["lineage"].values[0])
        recombinants_data["parents"].append(match_df["parents"].values[0])
        recombinants_data["breakpoints"].append(match_df["breakpoints"].values[0])
        recombinants_data["issue"].append(match_df["issue"].values[0])
        recombinants_data["subtree"].append(match_df["subtree"].values[0])

        recombinants_data["sequences"].append(sequences)
        recombinants_data["earliest_date"].append(earliest_date)
        recombinants_data["latest_date"].append(latest_date)

        geo_list = list(set(match_df[geo]))
        geo_list.sort()
        geo_counts = []
        for loc in geo_list:
            loc_df = match_df[match_df[geo] == loc]
            num_sequences = len(loc_df)
            geo_counts.append("{} ({})".format(loc, num_sequences))

        recombinants_data[geo].append(", ".join(geo_counts))

        # Growth Calculation
        growth_score = 0
        duration = (latest_date - earliest_date).days + 1
        growth_score = round(sequences / duration, 2)
        recombinants_data["growth_score"].append(growth_score)

    recombinants_df = pd.DataFrame(recombinants_data)
    recombinants_df.sort_values(by="sequences", ascending=False, inplace=True)

    outpath = os.path.join(outdir, "recombinants.tsv")
    recombinants_df.to_csv(outpath, index=False, sep="\t")


if __name__ == "__main__":
    main()
