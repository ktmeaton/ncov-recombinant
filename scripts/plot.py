#!/usr/bin/env python3
import click
import os
import pandas as pd
import numpy as np
import epiweeks
import matplotlib.pyplot as plt
from matplotlib import patches, cm
from datetime import datetime, timedelta
import sys
import copy

NO_DATA_CHAR = "NA"
ALPHA_LAG = 0.25
ALPHA_BAR = 1.00
WIDTH_BAR = 0.75
# This is the aspect ratio/dpi for ppt embeds
DPI = 200
FIGSIZE = [7, 5]
EPIWEEK_MAX_BUFF_FACTOR = 1.1


@click.command()
@click.option("--linelist", help="Recombinant sequences (TSV)", required=True)
@click.option("--outdir", help="Output directory", required=False, default=".")
@click.option(
    "--weeks", help="Number of weeks in retrospect to plot", required=False, default=16
)
@click.option(
    "--min-date", help="Ignore sequences before this date (yyyy-mm-dd, overrides --weeks)", required=False
)
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
    "--singletons", help="Flag to indicate singleton clusters (N=1) should be reported.", is_flag=True,
)
def main(
    linelist,
    outdir,
    weeks,
    geo,
    lag,
    min_date,
    singletons,
):
    """Plot recombinant lineages"""

    # Creat output directory if it doesn't exist
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # -------------------------------------------------------------------------
    # Import dataframes
    linelist_df = pd.read_csv(linelist, sep="\t")

    # Add datetime columns
    linelist_df["datetime"] = pd.to_datetime(linelist_df["date"], format="%Y-%m-%d")
    linelist_df["year"] = [d.year for d in linelist_df["datetime"]]
    linelist_df["epiweek"] = [
        epiweeks.Week.fromdate(d, system="iso").startdate()
        for d in linelist_df["datetime"]
    ]

    # Filter on weeks reporting
    max_epiweek = epiweeks.Week.fromdate(datetime.today(), system="iso").startdate()

    if min_date:
        min_datetime = datetime.strptime(min_date, "%Y-%m-%d")
        min_epiweek = epiweeks.Week.fromdate(min_datetime, system="iso").startdate()
    else:
        min_epiweek = max_epiweek - timedelta(weeks=weeks)
    
    weeks = int((max_epiweek - min_epiweek).days / 7)

    # Dummy data outside of plotting range when empty
    one_week_prev = min_epiweek - timedelta(weeks=1)

    linelist_df = copy.deepcopy(linelist_df[linelist_df["epiweek"] >= min_epiweek])    

    # Change status to title case
    linelist_df["status"] = [s.title() for s in linelist_df["status"]]

    # Get largest cluster
    largest_cluster_id = NO_DATA_CHAR
    largest_cluster_size = 0
    largest_lineage = NO_DATA_CHAR

    # All record cluster sizes to decided if singletons should be dropped
    drop_singleton_ids = []

    for cluster_id in set(linelist_df["cluster_id"]):
        cluster_df = linelist_df[linelist_df["cluster_id"] == cluster_id]
        cluster_size = len(cluster_df)
        if cluster_size >= largest_cluster_size:
            largest_cluster_id = cluster_id
            largest_lineage = cluster_df["lineage"].values[0]

        if not cluster_size == 1:
            for i in cluster_df.index:
                drop_singleton_ids.append(i)

    # now decided if we should drop singletons
    if not singletons:
        linelist_df.drop(labels=drop_singleton_ids, axis="rows", inplace=True)

    # Make NA parents "Unknown"
    linelist_df["parents"] = linelist_df["parents"].fillna("Unknown")

    # -------------------------------------------------------------------------
    # Pivot Tables
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # All
    all_df = pd.pivot_table(
        data=linelist_df.sort_values(by="epiweek"),
        values="strain",
        index=["epiweek"],
        aggfunc="count",
    )
    all_df.index.name = None
    all_df.fillna(0, inplace=True)
    all_df["epiweek"] = all_df.index
    all_df.rename(columns={"strain": "sequences"}, inplace=True)
    max_epiweek_sequences = max(all_df["sequences"])

    # Attempt to dynamically create pivot tables
    plot_dict = {
        "lineage"    : {"legend_title" : "lineage", "cols" : ["recombinant_lineage_curated"], "y": "recombinant_lineage_curated"},
        "status"     : {"legend_title" : "status",  "cols" : ["status"]},
        "geography"  : {"legend_title" : geo,       "cols" : [geo]},
        "largest"    : {"legend_title" : geo,       "cols" : [geo], "filter" : "cluster_id", "value" : largest_cluster_id},
        "designated" : {"legend_title" : "lineage", "cols": ["lineage"], "filter" : "status", "value" : "Designated"},
        "parents"    : {"legend_title" : "parents", "cols": ["parents"]},
    }

    for plot in plot_dict:
        columns = plot_dict[plot]["cols"]

        # Several plots need special filtering
        if "filter" in plot_dict[plot]:
            filter  = plot_dict[plot]["filter"]
            value  = plot_dict[plot]["value"]

            df = pd.pivot_table(
                data=linelist_df[linelist_df[filter] == value].sort_values(by="epiweek"),
                values="strain",
                index=["epiweek"],
                columns=columns,
                aggfunc="count",
            )

        # Otherwise no filtering required
        else:
            df = pd.pivot_table(
                data=linelist_df.sort_values(by="epiweek"),
                index=["epiweek"],        
                values="strain",
                aggfunc="count",
                columns=columns,
            )            

        df.index.name = None
        df.fillna(0, inplace=True)
        df["epiweek"] = df.index

        plot_dict[plot]["df"] = df

    # -------------------------------------------------------------------------
    # Filter for Reporting Period
    # -------------------------------------------------------------------------

    # Add empty data for weeks if needed
    epiweek_map = {}
    iter_week = min_epiweek
    iter_i = 0
    df_list = [plot_dict[plot]["df"] for plot in plot_dict]
    while iter_week <= max_epiweek:

        for df in df_list:

            if iter_week not in df["epiweek"]:
                df.at[iter_week, "epiweek"] = iter_week

        # Check if its the largest
        epiweek_map[iter_week] = iter_i
        iter_week += timedelta(weeks=1)
        iter_i += 1

    for df in df_list:
        df.sort_values(by="epiweek", axis="index", inplace=True)

    lag_epiweek = max_epiweek - timedelta(weeks=lag)
    lag_i = epiweek_map[lag_epiweek]

    # -------------------------------------------------------------------------
    # Plot

    for plot in plot_dict:


        df = plot_dict[plot]["df"]     

        x = "epiweek"
        label = plot
        legend_title = plot_dict[plot]["legend_title"]
        out_path = os.path.join(outdir, label)

        # Save plotting dataframe to file
        # for the largest, we also include the lineage and cluster_id in the file name
        if label == "largest":
            out_path += "_{lineage}_{cluster_id}".format(
                lineage=largest_lineage,
                cluster_id=largest_cluster_id,
            )
        df.to_csv(out_path + ".tsv", sep="\t", index=False)

        # Use the tab20 color palette
        if len(df.columns) > 20:
            print(
                "WARNING: {} dataframe has more than 20 categories".format(label),
                file=sys.stderr,
            )

        legend_ncol = 1
        if len(df.columns) > 10:
            legend_ncol = 2

        custom_cmap_i = np.linspace(0.0, 1.0, 20)
        df_cmap = cm.get_cmap("tab20")(custom_cmap_i)

        # The df is sorted by time (epiweek)
        # But we want colors to be sorted by number of sequences
        df_count_dict = {}
        for col in df.columns:
            if col == "epiweek":
                continue
            df_count_dict[col] = sum([c for c in df[col] if not np.isnan(c)])

        # Sort by counts
        df_count_dict = dict(
            sorted(df_count_dict.items(), key=lambda item: item[1], reverse=True)
        )
        # Reorder the columns in the data frame
        ordered_cols = list(df_count_dict.keys()) + ["epiweek"]
        df = df[ordered_cols]

        # Setup up Figure
        fig, ax = plt.subplots(1, figsize=FIGSIZE, dpi=DPI)

        # Check if we dropped all records
        if len(df.columns) <= 1:
            print(
                "WARNING: No records to plot between {min_epiweek} and {max_epiweek} for dataframe: {plot}".format(
                    plot=plot, min_epiweek=min_epiweek, max_epiweek=max_epiweek,), 
                file=sys.stderr
            )
            # Add dummy data to force an empty plot
            df["dummy"] = [None] * len(df)
            df.at[one_week_prev, "epiweek"] = one_week_prev
            df.at[one_week_prev, "dummy"] = 1
            df.sort_values(by="epiweek", inplace=True)


        df.plot.bar(
            stacked=True,
            ax=ax,
            x=x,
            color=df_cmap,
            edgecolor="black",
            width=WIDTH_BAR,
            alpha=ALPHA_BAR,
        )
        
        # Plot the reporting lag
        ax.axvline(x=lag_i + (1 - (WIDTH_BAR) / 2), color="black", linestyle="--", lw=1)
        lag_rect = patches.Rectangle(
            xy=[lag_i + (1 - (WIDTH_BAR) / 2), 0],
            width=lag + (1 - (WIDTH_BAR) / 2),
            height=len(linelist_df),
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

        ax.set_ylim(0, round(max_epiweek_sequences * EPIWEEK_MAX_BUFF_FACTOR, 1))

        legend = ax.legend(
            title=legend_title.title(), edgecolor="black", fontsize=8, ncol=legend_ncol, loc = "upper right"
        )

        legend.get_frame().set_linewidth(1)
        legend.get_title().set_fontweight("bold")

        # If dummy is a column, there were no records and added fake data for plot
        if "dummy" in df.columns:
            legend.remove()

        plt.savefig(out_path + ".png", bbox_inches="tight")
        plt.savefig(out_path + ".svg", bbox_inches="tight")

if __name__ == "__main__":
    main()
