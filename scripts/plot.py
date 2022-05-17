#!/usr/bin/env python3
import click
import os
import pandas as pd
import epiweeks
import matplotlib.pyplot as plt

NO_DATA_CHAR = "NA"

# designated: X*
# proposed: proposed* or associated issue
# unpublished: not designated or proposed

RECOMBINANT_STATUS = {
    "designated": "X*",
    "proposed": "proposed*",
    "unpublished": "misc*",
}

# Concise names for report
CLADES_RENAME = {
    "Alpha/B.1.1.7/20I": "Alpha (20I)",
    "Delta/21I": "Delta (21I)",
    "Delta/21J": "Delta (21J)",
    "Omicron/21K": "BA.1",
    "Omicron/21L": "BA.2",
}

D3_PAL = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
]


@click.command()
@click.option("--linelist", help="Recombinant sequences (TSV)", required=True)
def main(
    linelist,
):
    """Create a report of powerpoint slides"""

    outdir = os.path.dirname(linelist)

    # Import dataframes
    linelist_df = pd.read_csv(linelist, sep="\t")

    # Add datetime columns
    linelist_df["datetime"] = pd.to_datetime(linelist_df["date"], format="%Y-%m-%d")
    linelist_df["year"] = [d.year for d in linelist_df["datetime"]]
    linelist_df["epiweek"] = [
        epiweeks.Week.fromdate(d, system="iso").startdate()
        for d in linelist_df["datetime"]
    ]

    # Dates
    dates_df = pd.pivot_table(
        data=linelist_df.sort_values(by="epiweek"),
        values="strain",
        index=["epiweek"],
        columns=["status"],
        aggfunc="count",
    )

    dates_df.fillna(0, inplace=True)
    dates_df["epiweek"] = dates_df.index
    # dates_df["epiweek"] = [i[0] for i in dates_df.index]
    # dates_df["status"] = [i[1] for i in dates_df.index]
    # dates_df.rename(columns={"strain" : "sequences"}, inplace=True)
    print(dates_df)

    out_path = os.path.join(outdir, "linelist.dates.tsv")
    dates_df.to_csv(out_path, sep="\t", index=False)

    # -------------------------------------------------------------------------
    # Timeline

    dpi = 200
    figsize = [16, 6]
    fig, ax = plt.subplots(
        1,
        figsize=figsize,
        dpi=dpi,
    )

    ax.set_title("Timeline of Recombinant Sequences in Canada", fontweight="bold")

    dates_df.plot.bar(stacked=True, ax=ax, edgecolor="black", width=0.75)

    ax.set_ylabel("Number of Sequences")
    ax.set_xlabel("Start of Week")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.legend(title="Status")

    out_path = os.path.join(outdir, "linelist.dates")
    plt.savefig(out_path + ".png", bbox_inches="tight")


if __name__ == "__main__":
    main()
