#!/usr/bin/env python3
import click
import os
import pandas as pd

# Hard-coded constants

NO_DATA_CHAR = "NA"


# Select and rename columns from linelist
PARENTS_COLS = [
    "parents",
    "sequences",
    "earliest_date",
    "latest_date",
]


@click.command()
@click.option("--linelist", help="Linelist (tsv).", required=True)
def main(
    linelist,
):
    """Create a table of recombinant sequences by parent"""

    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------

    # Misc variables
    outdir = os.path.dirname(linelist)

    linelist_df = pd.read_csv(linelist, sep="\t")
    linelist_df.fillna(NO_DATA_CHAR, inplace=True)

    linelist_df["datetime"] = pd.to_datetime(linelist_df["date"], format="%Y-%m-%d")

    # -------------------------------------------------------------------------
    # Create the parents table (parents.tsv)
    # -------------------------------------------------------------------------

    data = {col: [] for col in PARENTS_COLS}

    for parents in set(linelist_df["parents"]):

        match_df = linelist_df[linelist_df["parents"] == parents]

        if parents == NO_DATA_CHAR:
            parents = "Unknown"

        earliest_date = min(match_df["datetime"])
        latest_date = max(match_df["datetime"])
        sequences = len(match_df)

        data["parents"].append(parents)
        data["sequences"].append(sequences)
        data["earliest_date"].append(earliest_date)
        data["latest_date"].append(latest_date)

    parents_df = pd.DataFrame(data)
    parents_df.sort_values(by="sequences", ascending=False, inplace=True)

    outpath = os.path.join(outdir, "parents.tsv")
    parents_df.to_csv(outpath, index=False, sep="\t")


if __name__ == "__main__":
    main()
