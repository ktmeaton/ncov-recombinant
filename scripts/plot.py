#!/usr/bin/env python3
import click
import os
import pandas as pd
import numpy as np
import epiweeks
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import patches, colors, lines
from datetime import datetime, timedelta
import sys
import copy
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

# Breakpoint Plotting
GENOME_LENGTH = 29903
BREAKPOINT_COLOR = "lightgrey"
X_BUFF = 1000
BREAKPOINT_COLOR = "lightgrey"

# Select and rename columns from linelist
LINEAGES_COLS = [
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

plt.rcParams["svg.fonttype"] = "none"


def categorical_cmap(nc, nsc, cmap="tab20", continuous=False):
    """
    Author: ImportanceOfBeingEarnest
    Link: https://stackoverflow.com/a/47232942
    """
    if nc > plt.get_cmap(cmap).N:
        raise ValueError("Too many categories for the specified colormap.")
    if continuous:
        ccolors = plt.get_cmap(cmap)(np.linspace(0, 1, nc))
    else:
        ccolors = plt.get_cmap(cmap)(np.arange(nc, dtype=int))
    cols = np.zeros((nc * nsc, 3))
    for i, c in enumerate(ccolors):
        chsv = colors.rgb_to_hsv(c[:3])
        arhsv = np.tile(chsv, nsc).reshape(nsc, 3)
        arhsv[:, 1] = np.linspace(chsv[1], 0.25, nsc)
        arhsv[:, 2] = np.linspace(chsv[2], 1, nsc)
        rgb = colors.hsv_to_rgb(arhsv)
        cols[i * nsc : (i + 1) * nsc, :] = rgb
    cmap = colors.ListedColormap(cols)
    return cmap


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
        epiweeks.Week.fromdate(d, system="iso").startdate() for d in df["datetime"]
    ]

    # Filter on weeks reporting
    if max_date:
        max_datetime = datetime.strptime(max_date, "%Y-%m-%d")
        max_epiweek = epiweeks.Week.fromdate(max_datetime, system="iso").startdate()
    else:
        max_epiweek = epiweeks.Week.fromdate(datetime.today(), system="iso").startdate()

    if min_date:
        min_datetime = datetime.strptime(min_date, "%Y-%m-%d")
        min_epiweek = epiweeks.Week.fromdate(min_datetime, system="iso").startdate()
    elif weeks:
        weeks = int(weeks)
        min_epiweek = max_epiweek - timedelta(weeks=(weeks - 1))
    elif len(df) == 0:
        # Just need something for empty plots
        min_epiweek = max_epiweek - timedelta(weeks=16)
    else:
        min_epiweek = epiweeks.Week.fromdate(
            min(df["epiweek"]), system="iso"
        ).startdate()

    weeks = int((max_epiweek - min_epiweek).days / 7)

    # Dummy data outside of plotting range when empty
    one_week_prev = min_epiweek - timedelta(weeks=1)

    df = copy.deepcopy(
        df[(df["epiweek"] >= min_epiweek) & (df["epiweek"] <= max_epiweek)]
    )

    # Change status to title case
    df["status"] = [s.title() for s in df["status"]]

    # Get largest cluster
    largest_cluster_id = NO_DATA_CHAR
    largest_cluster_size = 0
    largest_lineage = NO_DATA_CHAR

    # All record cluster sizes to decided if singletons should be dropped
    drop_singleton_ids = []

    for cluster_id in set(df["cluster_id"]):
        cluster_df = df[df["cluster_id"] == cluster_id]
        cluster_size = len(cluster_df)
        if cluster_size >= largest_cluster_size:
            largest_cluster_id = cluster_id
            largest_lineage = cluster_df["lineage"].values[0]
            largest_cluster_size = cluster_size

        if cluster_size == 1:
            for i in cluster_df.index:
                drop_singleton_ids.append(i)

    # now decided if we should drop singletons
    if not singletons:
        df.drop(labels=drop_singleton_ids, axis="rows", inplace=True)

    # Make NA parents "Unknown"
    df["parents"] = df["parents"].fillna("Unknown")

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
            "filter": "cluster_id",
            "value": largest_cluster_id,
        },
        "designated": {
            "legend_title": "lineage",
            "cols": ["lineage"],
            "filter": "status",
            "value": "Designated",
        },
        "parents": {"legend_title": "parents", "cols": ["parents"]},
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

    for plot in plot_dict:

        plot_df = plot_dict[plot]["df"]

        x = "epiweek"
        label = plot
        legend_title = plot_dict[plot]["legend_title"]
        out_path = os.path.join(outdir, label)

        # Save plotting dataframe to file
        # for the largest, we also include the lineage and cluster_id in the file name
        if label == "largest":
            out_path += "_{lineage}_{cluster_id}".format(
                lineage=largest_lineage,
                cluster_id=largest_cluster_id.replace("/", "-DELIM-"),
            )

        plot_df.to_csv(out_path + ".tsv", sep="\t", index=False)

        # Use the tab20 color palette
        num_cat = len(plot_df.columns)

        legend_ncol = 1
        if num_cat > 10:
            legend_ncol = 2

        pal = "tab10"
        # Exclude the last color in tab10, which is a light blue
        pal_num_cat = 9
        pal_num_sub_cat = 1

        custom_cmap_i = np.linspace(0.0, 1.0, pal_num_cat)

        if num_cat > pal_num_cat:
            print(
                "WARNING: {} dataframe has more than {} categories".format(
                    label, pal_num_cat
                ),
                file=sys.stderr,
            )
            # Determine subcategories
            pal_num_sub_cat = math.ceil(num_cat / pal_num_cat)
            custom_cmap_i = np.linspace(0.0, 1.0, num_cat)

        df_cmap = categorical_cmap(pal_num_cat, pal_num_sub_cat, cmap=pal)(
            custom_cmap_i
        )

        # df_cmap = cm.get_cmap(pal)(custom_cmap_i)

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
        ordered_cols = list(df_count_dict.keys()) + ["epiweek"]
        plot_df = plot_df[ordered_cols]

        # Setup up Figure
        fig, ax = plt.subplots(1, figsize=FIGSIZE, dpi=DPI)

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

        plot_df.plot.bar(
            stacked=True,
            ax=ax,
            x=x,
            color=df_cmap,
            edgecolor="none",
            width=WIDTH_BAR,
            alpha=ALPHA_BAR,
        )

        # Plot the reporting lag
        lag_i = epiweek_map[lag_epiweek]
        lag_rect_height = len(df)

        # If we had to use dummy data for an empty dataframe, shift lag by 1
        if "dummy" in plot_df.columns:
            lag_i += 1
            lag_rect_height = 1

        ax.axvline(x=lag_i + (1 - (WIDTH_BAR) / 2), color="black", linestyle="--", lw=1)
        lag_rect = patches.Rectangle(
            xy=[lag_i + (1 - (WIDTH_BAR) / 2), 0],
            width=lag + (1 - (WIDTH_BAR) / 2),
            height=lag_rect_height,
            linewidth=1,
            edgecolor="none",
            facecolor="grey",
            alpha=ALPHA_LAG,
            zorder=0,
        )

        ax.add_patch(lag_rect)
        footnote = (
            "The grey area indicates an approximate reporting"
            + " lag of {} weeks.".format(lag)
        )
        ax.text(
            x=0,
            y=-0.45,
            s=footnote,
            transform=ax.transAxes,
            fontsize=8,
        )

        xlim = ax.get_xlim()
        # If plotting 16 weeks, the x-axis will be (-0.625, 16.625)
        # If we added dummy data, need to correct start date
        x_start = xlim[1] - weeks - 1.25
        ax.set_xlim(x_start, xlim[1])
        ax.set_ylabel("Number of Sequences", fontweight="bold")
        ax.set_xlabel("Start of Week", fontweight="bold")
        ax.xaxis.set_label_coords(0.5, -0.30)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha="center", fontsize=8)

        # Catch 0 records
        if max_epiweek_sequences == 0:
            ax.set_ylim(0, 1)
        else:
            ax.set_ylim(0, round(max_epiweek_sequences * EPIWEEK_MAX_BUFF_FACTOR, 1))

        # small df: upper right
        # large df: upper left
        legend_loc = "upper right"
        if len(plot_df) > 16:
            legend_loc = "upper left"
        legend = ax.legend(
            title=legend_title.title(),
            edgecolor="black",
            fontsize=8,
            ncol=legend_ncol,
            loc=legend_loc,
        )

        legend.get_frame().set_linewidth(1)
        legend.get_title().set_fontweight("bold")

        # If dummy is a column, there were no records and added fake data for plot
        if "dummy" in plot_df.columns:
            legend.remove()

        plt.tight_layout()
        plt.savefig(out_path + ".png")
        plt.savefig(out_path + ".svg")

    # -------------------------------------------------------------------------
    # Breakpoints
    # -------------------------------------------------------------------------

    # Create the lineages dataframe
    lineages_data = {col: [] for col in LINEAGES_COLS}
    lineages_data[geo] = []

    for cluster_id in set(df["cluster_id"]):

        match_df = df[df["cluster_id"] == cluster_id]

        earliest_date = min(match_df["datetime"])
        latest_date = max(match_df["datetime"])
        sequences = len(match_df)

        # TBD majority vote on disagreement
        lineages_data["cluster_id"].append(cluster_id)
        lineages_data["status"].append(match_df["status"].values[0])
        lineages_data["lineage"].append(match_df["lineage"].values[0])
        lineages_data["parents"].append(match_df["parents"].values[0])
        lineages_data["breakpoints"].append(match_df["breakpoints"].values[0])
        lineages_data["issue"].append(match_df["issue"].values[0])
        lineages_data["subtree"].append(match_df["subtree"].values[0])

        lineages_data["sequences"].append(sequences)
        lineages_data["earliest_date"].append(earliest_date)
        lineages_data["latest_date"].append(latest_date)

        geo_list = list(set(match_df[geo]))
        geo_list.sort()
        geo_counts = []
        for loc in geo_list:
            loc_df = match_df[match_df[geo] == loc]
            num_sequences = len(loc_df)
            geo_counts.append("{} ({})".format(loc, num_sequences))

        lineages_data[geo].append(", ".join(geo_counts))

        # Growth Calculation
        growth_score = 0
        duration = (latest_date - earliest_date).days + 1
        growth_score = round(sequences / duration, 2)
        lineages_data["growth_score"].append(growth_score)

    lineages_df = pd.DataFrame(lineages_data)
    lineages_df.sort_values(by="sequences", ascending=False, inplace=True)

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
        cluster_id = rec[1]["cluster_id"]

        lineage = "{} {}".format(lineage, cluster_id)

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

    fig, axes = plt.subplots(
        2,
        1,
        dpi=DPI,
        figsize=FIGSIZE,
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
    y_tick_labs_cluster = []

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
        cluster_id_label = lineage.split(" ")[1]
        y_tick_labs_lineage.append(lineage_label)
        y_tick_labs_cluster.append(cluster_id_label)

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
    if num_lineages >= 20:
        y_tick_fontsize = 8
    if num_lineages >= 30:
        y_tick_fontsize = 6
    if num_lineages >= 40:
        y_tick_fontsize = 4

    # Axis ticks
    ax.set_yticks(y_tick_locs)
    ax.set_yticklabels(y_tick_labs_lineage, fontsize=y_tick_fontsize)

    # ax2 = ax.twinx()
    # ax2.set_yticks(y_tick_locs)
    # ax2.set_yticklabels(y_tick_labs_cluster, fontsize=y_tick_fontsize)

    # Axis Labels
    ax.set_ylabel("Lineage")
    ax.set_xlabel("Genomic Coordinate")

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
        bbox_to_anchor=[1.01, 1.01],
    )
    frame = legend.get_frame()
    frame.set_linewidth(1)
    frame.set_edgecolor("black")
    frame.set_boxstyle("Square", pad=0.2)

    # -------------------------------------------------------------------------
    # Export

    plt.suptitle("Recombination Breakpoints by Lineage")
    plt.tight_layout()
    plt.subplots_adjust(hspace=0)
    outpath = os.path.join(outdir, "breakpoints")
    breakpoints_df.to_csv(outpath + ".tsv", sep="\t", index=False)
    plt.savefig(outpath + ".png")
    plt.savefig(outpath + ".svg")


if __name__ == "__main__":
    main()
