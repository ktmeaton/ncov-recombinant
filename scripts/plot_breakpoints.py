#!/usr/bin/env python3

import click
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import patches, colors, lines, collections
from functions import categorical_palette

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

    # Store data for plotting breakpoint distributions
    breakpoints_dist_data = {
        "coordinate": [],
        "parent": [],
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
                breakpoint_mean_coord = round(
                    (breakpoint_start_coord + breakpoint_end_coord) / 2
                )

                # Give this coordinate to both parents
                parent_next = parents_split[i + 1]
                if parent_next == NO_DATA_CHAR:
                    parent_next = "Unknown"

                breakpoints_dist_data["parent"].append(parent)
                breakpoints_dist_data["parent"].append(parent_next)
                breakpoints_dist_data["coordinate"].append(breakpoint_mean_coord)
                breakpoints_dist_data["coordinate"].append(breakpoint_mean_coord)

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
    breakpoints_dist_df = pd.DataFrame(breakpoints_dist_data)

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

    # Number of axes will vary depending on how many clades there are
    # Because on top, there will be a separate distribution for each clade

    num_dist_plots = 0
    for parent in parents_colors:
        # Skip plotting breakpoints of unknown parents
        if parent == "Unknown":
            continue
        match_df = breakpoints_dist_df[breakpoints_dist_df["parent"] == parent]

        # If there are breakpoints for that parent, add it to the dist plots
        if len(match_df) > 0:
            num_dist_plots += 1

    # I want the breakpoints subplot to be twice as big as the dist plots area
    if num_dist_plots > 0:
        height_ratios = [1] * num_dist_plots + [num_dist_plots * 2]
    else:
        height_ratios = [1]

    if autoscale and num_dist_plots > 0:
        figsize = [figsize[0], 1 * num_dist_plots]

    fig, axes = plt.subplots(
        num_dist_plots + 1,
        1,
        dpi=DPI,
        figsize=figsize,
        gridspec_kw={"height_ratios": height_ratios},
        sharex=True,
    )

    # -------------------------------------------------------------------------
    # Plot Breakpoint Distribution

    parents_seen = []
    i = 0

    for parent in list(breakpoints_dist_df["parent"]):
        if parent == "breakpoint" or parent == "Unknown":
            continue
        if parent in parents_seen:
            continue
        else:
            parents_seen.append(parent)

        ax = axes[i]
        color = parents_colors[parent]
        breakpoints_dist_parent_df = breakpoints_dist_df[
            breakpoints_dist_df["parent"] == parent
        ]
        # Is there only one coordinate observation?
        num_breakpoints_coord = len(set(breakpoints_dist_parent_df["coordinate"]))
        if num_breakpoints_coord == 1:
            # Double the dataframe to force plotting
            breakpoints_dist_parent_df = pd.concat(
                [
                    breakpoints_dist_parent_df,
                    breakpoints_dist_parent_df,
                ],
                ignore_index=True,
            )
            breakpoints_dist_parent_df.at[1, "coordinate"] = -9999

        sns.kdeplot(
            ax=ax,
            data=breakpoints_dist_parent_df,
            x="coordinate",
            bw_adjust=0.1,
            fill=True,
            hue="parent",
            palette=[color],
            alpha=1,
            edgecolor="black",
            linewidth=0.5,
        )

        ax.set_yticks([])
        ax.set_ylabel("")
        ax.legend().remove()

        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)

        i += 1

    # Label the last axes
    if num_dist_plots > 0:
        # Put the label on the halfway axes
        ax = axes[num_dist_plots // 2]
        ax.set_ylabel("Breakpoint\nDistribution")

    # -------------------------------------------------------------------------
    # Plot Breakpoint Regions
    if num_dist_plots > 0:
        ax = axes[-1]
    else:
        ax = axes

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

    legend = ax.legend(
        handles=legend_handles,
        labels=legend_labels,
        title=parent_type.title(),
        bbox_to_anchor=[1.02, 1.01],
    )

    frame = legend.get_frame()
    frame.set_linewidth(1)
    frame.set_edgecolor("black")
    frame.set_boxstyle("Square", pad=0.2)

    # -------------------------------------------------------------------------
    # Export

    # plt.suptitle("Recombination Breakpoints by Lineage")
    if num_dist_plots > 0:
        plt.tight_layout()
        plt.subplots_adjust(hspace=0)

    outpath = os.path.join(outdir, "breakpoints_{}".format(parent_type))
    breakpoints_df.to_csv(outpath + ".tsv", sep="\t", index=False)
    plt.savefig(outpath + ".png")
    plt.savefig(outpath + ".svg")


if __name__ == "__main__":
    main()
