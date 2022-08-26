#!/usr/bin/env python3
import click
import os
import pandas as pd
import numpy as np
import epiweeks
import matplotlib.pyplot as plt
from matplotlib import patches, colors
from datetime import datetime, timedelta
import sys
import copy
from functions import categorical_palette
import math

NO_DATA_CHAR = "NA"
ALPHA_LAG = 0.25
ALPHA_BAR = 1.00
WIDTH_BAR = 0.75
EPIWEEK_MAX_BUFF_FACTOR = 1.1
# This is the aspect ratio/dpi for ppt embeds
# The dimensions are set in the powerpoint template (resources/template.pttx)
DPI = 96 * 2
FIGSIZE = [6.75, 5.33]

UNKNOWN_COLOR = "dimgrey"
UNKNOWN_RGB = colors.to_rgb(UNKNOWN_COLOR)

# This is the number of characters than can fit width-wise across the legend
LEGEND_FONTSIZE = 6
LEGEND_CHAR_WIDTH = 100
# The maximum columns in the legend is dictated by the char width, but more
# importantly, in the categorical_palette function, we restrict it to the
# first 5 colors of the tap10 palette, and make different shades within it
LEGEND_MAX_COL = 5

# Show the first N char of the label in the plot
LEGEND_LABEL_MAX_LEN = 15

# Select and rename columns from linelist
LINEAGES_COLS = [
    "cluster_id",
    "status",
    "lineage",
    "parents_clade",
    "parents_lineage",
    "breakpoints",
    "issue",
    "sequences",
    "growth_score",
    "earliest_date",
    "latest_date",
]

plt.rcParams["svg.fonttype"] = "none"


@click.command()
@click.option("--input", help="Recombinant sequences (TSV)", required=True)
@click.option("--outdir", help="Output directory", required=False, default=".")
@click.option(
    "--weeks",
    help="Number of weeks in retrospect to plot",
    required=False,
)
@click.option(
    "--min-date",
    help="Ignore sequences before this date (yyyy-mm-dd, overrides --weeks)",
    required=False,
)
@click.option("--max-date", help="Ignore sequences after this date", required=False)
@click.option(
    "--geo",
    help="Geography column to use when plotting",
    required=False,
    default="country",
)
@click.option(
    "--lag", help="Reporting lag weeks to draw a grey box", required=False, default=4
)
@click.option(
    "--singletons",
    help="Flag to indicate singleton clusters (N=1) should be reported.",
    is_flag=True,
)
def main(
    input,
    outdir,
    weeks,
    geo,
    lag,
    min_date,
    max_date,
    singletons,
):
    """Plot recombinant lineages"""

    # Creat output directory if it doesn't exist
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # -------------------------------------------------------------------------
    # Import dataframes
    df = pd.read_csv(input, sep="\t")

    # Add datetime columns
    df["datetime"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df["year"] = [d.year for d in df["datetime"]]
    df["epiweek"] = [
        epiweeks.Week.fromdate(d, system="cdc").startdate() for d in df["datetime"]
    ]

    # Filter on weeks reporting
    if max_date:
        max_datetime = datetime.strptime(max_date, "%Y-%m-%d")
        max_epiweek = epiweeks.Week.fromdate(max_datetime, system="cdc").startdate()
    else:
        max_epiweek = epiweeks.Week.fromdate(datetime.today(), system="cdc").startdate()

    if min_date:
        min_datetime = datetime.strptime(min_date, "%Y-%m-%d")
        min_epiweek = epiweeks.Week.fromdate(min_datetime, system="cdc").startdate()
    elif weeks:
        weeks = int(weeks)
        min_epiweek = max_epiweek - timedelta(weeks=(weeks - 1))
    elif len(df) == 0:
        # Just need something for empty plots
        min_epiweek = max_epiweek - timedelta(weeks=16)
    else:
        min_epiweek = epiweeks.Week.fromdate(
            min(df["epiweek"]), system="cdc"
        ).startdate()

    weeks = int((max_epiweek - min_epiweek).days / 7)

    # Dummy data outside of plotting range when empty
    one_week_prev = min_epiweek - timedelta(weeks=1)

    df = copy.deepcopy(
        df[(df["epiweek"] >= min_epiweek) & (df["epiweek"] <= max_epiweek)]
    )

    # Change status to title case
    df["status"] = [s.title() for s in df["status"]]

    # Get largest lineage
    largest_lineage = NO_DATA_CHAR
    largest_lineage_size = 0

    # All record cluster sizes to decided if singletons should be dropped
    drop_singleton_ids = []

    for lineage in set(df["recombinant_lineage_curated"]):
        match_df = df[df["recombinant_lineage_curated"] == lineage]
        lineage_size = len(match_df)
        if lineage_size >= largest_lineage_size:
            largest_lineage = match_df["recombinant_lineage_curated"].values[0]
            largest_lineage_size = lineage_size

        if lineage_size == 1:
            for i in match_df.index:
                drop_singleton_ids.append(i)

    # now decided if we should drop singletons
    if not singletons:
        df.drop(labels=drop_singleton_ids, axis="rows", inplace=True)

    df["parents_clade"] = df["parents_clade"].fillna("Unknown")
    df["parents_lineage"] = df["parents_lineage"].fillna("Unknown")

    # -------------------------------------------------------------------------
    # Pivot Tables
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # All
    all_df = pd.pivot_table(
        data=df.sort_values(by="epiweek"),
        values="strain",
        index=["epiweek"],
        aggfunc="count",
    )
    all_df.index.name = None
    all_df.fillna(0, inplace=True)
    all_df.insert(0, "epiweek", all_df.index)
    # Check if it was empty
    if len(all_df) == 0:
        all_df.insert(1, "sequences", [])
        max_epiweek_sequences = 0
    else:
        all_df.rename(columns={"strain": "sequences"}, inplace=True)
        max_epiweek_sequences = max(all_df["sequences"])

    # Attempt to dynamically create pivot tables
    plot_dict = {
        "lineage": {
            "legend_title": "lineage",
            "cols": ["recombinant_lineage_curated"],
            "y": "recombinant_lineage_curated",
        },
        "status": {"legend_title": "status", "cols": ["status"]},
        "geography": {"legend_title": geo, "cols": [geo]},
        "largest": {
            "legend_title": geo,
            "cols": [geo],
            "filter": "recombinant_lineage_curated",
            "value": largest_lineage,
        },
        "designated": {
            "legend_title": "lineage",
            "cols": ["recombinant_lineage_curated"],
            "filter": "status",
            "value": "Designated",
        },
        "proposed": {
            "legend_title": "lineage",
            "cols": ["recombinant_lineage_curated"],
            "filter": "status",
            "value": "Proposed",
        },
        "unpublished": {
            "legend_title": "lineage",
            "cols": ["recombinant_lineage_curated"],
            "filter": "status",
            "value": "Unpublished",
        },
        "parents_clade": {"legend_title": "Parents (Clade)", "cols": ["parents_clade"]},
        "parents_lineage": {
            "legend_title": "Parents (Lineage)",
            "cols": ["parents_lineage"],
        },
        "cluster_id": {"legend_title": "Cluster ID", "cols": ["cluster_id"]},
    }

    for plot in plot_dict:
        columns = plot_dict[plot]["cols"]

        # Several plots need special filtering
        if "filter" in plot_dict[plot]:
            filter = plot_dict[plot]["filter"]
            value = plot_dict[plot]["value"]

            plot_df = pd.pivot_table(
                data=df[df[filter] == value].sort_values(by="epiweek"),
                values="strain",
                index=["epiweek"],
                columns=columns,
                aggfunc="count",
            )

        # Otherwise no filtering required
        else:
            plot_df = pd.pivot_table(
                data=df.sort_values(by="epiweek"),
                index=["epiweek"],
                values="strain",
                aggfunc="count",
                columns=columns,
            )

        plot_df.index.name = None
        plot_df.fillna(0, inplace=True)

        # Convert counts from floats to integers
        plot_df[plot_df.columns] = plot_df[plot_df.columns].astype(int)

        # Add epiweeks column
        plot_df.insert(0, "epiweek", plot_df.index)

        plot_dict[plot]["df"] = plot_df

    # -------------------------------------------------------------------------
    # Filter for Reporting Period
    # -------------------------------------------------------------------------

    # Add empty data for weeks if needed
    epiweek_map = {}
    iter_week = min_epiweek
    iter_i = 0
    df_list = [plot_dict[plot]["df"] for plot in plot_dict]
    while iter_week <= max_epiweek:

        for plot_df in df_list:

            if iter_week not in plot_df["epiweek"]:
                plot_df.at[iter_week, "epiweek"] = iter_week

        # Check if its the largest
        epiweek_map[iter_week] = iter_i
        iter_week += timedelta(weeks=1)
        iter_i += 1

    for plot_df in df_list:
        plot_df.fillna(0, inplace=True)
        plot_df.sort_values(by="epiweek", axis="index", inplace=True)

    lag_epiweek = max_epiweek - timedelta(weeks=lag)

    # -------------------------------------------------------------------------
    # Plot
    # -------------------------------------------------------------------------

    for plot in plot_dict:

        plot_df = plot_dict[plot]["df"]

        x = "epiweek"
        label = plot
        legend_title = plot_dict[plot]["legend_title"]
        out_path = os.path.join(outdir, label)

        # Save plotting dataframe to file
        # for the largest, we need to replace the slashes in the filename
        if label == "largest":
            out_path += "_{lineage}".format(lineage=largest_lineage)

        plot_df.to_csv(out_path + ".tsv", sep="\t", index=False)

        # ---------------------------------------------------------------------
        # Sort categories by count

        # The df is sorted by time (epiweek)
        # But we want colors to be sorted by number of sequences
        df_count_dict = {}
        for col in plot_df.columns:
            if col == "epiweek":
                continue
            df_count_dict[col] = sum([c for c in plot_df[col] if not np.isnan(c)])

        # Sort by counts
        df_count_dict = dict(
            sorted(df_count_dict.items(), key=lambda item: item[1], reverse=True)
        )
        # Reorder the columns in the data frame
        cols = list(df_count_dict.keys())

        # Place Unknown at the end, for better color palettes
        if "Unknown" in cols:
            cols.remove("Unknown")
            ordered_cols = cols + ["Unknown"] + ["epiweek"]
        else:
            ordered_cols = cols + ["epiweek"]

        plot_df = plot_df[ordered_cols]

        # ---------------------------------------------------------------------
        # Dynamically create the color palette

        num_cat = len(plot_df.columns) - 1

        plot_palette = categorical_palette(num_cat=num_cat)

        # Recolor unknown
        if "Unknown" in plot_df.columns:
            unknown_i = list(plot_df.columns).index("Unknown")
            plot_palette[unknown_i] = list(UNKNOWN_RGB)

        # Setup up Figure
        fig, ax = plt.subplots(1, figsize=FIGSIZE, dpi=DPI)

        # ---------------------------------------------------------------------
        # Stacked bar charts

        # Check if we dropped all records
        if len(plot_df.columns) <= 1:
            error_msg = (
                "WARNING: No records to plot between"
                + " {min_epiweek} and {max_epiweek} for dataframe: {plot}".format(
                    plot=plot,
                    min_epiweek=min_epiweek,
                    max_epiweek=max_epiweek,
                )
            )
            print(error_msg, file=sys.stderr)
            # Add dummy data to force an empty plot
            plot_df["dummy"] = [None] * len(plot_df)
            plot_df.at[one_week_prev, "epiweek"] = one_week_prev
            plot_df.at[one_week_prev, "dummy"] = 1
            plot_df.sort_values(by="epiweek", inplace=True)

            plot_palette = categorical_palette(num_cat=1)

        plot_df.plot.bar(
            stacked=True,
            ax=ax,
            x=x,
            color=plot_palette,
            edgecolor="none",
            width=WIDTH_BAR,
            alpha=ALPHA_BAR,
        )

        # ---------------------------------------------------------------------
        # Axis limits

        xlim = ax.get_xlim()
        # If plotting 16 weeks, the x-axis will be (-0.625, 16.625)
        # If we added dummy data, need to correct start date
        x_start = xlim[1] - weeks - 1.25
        ax.set_xlim(x_start, xlim[1])

        if max_epiweek_sequences == 0:
            ylim = [0, 1]
        else:
            ylim = [0, round(max_epiweek_sequences * EPIWEEK_MAX_BUFF_FACTOR, 1)]
        ax.set_ylim(ylim[0], ylim[1])

        # ---------------------------------------------------------------------
        # Reporting Lag

        # If the scope of the data is smaller than the lag
        if lag_epiweek in epiweek_map:
            lag_i = epiweek_map[lag_epiweek]
        else:
            lag_i = epiweek_map[max_epiweek]

        lag_rect_height = ylim[1]

        # If we had to use dummy data for an empty dataframe, shift lag by 1
        if "dummy" in plot_df.columns:
            lag_i += 1

        ax.axvline(x=lag_i + (1 - (WIDTH_BAR) / 2), color="black", linestyle="--", lw=1)
        lag_rect_xy = [lag_i + (1 - (WIDTH_BAR) / 2), 0]
        lag_rect = patches.Rectangle(
            xy=lag_rect_xy,
            width=lag + (1 - (WIDTH_BAR) / 2),
            height=lag_rect_height,
            linewidth=1,
            edgecolor="none",
            facecolor="grey",
            alpha=ALPHA_LAG,
            zorder=0,
        )
        ax.add_patch(lag_rect)

        # Label the lag rectangle
        text_props = dict(facecolor="white")
        ax.text(
            x=lag_rect_xy[0],
            y=ylim[1] / 2,
            s="Reporting Lag",
            fontsize=6,
            fontweight="bold",
            rotation=90,
            bbox=text_props,
            va="center",
            ha="center",
        )

        # ---------------------------------------------------------------------
        # Legend

        # Dynamically set the number of columns in the legend based on how
        # how much space the labels will take up (in characters)
        max_char_len = 0
        for col in ordered_cols:
            if len(col) >= max_char_len:
                max_char_len = len(col)

        legend_ncol = math.floor(LEGEND_CHAR_WIDTH / max_char_len)
        # we don't want too many columns
        if legend_ncol > LEGEND_MAX_COL:
            legend_ncol = LEGEND_MAX_COL
        elif legend_ncol > num_cat:
            legend_ncol = num_cat

        legend = ax.legend(
            title=legend_title.title(),
            edgecolor="black",
            fontsize=LEGEND_FONTSIZE,
            ncol=legend_ncol,
            loc="lower center",
            mode="expand",
            bbox_to_anchor=(0, 1.02, 1, 0.2),
            borderaxespad=0,
        )

        # Truncate long labels in the legend
        # But only if this plots does not involve plotting parents!
        # Because we need to see the 2+ parent listed at the end
        if "parents" not in label:
            for i in range(0, len(legend.get_texts())):

                l_label = legend.get_texts()[i].get_text()

                if len(l_label) > LEGEND_LABEL_MAX_LEN:
                    l_label = l_label[0:LEGEND_LABEL_MAX_LEN]
                    if "(" in l_label and ")" not in l_label:
                        l_label = l_label + "...)"
                    else:
                        l_label = l_label + "..."

                legend.get_texts()[i].set_text(l_label)

        legend.get_frame().set_linewidth(1)
        legend.get_title().set_fontweight("bold")

        # If dummy is a column, there were no records and added fake data for plot
        if "dummy" in plot_df.columns:
            legend.remove()

        # ---------------------------------------------------------------------
        # Axes

        xlim = ax.get_xlim()
        # If plotting 16 weeks, the x-axis will be (-0.625, 16.625)
        # If we added dummy data, need to correct start date
        x_start = xlim[1] - weeks - 1.25
        ax.set_xlim(x_start, xlim[1])
        ax.set_ylim(ylim[0], ylim[1])
        ax.set_ylabel("Number of Sequences", fontweight="bold")
        ax.set_xlabel("Start of Week", fontweight="bold")
        # ax.xaxis.set_label_coords(0.5, -0.30)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha="center", fontsize=6)

        plt.tight_layout()
        plt.savefig(out_path + ".png")
        plt.savefig(out_path + ".svg")


if __name__ == "__main__":
    main()
