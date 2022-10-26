#!/usr/bin/env python3
import click
import os
import pandas as pd
from datetime import datetime, date

# Hard-coded constants

NO_DATA_CHAR = "NA"


# Select and rename columns from linelist
LINEAGE_COLS = [
    "cluster_id",
    "status",
    "lineage",
    "recombinant_lineage_curated",
    "parents_clade",
    "parents_lineage",
    "parents_lineage_confidence",
    "breakpoints",
    "issue",
    "sequences",
    "growth_score",
    "earliest_date",
    "latest_date",
    "cluster_privates",
    "cov-spectrum_query",
]


@click.command()
@click.option(
    "--input", help="Input file of recombinant sequences (tsv).", required=True
)
@click.option(
    "--output", help="Output file of recombinant lineages (tsv)", required=True
)
@click.option("--geo", help="Geography column", required=False, default="country")
def main(
    input,
    output,
    geo,
):
    """Create a table of recombinant lineages"""

    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------

    # Misc variables
    outdir = os.path.dirname(output)
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    df = pd.read_csv(input, sep="\t")
    df.fillna(NO_DATA_CHAR, inplace=True)

    issues_format = []

    for issue in df["issue"]:
        if type(issue) == int:
            issues_format.append(int(issue))
        elif type(issue) == float:
            issue = str(int(issue))
            issues_format.append(issue)
        elif type(issue) == str:
            issues_format.append(issue)

    df["issue"] = issues_format

    # Issue #168 NULL dates are allowed
    # Set to today instead
    # https://github.com/ktmeaton/ncov-recombinant/issues/168
    seq_date = []
    for d in list(df["date"]):
        try:
            d = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            # Set NA dates to today
            d = date.today()

        seq_date.append(d)
    df["datetime"] = seq_date

    # -------------------------------------------------------------------------
    # Create the recombinants table (recombinants.tsv)
    # -------------------------------------------------------------------------

    recombinants_data = {col: [] for col in LINEAGE_COLS}
    recombinants_data[geo] = []

    for cluster_id in set(df["cluster_id"]):

        match_df = df[df["cluster_id"] == cluster_id]

        earliest_date = min(match_df["datetime"])
        latest_date = max(match_df["datetime"])
        sequences = len(match_df)

        # TBD majority vote on disagreement
        recombinants_data["cluster_id"].append(cluster_id)
        recombinants_data["status"].append(match_df["status"].values[0])
        recombinants_data["lineage"].append(match_df["lineage"].values[0])
        recombinants_data["recombinant_lineage_curated"].append(
            match_df["recombinant_lineage_curated"].values[0]
        )
        recombinants_data["parents_clade"].append(match_df["parents_clade"].values[0])
        recombinants_data["parents_lineage"].append(
            match_df["parents_lineage"].values[0]
        )
        recombinants_data["parents_lineage_confidence"].append(
            match_df["parents_lineage_confidence"].values[0]
        )
        recombinants_data["breakpoints"].append(match_df["breakpoints"].values[0])
        recombinants_data["issue"].append(match_df["issue"].values[0])
        recombinants_data["sequences"].append(sequences)
        recombinants_data["earliest_date"].append(earliest_date)
        recombinants_data["latest_date"].append(latest_date)
        recombinants_data["cluster_privates"].append(
            match_df["cluster_privates"].values[0]
        )
        recombinants_data["cov-spectrum_query"].append(
            match_df["cov-spectrum_query"].values[0]
        )

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
    recombinants_df.to_csv(output, index=False, sep="\t")


if __name__ == "__main__":
    main()
