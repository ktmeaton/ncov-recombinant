#!/usr/bin/env python3

import click
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import patches, colors, lines, collections
from functions import categorical_palette
import math

NO_DATA_CHAR = "NA"
# This is the aspect ratio/dpi for ppt embeds
# The dimensions are set in the powerpoint template (resources/template.pttx)
DPI = 96 * 2
FIGSIZE = [6.75, 5.33]
FIG_Y_PER_LINEAGE = 1

# Breakpoint Plotting
GENOME_LENGTH = 29903
X_BUFF = 1000
BREAKPOINT_COLOR = "lightgrey"
UNKNOWN_COLOR = "dimgrey"
COORD_ITER = 5000

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
@click.option("--lineages", help="Recombinant lineages (tsv)", required=True)
@click.option("--outdir", help="Output directory", required=False, default=".")
@click.option(
    "--lineage-col", help="Column name of lineage", required=False, default="lineage"
)
@click.option(
    "--breakpoint-col",
    help="Column name of breakpoints",
    required=False,
    default="breakpoints",
)
@click.option(
    "--parent-col", help="Column name of parents", required=False, default="parents"
)
@click.option(
    "--parent-type",
    help="Parent type (ex. clade, lineage)",
    required=False,
    default="clade",
)
@click.option(
    "--cluster-col", help="Column name of cluster ID (ex. cluster_id)", required=False
)
@click.option(
    "--clusters", help="Restrict plotting to only these cluster IDs", required=False
)
@click.option(
    "--figsize",
    help="Figure dimensions as h,w in inches (ex. 6.75,5.33)",
    default=",".join([str(d) for d in FIGSIZE]),
)
@click.option(
    "--autoscale",
    help="Autoscale plot dimensions to the number of lineages (overrides --figsize)",
    is_flag=True,
)
@click.option(
    "--positives",
    help="Table of positive recombinants",
    required=False,
)
def main(
    lineages,
    outdir,
    lineage_col,
    parent_col,
    breakpoint_col,
    cluster_col,
    clusters,
    parent_type,
    autoscale,
    figsize,
    positives,
):
    """Plot recombinant lineage breakpoints"""

    # Creat output directory if it doesn't exist
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # -------------------------------------------------------------------------
    # Import dataframes
    lineages_df = pd.read_csv(lineages, sep="\t")
    lineages_df.fillna(NO_DATA_CHAR, inplace=True)

    if cluster_col:

        lineages_df[cluster_col] = [str(c) for c in lineages_df[cluster_col]]
        # Filter dataframe on cluster IDs
        if clusters:
            clusters_list = clusters.split(",")
            lineages_df = lineages_df[lineages_df[cluster_col].isin(clusters_list)]

        # Which lineages have the same name but different cluster ID?
        lineages_seen = []
        lineages_dup = []
        for lineage in list(lineages_df[lineage_col]):
            if lineage not in lineages_seen:
                lineages_seen.append(lineage)
            else:
                lineages_dup.append(lineage)

    else:
        lineages_dup = []

    if positives:
        positives_df = pd.read_csv(positives, sep="\t")
        positives_df["strain"] = [str(s) for s in positives_df["strain"]]
        if cluster_col:
            positives_df[cluster_col] = [str(s) for s in positives_df[cluster_col]]
        positives_df.fillna(NO_DATA_CHAR, inplace=True)

    # Figsize format back to list
    figsize = [float(d) for d in figsize.split(",")]

    # -------------------------------------------------------------------------

    # Create a dataframe to hold plot data
    # Lineage (y axis, categorical)
    # Coordinate (x axis, numeric)

    breakpoints_data = {
        "lineage": [],
        "parent": [],
        "start": [],
        "end": [],
    }

    parents_colors = {}

    # -------------------------------------------------------------------------
    # Create a dataframe to hold plot data

    # Iterate through lineages
    for rec in lineages_df.iterrows():
        lineage = rec[1][lineage_col]

        if cluster_col:
            cluster_id = rec[1][cluster_col]
            lineage = "{} {}".format(lineage, cluster_id)

        parents = rec[1][parent_col]
        breakpoints = rec[1][breakpoint_col]

        parents_split = parents.split(",")
        breakpoints_split = breakpoints.split(",")

        prev_start_coord = 0

        # Iterate through the parents
        for i in range(0, len(parents_split)):
            parent = parents_split[i]

            # Convert NA parents to Unknown
            if parent == NO_DATA_CHAR:
                parent = "Unknown"
            if parent not in parents_colors:
                parents_colors[parent] = ""

            if i < (len(parents_split) - 1):
                breakpoint = breakpoints_split[i]
                # Check that we actually found a breakpoint
                if ":" not in breakpoint:
                    continue

                breakpoint_start_coord = int(breakpoint.split(":")[0])
                breakpoint_end_coord = int(breakpoint.split(":")[1])

                # Give this coordinate to both parents
                parent_next = parents_split[i + 1]
                if parent_next == NO_DATA_CHAR:
                    parent_next = "Unknown"

                start_coord = prev_start_coord
                end_coord = int(breakpoint.split(":")[0]) - 1
                # Update start coord
                prev_start_coord = int(breakpoint.split(":")[1]) + 1

                # Add record for breakpoint
                breakpoints_data["lineage"].append(lineage)
                breakpoints_data["parent"].append("breakpoint")
                breakpoints_data["start"].append(breakpoint_start_coord)
                breakpoints_data["end"].append(breakpoint_end_coord)

            else:
                start_coord = prev_start_coord
                end_coord = GENOME_LENGTH

            # Add record for parent
            breakpoints_data["lineage"].append(lineage)
            breakpoints_data["parent"].append(parent)
            breakpoints_data["start"].append(start_coord)
            breakpoints_data["end"].append(end_coord)

    # Convert the dictionary to a dataframe
    breakpoints_df = pd.DataFrame(breakpoints_data)

    # Sort by coordinates
    breakpoints_df.sort_values(by=["parent", "start", "end"], inplace=True)

    # -------------------------------------------------------------------------
    # Colors

    # Pick paletted based on number of parents
    parents_palette = categorical_palette(num_cat=len(parents_colors))

    i = 0

    for parent in parents_colors:
        if parent == "Unknown":
            # We'll sort this out after, so it will be at the end
            continue

        color_rgb = parents_palette[i]
        color = colors.to_hex(color_rgb)
        parents_colors[parent] = color
        i += 1

    # Reorder unknown parents to the end
    if "Unknown" in parents_colors:
        del parents_colors["Unknown"]
        parents_colors["Unknown"] = UNKNOWN_COLOR
    parents_colors["breakpoint"] = BREAKPOINT_COLOR

    # -------------------------------------------------------------------------
    # Plot Setup

    # When dynamically setting the aspect ratio, the height is
    # multiplied by the number of lineages
    num_lineages = len(set(list(breakpoints_df["lineage"])))
    if autoscale:
        # This is the minimum size it can be for 1 lineage with two parents
        figsize = [figsize[0], 2]
        # Adjusted for other sizes of lineages, mirrors fontsize detection later
        if num_lineages >= 40:
            figsize = [figsize[0], 0.1 * num_lineages]
        elif num_lineages >= 30:
            figsize = [figsize[0], 0.2 * num_lineages]
        elif num_lineages >= 20:
            figsize = [figsize[0], 0.3 * num_lineages]
        elif num_lineages >= 10:
            figsize = [figsize[0], 0.5 * num_lineages]
        elif num_lineages > 1:
            figsize = [figsize[0], 1 * num_lineages]

    fig, ax = plt.subplots(
        1,
        1,
        dpi=DPI,
        figsize=figsize,
    )

    # -------------------------------------------------------------------------
    # Plot Breakpoint Regions

    rect_height = 1
    start_y = 0
    y_buff = 1
    y = start_y
    y_increment = rect_height + y_buff
    y_tick_locs = []
    y_tick_labs_lineage = []

    num_lineages = len(set(breakpoints_df["lineage"]))
    lineages_seen = []

    # Iterate through lineages to plot
    for rec in breakpoints_df.iterrows():
        lineage = rec[1]["lineage"]
        if lineage in lineages_seen:
            continue
        lineages_seen.append(lineage)

        y_tick_locs.append(y + (rect_height / 2))
        lineage_label = lineage.split(" ")[0]
        if cluster_col:

            cluster_id_label = lineage.split(" ")[1]

        # Non-unique, use cluster ID in y axis
        if lineage_label in lineages_dup:
            ylabel = "{} ({})".format(lineage_label, cluster_id_label)
        else:
            ylabel = lineage_label

        y_tick_labs_lineage.append(ylabel)

        lineage_df = breakpoints_df[breakpoints_df["lineage"] == lineage]

        # Iterate through regions to plot
        for rec in lineage_df.iterrows():
            parent = rec[1]["parent"]
            start = rec[1]["start"]
            end = rec[1]["end"]

            color = parents_colors[parent]

            region_rect = patches.Rectangle(
                xy=[start, y],
                width=end - start,
                height=rect_height,
                linewidth=1,
                edgecolor="none",
                facecolor=color,
            )
            ax.add_patch(region_rect)

        # Iterate through substitutions to plot
        if positives:
            positive_rec = positives_df[(positives_df[lineage_col] == lineage_label)]
            # If we're using a cluster id col, further filter on that
            if cluster_col:
                positive_rec = positive_rec[
                    (positive_rec[cluster_col] == cluster_id_label)
                ]

            # Extract the substitutions, just taking the first as representative
            cov_spectrum_subs = list(positive_rec["cov-spectrum_query"])[0]

            if cov_spectrum_subs != NO_DATA_CHAR:
                # Split into a list, and extract coordinates
                coord_list = [int(s[1:-1]) for s in cov_spectrum_subs.split(",")]
                subs_lines = []
                # Create vertical bars for each sub
                for coord in coord_list:
                    sub_line = [(coord, y), (coord, y + rect_height)]
                    subs_lines.append(sub_line)
                # Combine all bars into a collection
                collection_subs = collections.LineCollection(
                    subs_lines, color="black", linewidth=0.25
                )
                # Add the subs bars to the plot
                ax.add_collection(collection_subs)

        # Jump to the next y coordinate
        y -= y_increment

    # Axis Limits
    ax.set_xlim(0 - X_BUFF, GENOME_LENGTH + X_BUFF)
    ax.set_ylim(
        0 - ((num_lineages * y_increment) - (y_increment / 2)),
        0 + (rect_height * 2),
    )

    # This is the default fontisze to use
    y_tick_fontsize = 10
    if num_lineages >= 20:
        y_tick_fontsize = 8
    if num_lineages >= 30:
        y_tick_fontsize = 6
    if num_lineages >= 40:
        y_tick_fontsize = 4

    # Axis ticks
    ax.set_yticks(y_tick_locs)

    # Truncate long labels
    for i in range(0, len(y_tick_labs_lineage)):

        y_label = y_tick_labs_lineage[i]

        if len(y_label) > LEGEND_LABEL_MAX_LEN:
            y_label = y_label[0:LEGEND_LABEL_MAX_LEN]
            if "(" in y_label and ")" not in y_label:
                y_label = y_label + "...)"
            else:
                y_label = y_label + "..."

        y_tick_labs_lineage[i] = y_label

    ax.set_yticklabels(y_tick_labs_lineage, fontsize=y_tick_fontsize)

    # Axis Labels
    ax.set_ylabel("Lineage")
    ax.set_xlabel("Genomic Coordinate")

    # -------------------------------------------------------------------------
    # Manually create legend

    legend_handles = []
    legend_labels = []

    for parent in parents_colors:
        handle = lines.Line2D([0], [0], color=parents_colors[parent], lw=4)
        legend_handles.append(handle)
        if parent == "breakpoint":
            legend_labels.append(parent.title())
        else:
            legend_labels.append(parent)

    subs_handle = lines.Line2D(
        [],
        [],
        color="black",
        marker="|",
        linestyle="None",
        markersize=10,
        markeredgewidth=1,
    )
    legend_handles.append(subs_handle)
    legend_labels.append("Substitution")

    # Dynamically set the number of columns in the legend based on how
    # how much space the labels will take up (in characters)
    max_char_len = 0
    for label in legend_labels:
        if len(label) >= max_char_len:
            max_char_len = len(label)

    legend_ncol = math.floor(LEGEND_CHAR_WIDTH / max_char_len)
    # we don't want too many columns
    if legend_ncol > LEGEND_MAX_COL:
        legend_ncol = LEGEND_MAX_COL
    elif legend_ncol > len(parents_colors):
        legend_ncol = len(parents_colors)

    legend = ax.legend(
        handles=legend_handles,
        labels=legend_labels,
        title=parent_type.title(),
        edgecolor="black",
        fontsize=LEGEND_FONTSIZE,
        ncol=legend_ncol,
        loc="lower center",
        mode="expand",
        bbox_to_anchor=(0, 1.02, 1, 0.2),
        borderaxespad=0,
        borderpad=1,
    )

    legend.get_frame().set_linewidth(1)
    legend.get_title().set_fontweight("bold")
    # legend.get_frame().set_boxstyle("Square", pad=0.2)

    # -------------------------------------------------------------------------
    # Export

    # plt.suptitle("Recombination Breakpoints by Lineage")
    if num_lineages > 0:
        plt.tight_layout()

    outpath = os.path.join(outdir, "breakpoints_{}".format(parent_type))
    breakpoints_df.to_csv(outpath + ".tsv", sep="\t", index=False)
    plt.savefig(outpath + ".png")
    plt.savefig(outpath + ".svg")


if __name__ == "__main__":
    main()
