#!/usr/bin/env python3

import click
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import patches, colors, lines
from functions import categorical_palette

print(categorical_palette)

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
@click.option("--cluster-col", help="Column name of cluster ID", required=False)
@click.option(
    "--autoscale",
    help="Autoscale plot dimensions to the number of lineages",
    is_flag=True,
)
def main(
    lineages,
    outdir,
    parent_col,
    breakpoint_col,
    cluster_col,
    parent_type,
    autoscale,
):
    """Plot recombinant lineage breakpoints"""

    # Creat output directory if it doesn't exist
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # -------------------------------------------------------------------------
    # Import dataframe
    lineages_df = pd.read_csv(lineages, sep="\t")
    lineages_df.fillna(NO_DATA_CHAR, inplace=True)

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

    for rec in lineages_df.iterrows():
        lineage = rec[1]["lineage"]

        if cluster_col:
            cluster_id = rec[1][cluster_col]
            lineage = "{} {}".format(lineage, cluster_id)

        parents = rec[1][parent_col]
        breakpoints = rec[1][breakpoint_col]

        parents_split = parents.split(",")
        breakpoints_split = breakpoints.split(",")

        prev_start_coord = 0

        for i in range(0, len(parents_split)):
            parent = parents_split[i]
            if parent not in parents_colors:
                parents_colors[parent] = ""

            if i < (len(parents_split) - 1):
                breakpoint = breakpoints_split[i]
                breakpoint_start_coord = int(breakpoint.split(":")[0])
                breakpoint_end_coord = int(breakpoint.split(":")[1])
                breakpoint_mean_coord = round(
                    (breakpoint_start_coord + breakpoint_end_coord) / 2
                )

                # Give this coordinate to both parents
                parent_next = parents_split[i + 1]
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
            parents_colors["Unknown"] = UNKNOWN_COLOR
            continue

        color_rgb = parents_palette[i]
        color = colors.to_hex(color_rgb)
        parents_colors[parent] = color
        i += 1

    parents_colors["breakpoint"] = BREAKPOINT_COLOR

    # -------------------------------------------------------------------------
    # Plot Setup

    # Number of axes will vary depending on how many clades there are
    # Because on top, there will be a separate distribution for each clade

    num_dist_plots = 0
    for parent in parents_colors:
        match_df = breakpoints_dist_df[breakpoints_dist_df["parent"] == parent]

        # If there are breakpoints for that parent, add it to the dist plots
        if len(match_df) > 0:
            num_dist_plots += 1

    # I want the breakpoints subplot to be twice as big as the dist plots area
    height_ratios = [1] * num_dist_plots + [num_dist_plots * 2]

    if autoscale:
        figsize = [FIGSIZE[0], 1 * num_dist_plots]
    else:
        figsize = FIGSIZE

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
        if parent == "breakpoint":
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

        # Is there only one observation?
        if len(breakpoints_dist_parent_df) == 1:
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

    # -------------------------------------------------------------------------
    # Plot Breakpoint Regions

    ax = axes[-1]

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
        y_tick_labs_lineage.append(lineage_label)

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
    ax.set_yticklabels(y_tick_labs_lineage, fontsize=y_tick_fontsize)

    # Axis Labels
    ax.set_ylabel("Lineage")
    ax.set_xlabel("Genomic Coordinate")

    # -------------------------------------------------------------------------
    # Vertical lines every 5000 nuc

    for ax in axes:
        for coord in range(COORD_ITER, GENOME_LENGTH, COORD_ITER):
            ax.axvline(x=coord, linestyle="--", linewidth=0.5, color="black", alpha=0.5)

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

    legend = ax.legend(
        handles=legend_handles,
        labels=legend_labels,
        title=parent_type.title(),
        bbox_to_anchor=[1.01, 1.01],
    )
    frame = legend.get_frame()
    frame.set_linewidth(1)
    frame.set_edgecolor("black")
    frame.set_boxstyle("Square", pad=0.2)

    # -------------------------------------------------------------------------
    # Export

    # plt.suptitle("Recombination Breakpoints by Lineage")
    plt.tight_layout()
    plt.subplots_adjust(hspace=0)
    outpath = os.path.join(outdir, "breakpoints_{}".format(parent_type))
    breakpoints_df.to_csv(outpath + ".tsv", sep="\t", index=False)
    plt.savefig(outpath + ".png")
    plt.savefig(outpath + ".svg")


if __name__ == "__main__":
    main()
