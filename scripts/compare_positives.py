#!/usr/bin/env python3

import click
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from matplotlib import colors
import os
from functions import create_logger
import copy

NO_DATA_CHAR = "NA"
SOURCE_CHAR = "*"
TARGET_CHAR = "†"
UNKNOWN_COLOR = "dimgrey"
UNKNOWN_RGB = colors.to_rgb(UNKNOWN_COLOR)


def create_sankey_data(df):

    labels = list(set(list(df["source"]) + list(df["target"])))
    labels_i = {label: i for i, label in enumerate(labels)}

    # -------------------------------------------------------------------------
    # Option 1. Categorical Palette

    # node_palette_raw = categorical_palette(num_cat=len(labels_i))
    # # Recolor NA
    # if NO_DATA_CHAR in labels:
    #    na_i = labels.index(NO_DATA_CHAR)
    #    node_palette_raw[na_i] = list(UNKNOWN_RGB)
    # # Convert matplotlib rgb colors ([0.12156863 0.46666667 0.70588235])
    # # to plotly rgb colors 'rgb(255,0,0')
    # node_palette = []
    # for rgb in node_palette_raw:
    #     plotly_rgb = [str(round(col * 255)) for col in rgb]
    #     plotly_rgb_str = "rgb({})".format(",".join(plotly_rgb))
    #     node_palette.append(plotly_rgb_str)

    # -------------------------------------------------------------------------
    # Option 2. Binary Palette

    # node_palette = []
    # for label in labels:
    #     if label.startswith("X"):
    #         node_palette.append("red")
    #     elif label.startswith(NO_DATA_CHAR):
    #         node_palette.append(UNKNOWN_COLOR)
    #     else:
    #         node_palette.append("blue")

    # -------------------------------------------------------------------------
    # Option 3. Constant Palette

    node_palette = []
    for label in labels:
        if label.startswith(NO_DATA_CHAR):
            node_palette.append(UNKNOWN_COLOR)
        else:
            node_palette.append("#1f77b4")

    # -------------------------------------------------------------------------
    # Nodes

    node_data = {
        "pad": 15,
        "thickness": 20,
        "line": dict(color="black", width=0.5),
        "label": labels,
        "color": node_palette,
        "x": [],
        "y": [],
    }

    # -------------------------------------------------------------------------
    # Links

    link_data = {
        "source": [],
        "target": [],
        "value": [],
        "color": None,
    }

    source_node_links = {}
    target_node_links = {}

    for rec in df.iterrows():
        source = rec[1]["source"]
        target = rec[1]["target"]

        # Iterate through source/target to find a match
        match_found = False

        for i in range(0, len(link_data["source"])):
            s = link_data["source"][i]
            t = link_data["target"][i]

            # Found a match
            if s == source and t == target:
                match_found = True
                link_data["value"][i] += 1

        # If a match wasn't found
        if not match_found:
            link_data["source"].append(source)
            link_data["target"].append(target)
            link_data["value"].append(1)

        if source not in source_node_links:
            source_node_links[source] = 0
        if target not in target_node_links:
            target_node_links[target] = 0

        # Incrememnt count of these nodes
        source_node_links[source] += 1
        target_node_links[target] += 1

    # Create a color palette for links
    link_palette = []
    for s, t in zip(link_data["source"], link_data["target"]):

        # No change
        color = "rgba(212,212,212,0.8)"  # light grey

        # New (green)
        if s == NO_DATA_CHAR + SOURCE_CHAR:
            color = "rgba(44,160,44,0.5)"

        # Dropped (red)
        elif t == NO_DATA_CHAR + TARGET_CHAR:
            color = "rgba(214,39,40,0.5)"

        # Changed (orange)
        elif s.rstrip(SOURCE_CHAR) != t.rstrip(TARGET_CHAR):
            color = "rgba(255,127,14,0.5)"

        link_palette.append(color)
    link_data["color"] = link_palette

    # Source: Order Y position by link size
    # This doesn't work yet, and I don't know why
    source_node_rank = sorted(source_node_links.items(), key=lambda x: x[1])
    source_node_rank = [kv[0] for kv in source_node_rank[::-1]]
    source_node_y = {}

    y_buff = 1 / len(source_node_links)
    for i, label in enumerate(source_node_rank):
        y = 1 - (i * y_buff)
        source_node_y[label] = y

    # Target: Order Y position by link size
    target_node_rank = sorted(target_node_links.items(), key=lambda x: x[1])
    target_node_rank = [kv[0] for kv in target_node_rank[::-1]]
    target_node_y = {}

    y_buff = 1 / len(target_node_links)
    for i, label in enumerate(target_node_rank):
        y = 1 - (i * y_buff)
        target_node_y[label] = y

    node_x = []
    node_y = []

    for label in labels:
        if label in source_node_y:
            x = 0
            y = source_node_y[label]

        elif label in target_node_y:
            x = 1
            y = target_node_y[label]

        node_x.append(x)
        node_y.append(y)

    # This doesn't work yet
    # node_data["x"] = node_x
    # node_data["y"] = node_y

    # Convert source/target to numeric ID
    for i in range(0, len(link_data["source"])):
        s = link_data["source"][i]
        t = link_data["target"][i]

        s_i = labels_i[s]
        s_t = labels_i[t]

        link_data["source"][i] = s_i
        link_data["target"][i] = s_t

    data = {
        "node": node_data,
        "link": link_data,
    }
    return data


def create_sankey_plot(sankey_data):
    fig = go.Figure(
        data=[go.Sankey(node=sankey_data["node"], link=sankey_data["link"])]
    )
    return fig


@click.command()
@click.option("--positives-1", help="First positives table (TSV)", required=True)
@click.option("--positives-2", help="Second positives table (TSV)", required=True)
@click.option("--ver-1", help="First version for title", required=True)
@click.option("--ver-2", help="Second version for title", required=True)
@click.option("--outdir", help="Output directory", required=True)
@click.option("--log", help="Logfile", required=False)
def main(
    positives_1,
    positives_2,
    ver_1,
    ver_2,
    outdir,
    log,
):
    """Compare positive recombinants between two tables."""

    # create output directory
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    # create logger
    logger = create_logger(logfile=log)

    logger.info("Parsing table: {}".format(positives_1))
    positives_1_df = pd.read_csv(positives_1, sep="\t")
    logger.info("Parsing table: {}".format(positives_2))
    positives_2_df = pd.read_csv(positives_2, sep="\t")

    lineages_1 = positives_1_df[["strain", "recombinant_lineage_curated"]]
    lineages_2 = positives_2_df[["strain", "recombinant_lineage_curated"]]

    lineages_1 = lineages_1.rename(columns={"recombinant_lineage_curated": "source"})
    lineages_2 = lineages_2.rename(columns={"recombinant_lineage_curated": "target"})

    logger.info("Merging tables.")
    lineages_df = pd.merge(lineages_1, lineages_2, how="outer", on="strain")
    lineages_df.rename(columns={"strain": "id"}, inplace=True)

    # Convert NA
    for rec in lineages_df.iterrows():
        source = rec[1]["source"]
        target = rec[1]["target"]

        # Check for NA, which is float
        if type(source) == float:
            lineages_df.loc[rec[0], "source"] = NO_DATA_CHAR
        if type(target) == float:
            lineages_df.loc[rec[0], "target"] = NO_DATA_CHAR

    lineages_df.fillna(NO_DATA_CHAR, inplace=True)

    logger.info("Calculating statistics.")
    # Why all the copy statements? pandas throws errors unless we make
    # a proper different copy.
    new_df = copy.copy(lineages_df[lineages_df["source"] == NO_DATA_CHAR])
    drop_df = copy.copy(lineages_df[lineages_df["target"] == NO_DATA_CHAR])
    no_change_df = copy.copy(
        lineages_df[lineages_df["source"] == lineages_df["target"]]
    )
    change_df = copy.copy(
        lineages_df[
            (lineages_df["source"] != lineages_df["target"])
            & (lineages_df["source"] != NO_DATA_CHAR)
            & (lineages_df["target"] != NO_DATA_CHAR)
        ]
    )

    num_sequences = len(lineages_df)
    num_new = len(new_df)
    num_drop = len(drop_df)
    num_change = len(change_df)
    num_no_change = len(no_change_df)
    num_net = num_new - num_drop

    summary_df = pd.DataFrame(
        {
            "statistic": [
                "all",
                "no-change",
                "change",
                "new",
                "drop",
                "net",
            ],
            "count": [
                num_sequences,
                num_no_change,
                num_change,
                num_new,
                num_drop,
                num_net,
            ],
        }
    )

    # Put suffix char on end to separate source and target
    lineages_df["source"] = [s + SOURCE_CHAR for s in lineages_df["source"]]
    lineages_df["target"] = [t + TARGET_CHAR for t in lineages_df["target"]]

    title = "ncov-recombinant {ver_1}<sup>{ver_1_char}</sup> to ".format(
        ver_1=ver_1,
        ver_1_char=SOURCE_CHAR,
    ) + "{ver_2}<sup>{ver_2_char}</sup>".format(
        ver_2=ver_2,
        ver_2_char=TARGET_CHAR,
    )
    title += (
        "<br><sup>"
        + "Sequences: {}".format(num_sequences)
        + ", Unchanged (grey): {}".format(num_no_change)
        + ", Changed (orange): {}".format(num_change)
        + ", New (green): {}".format(num_new)
        + ", Dropped (red): {}".format(num_drop)
        + "</sup>"
    )

    # Create sankey data and plot
    logger.info("Creating sankey data.")
    sankey_data = create_sankey_data(lineages_df)
    logger.info("Creating sankey plot.")
    sankey_fig = create_sankey_plot(sankey_data)
    sankey_fig.update_layout(title_text=title, font_size=12, width=1000, height=800)

    # Rename columns in output tables from source/target to version numbers
    for df in [new_df, change_df, no_change_df, drop_df]:

        df.rename(columns={"source": ver_1}, inplace=True)
        df.rename(columns={"target": ver_2}, inplace=True)

    # -------------------------------------------------------------------------
    # Output

    prefix = os.path.join(outdir, "ncov-recombinant_{}_{}".format(ver_1, ver_2))

    # Tables
    logger.info("Writing output tables to: {}".format(outdir))
    summary_df.to_csv(prefix + "_summary.tsv", sep="\t", index=False)
    new_df.to_csv(prefix + "_new.tsv", sep="\t", index=False)
    drop_df.to_csv(prefix + "_drop.tsv", sep="\t", index=False)
    no_change_df.to_csv(prefix + "_no-change.tsv", sep="\t", index=False)
    change_df.to_csv(prefix + "_change.tsv", sep="\t", index=False)

    # Figures
    logger.info("Writing output figures to: {}".format(outdir))
    sankey_fig.write_html(prefix + ".html")
    pio.write_image(sankey_fig, prefix + ".png", format="png", scale=2)
    pio.write_image(sankey_fig, prefix + ".svg", format="svg", scale=2)


if __name__ == "__main__":
    main()
