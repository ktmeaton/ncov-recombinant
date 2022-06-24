#!/usr/bin/env python3
import click
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import patches, colors, lines
import os

NO_DATA_CHAR = "NA"

DPI = 96 * 2
# Breakpoint Plotting
GENOME_LENGTH = 29903
BREAKPOINT_COLOR = "lightgrey"
X_BUFF = 1000
BREAKPOINT_COLOR = "lightgrey"

plt.rcParams["svg.fonttype"] = "none"


@click.command()
@click.option("--input", help="Input file", required=True)
@click.option(
    "--output",
    help="Output file",
    required=True,
)
@click.option("--figsize", help="Figure dimensions (length,width)", required=False)
def main(
    input,
    output,
    figsize,
):
    """Plot breakpoints"""

    # I need columns lineage, parent, start, end
    lineages_df = pd.read_csv(input, sep="\t")
    lineages_df.fillna(NO_DATA_CHAR, inplace=True)

    # Drop NA
    lineages_df = lineages_df[lineages_df["breakpoints"] != NO_DATA_CHAR]

    parent_colors = {}

    # Create a dataframe to hold plot data
    # Lineage (y axis, categorical)
    #

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

    # -------------------------------------------------------------------------
    # Create a dataframe to hold plot data

    for rec in lineages_df.iterrows():
        lineage = rec[1]["lineage"]
        parents = rec[1]["parents"]
        breakpoints = rec[1]["breakpoints"]

        parents_split = parents.split(",")
        breakpoints_split = breakpoints.split(",")

        prev_start_coord = 0

        for i in range(0, len(parents_split)):
            parent = parents_split[i]
            if parent not in parent_colors:
                parent_colors[parent] = ""

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

    # Sort by coordinates
    breakpoints_df.sort_values(by=["parent", "start", "end"], inplace=True)

    num_lineages = len(set(breakpoints_df["lineage"]))
    # -------------------------------------------------------------------------
    # Colors

    # tab10/Set1 should be a safe palette for now

    i = 0
    for parent in parent_colors:
        color_rgb = plt.cm.Set1.colors[i]
        color = colors.to_hex(color_rgb)
        i += 1

        parent_colors[parent] = color

    parent_colors["breakpoint"] = BREAKPOINT_COLOR

    # -------------------------------------------------------------------------
    # Plot Setup

    # Dynamically set figsize
    if not figsize:
        figsize_width = 12
        figsize_height = 1
        figsize = [figsize_width, (figsize_height * num_lineages) / 2]
    else:
        figsize_width = int(figsize.split(",")[0])
        figsize_height = int(figsize.split(",")[1])
        figsize = [figsize_width, figsize_height]

    fig, axes = plt.subplots(
        2,
        1,
        dpi=DPI,
        figsize=figsize,
        gridspec_kw={"height_ratios": [1, 5]},
        sharex=True,
    )

    # -------------------------------------------------------------------------
    # Plot Breakpoint Distribution

    ax = axes[0]

    breakpoints_dist_df = pd.DataFrame(breakpoints_dist_data)

    sns.kdeplot(
        ax=ax,
        data=breakpoints_dist_df,
        x="coordinate",
        bw_adjust=0.3,
        hue="parent",
        palette=parent_colors,
        multiple="stack",
        fill=True,
    )

    ax.set_yticks([])
    ax.set_ylabel("")
    ax.legend().remove()

    for spine in ax.spines:
        ax.spines[spine].set_visible(False)

    # -------------------------------------------------------------------------
    # Plot Breakpoint Regions

    ax = axes[1]

    rect_height = 1
    start_y = 0
    y_buff = 1
    y = start_y
    y_increment = rect_height + y_buff
    y_tick_locs = []
    y_tick_labs_lineage = []

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

            color = parent_colors[parent]

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
        0 - ((num_lineages * y_increment) - (y_increment / 2)), 0 + (rect_height * 2)
    )

    # This is the default fontisze to use
    y_tick_fontsize = 10

    # Axis ticks
    ax.set_yticks(y_tick_locs)
    ax.set_yticklabels(y_tick_labs_lineage, fontsize=y_tick_fontsize)

    # ax2 = ax.twinx()
    # ax2.set_yticks(y_tick_locs)
    # ax2.set_yticklabels(y_tick_labs_cluster, fontsize=y_tick_fontsize)

    # Axis Labels
    ax.set_ylabel("Lineage")
    ax.set_xlabel("Genomic Coordinate")

    # Title
    plt.suptitle("Recombination Breakpoints by Lineage")

    # -------------------------------------------------------------------------
    # Manually create legend

    legend_handles = []
    legend_labels = []

    for parent in parent_colors:
        handle = lines.Line2D([0], [0], color=parent_colors[parent], lw=4)
        label = parent.title()
        legend_handles.append(handle)
        legend_labels.append(label)

    legend = ax.legend(
        handles=legend_handles,
        labels=legend_labels,
        title="Parent",
        bbox_to_anchor=[1.01, 1.00],
    )
    frame = legend.get_frame()
    frame.set_linewidth(1)
    frame.set_edgecolor("black")
    frame.set_boxstyle("Square", pad=0.2)

    # -------------------------------------------------------------------------
    # Export

    plt.tight_layout()
    plt.subplots_adjust(hspace=0)
    plt.savefig(output)
    output_basename = os.path.splitext(output)[0]
    plt.savefig(output_basename + ".svg")


if __name__ == "__main__":
    main()
