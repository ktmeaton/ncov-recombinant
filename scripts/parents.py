#!/usr/bin/env python3
import click
import os
import pandas as pd
from datetime import datetime, date

# Hard-coded constants

NO_DATA_CHAR = "NA"


# Select and rename columns from linelist
PARENTS_COLS = [
    "parents_clade",
    "sequences",
    "earliest_date",
    "latest_date",
]


@click.command()
@click.option(
    "--input", help="Input file of recombinant sequences (tsv).", required=True
)
@click.option(
    "--output", help="Output file of recombinant lineages (tsv)", required=True
)
def main(
    input,
    output,
):
    """Create a table of recombinant sequences by parent"""

    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------

    # Misc variables
    outdir = os.path.dirname(input)
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    df = pd.read_csv(input, sep="\t")
    df.fillna(NO_DATA_CHAR, inplace=True)

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
    # Create the parents table (parents.tsv)
    # -------------------------------------------------------------------------

    data = {col: [] for col in PARENTS_COLS}

    for parents_clade in set(df["parents_clade"]):

        match_df = df[df["parents_clade"] == parents_clade]

        if parents_clade == NO_DATA_CHAR:
            parents_clade = "Unknown"

        earliest_date = min(match_df["datetime"])
        latest_date = max(match_df["datetime"])
        sequences = len(match_df)

        data["parents_clade"].append(parents_clade)
        data["sequences"].append(sequences)
        data["earliest_date"].append(earliest_date)
        data["latest_date"].append(latest_date)

    parents_df = pd.DataFrame(data)
    parents_df.sort_values(by="sequences", ascending=False, inplace=True)

    outpath = os.path.join(outdir, "parents.tsv")
    parents_df.to_csv(outpath, index=False, sep="\t")


if __name__ == "__main__":
    main()
