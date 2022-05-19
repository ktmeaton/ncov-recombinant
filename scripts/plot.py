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

NO_DATA_CHAR = "NA"
ALPHA_LAG = 0.25
ALPHA_BAR = 1.00
WIDTH_BAR = 0.75
# This is the aspect ratio/dpi for ppt embeds
DPI = 200
FIGSIZE = [7, 4]
EPIWEEK_MAX_BUFF_FACTOR = 1.1


@click.command()
@click.option("--linelist", help="Recombinant sequences (TSV)", required=True)
@click.option("--recombinants", help="Recombinant lineages (TSV)", required=True)
@click.option("--outdir", help="Output directory", required=False, default=".")
@click.option(
    "--weeks", help="Number of weeks in retrospect to plot", required=False, default=16
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
def main(
    linelist,
    recombinants,
    outdir,
    weeks,
    geo,
    lag,
):
    """Plot recombinant lineages"""

    # -------------------------------------------------------------------------
    # Import dataframes
    linelist_df = pd.read_csv(linelist, sep="\t")
    recombinants_df = pd.read_csv(recombinants, sep="\t")

    # Add datetime columns
    linelist_df["datetime"] = pd.to_datetime(linelist_df["date"], format="%Y-%m-%d")
    linelist_df["year"] = [d.year for d in linelist_df["datetime"]]
    linelist_df["epiweek"] = [
        epiweeks.Week.fromdate(d, system="iso").startdate()
        for d in linelist_df["datetime"]
    ]

    # Change status to title case
    linelist_df["status"] = [s.title() for s in linelist_df["status"]]

    # Filter on weeks reporting
    max_epiweek = epiweeks.Week.fromdate(datetime.today(), system="iso").startdate()
    min_epiweek = max_epiweek - timedelta(weeks=weeks)
    linelist_df = linelist_df[linelist_df["epiweek"] >= min_epiweek]

    largest_i = recombinants_df["sequences"].idxmax()
    largest_cluster_id = recombinants_df["cluster_id"][largest_i]

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

    # -------------------------------------------------------------------------
    # Lineages
    lineage_df = pd.pivot_table(
        data=linelist_df.sort_values(by="epiweek"),
        values="strain",
        index=["epiweek"],
        columns=["recombinant_lineage_curated"],
        aggfunc="count",
    )
    lineage_df.index.name = None
    lineage_df.fillna(0, inplace=True)

    # Drop singletons
    drop_lineages = []
    for lineage in lineage_df.columns:
        total_sequences = sum(lineage_df[lineage])
        if total_sequences == 1 and not lineage.startswith("X"):
            drop_lineages.append(lineage)
    lineage_df.drop(labels=drop_lineages, axis="columns", inplace=True)

    lineage_df["epiweek"] = lineage_df.index

    # -------------------------------------------------------------------------
    # Status
    status_df = pd.pivot_table(
        data=linelist_df.sort_values(by="epiweek"),
        values="strain",
        index=["epiweek"],
        columns=["status"],
        aggfunc="count",
    )
    status_df.index.name = None
    status_df.fillna(0, inplace=True)
    status_df["epiweek"] = status_df.index

    # -------------------------------------------------------------------------
    # Geography
    geo_df = pd.pivot_table(
        data=linelist_df.sort_values(by="epiweek"),
        values="strain",
        index=["epiweek"],
        columns=[geo],
        aggfunc="count",
    )
    geo_df.index.name = None
    geo_df.fillna(0, inplace=True)
    geo_df["epiweek"] = geo_df.index

    # ---------------------------------------------------------------------
    # Designated

    designated_df = pd.pivot_table(
        data=linelist_df[linelist_df["status"] == "Designated"].sort_values(
            by="epiweek"
        ),
        values="strain",
        index=["epiweek"],
        columns=["lineage"],
        aggfunc="count",
    )
    designated_df.index.name = None
    designated_df.fillna(0, inplace=True)
    designated_df["epiweek"] = designated_df.index

    # ---------------------------------------------------------------------
    # Largest

    largest_df = pd.pivot_table(
        data=linelist_df[linelist_df["cluster_id"] == largest_cluster_id].sort_values(
            by="epiweek"
        ),
        values="strain",
        index=["epiweek"],
        columns=[geo],
        aggfunc="count",
    )
    largest_df.index.name = None
    largest_df.fillna(0, inplace=True)
    largest_df["epiweek"] = largest_df.index

    # -------------------------------------------------------------------------
    # Filter for Reporting Period
    # -------------------------------------------------------------------------

    # Add empty data for weeks if needed
    epiweek_map = {}
    iter_week = min_epiweek
    iter_i = 0
    while iter_week <= max_epiweek:

        if iter_week not in status_df["epiweek"]:

            status_df.loc[iter_week] = 0
            status_df.at[iter_week, "epiweek"] = iter_week

        if iter_week not in geo_df["epiweek"]:

            geo_df.loc[iter_week] = 0
            geo_df.at[iter_week, "epiweek"] = iter_week

        if iter_week not in lineage_df["epiweek"]:

            lineage_df.loc[iter_week] = 0
            lineage_df.at[iter_week, "epiweek"] = iter_week

        if iter_week not in designated_df["epiweek"]:
            designated_df.loc[iter_week] = 0
            designated_df.at[iter_week, "epiweek"] = iter_week

        if iter_week not in largest_df["epiweek"]:
            largest_df.loc[iter_week] = 0
            largest_df.at[iter_week, "epiweek"] = iter_week

        # Check if its the largest

        epiweek_map[iter_week] = iter_i
        iter_week += timedelta(weeks=1)
        iter_i += 1

    lineage_df.sort_values(by="epiweek", axis="index", inplace=True)
    status_df.sort_values(by="epiweek", axis="index", inplace=True)
    geo_df.sort_values(by="epiweek", axis="index", inplace=True)
    designated_df.sort_values(by="epiweek", axis="index", inplace=True)
    largest_df.sort_values(by="epiweek", axis="index", inplace=True)

    lag_epiweek = max_epiweek - timedelta(weeks=lag)
    lag_i = epiweek_map[lag_epiweek]

    # -------------------------------------------------------------------------
    # Plot Status

    plot_dict = {
        "lineage": {
            "legend_title": "lineage",
            "df": lineage_df,
            "y": "recombinant_lineage_curated",
        },
        "status": {
            "legend_title": "status",
            "df": status_df,
        },
        "geography": {
            "legend_title": geo,
            "df": geo_df,
        },
        "designated": {"legend_title": "lineage", "df": designated_df},
        "largest": {"legend_title": geo, "df": largest_df},
    }

    for plot in plot_dict:

        df = plot_dict[plot]["df"]
        x = "epiweek"
        label = plot
        legend_title = plot_dict[plot]["legend_title"]

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

        # Setup up Figure
        fig, ax = plt.subplots(1, figsize=FIGSIZE, dpi=DPI)

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

        ax.set_ylabel("Number of Sequences", fontweight="bold")
        ax.set_xlabel("Start of Week", fontweight="bold")
        ax.xaxis.set_label_coords(0.5, -0.30)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha="center", fontsize=8)

        ax.set_ylim(0, round(max_epiweek_sequences * EPIWEEK_MAX_BUFF_FACTOR, 1))

        legend = ax.legend(
            title=legend_title.title(), edgecolor="black", fontsize=8, ncol=legend_ncol
        )
        legend.get_frame().set_linewidth(1)
        legend.get_title().set_fontweight("bold")

        out_path = os.path.join(outdir, label)
        plt.savefig(out_path + ".png", bbox_inches="tight")


if __name__ == "__main__":
    main()
