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

LINEAGE_COLS = ["recombinant_lineage_curated", "lineage", "pango_lineage"]


def create_sankey_data(df, node_order="default", min_y=0.001, min_link_size=1):

    # -------------------------------------------------------------------------
    # Links

    link_data = {
        "source": [],
        "target": [],
        "value": [],
        "color": None,
    }

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

    # -------------------------------------------------------------------------
    # Filter on minimum link size

    remove_link_i = []
    for i, v in enumerate(link_data["value"]):
        s = link_data["source"][i]
        t = link_data["target"][i]

        if v < min_link_size:
            remove_link_i.append(i)

    # Delete links in reverse index order
    for i in sorted(remove_link_i, reverse=True):
        del link_data["source"][i]
        del link_data["target"][i]
        del link_data["value"][i]

    # Create source and target nodes links
    source_node_links = {}
    target_node_links = {}
    for source, target, value in zip(
        link_data["source"], link_data["target"], link_data["value"]
    ):
        if source not in source_node_links:
            source_node_links[source] = 0
        if target not in target_node_links:
            target_node_links[target] = 0

        # Incrememnt count of these nodes
        source_node_links[source] += value
        target_node_links[target] += value

    # -------------------------------------------------------------------------
    # Node Palette

    # labels = list(set(list(df["source"]) + list(df["target"])))
    labels = list(set(list(source_node_links.keys()) + list(target_node_links.keys())))
    labels_i = {label: i for i, label in enumerate(labels)}

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
    # Link Palette
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

    # -------------------------------------------------------------------------
    # Node Ordering

    source_node_order = list(source_node_links.keys())

    # Source: Order Y position alphabetically
    if node_order.startswith("alphabetical"):
        source_node_no_suffix = [node[0:-1] for node in source_node_links.keys()]
        source_node_order = [
            node + SOURCE_CHAR for node in sorted(source_node_no_suffix)
        ]

    # Source: Order Y position by link size
    elif node_order.startswith("size"):
        # List of tuples, lineage and size: [('XAW*', 1), ('XAY*', 4), ... ]
        source_node_order = sorted(source_node_links.items(), key=lambda x: x[1])
        source_node_order = [kv[0] for kv in source_node_order[::-1]]

    if node_order.endswith("rev"):
        source_node_order.reverse()

    # Put NA at the end
    if NO_DATA_CHAR + TARGET_CHAR in source_node_order:
        source_node_order.remove(NO_DATA_CHAR + SOURCE_CHAR)
        source_node_order.append(NO_DATA_CHAR + SOURCE_CHAR)

    source_node_y = {}

    if len(source_node_links) > 1:
        y_buff = 1 / (len(source_node_links) - 1)
    else:
        y_buff = 1

    for i, label in enumerate(source_node_order):
        if i == 0:
            y = min_y
        elif i == len(source_node_links) - 1:
            y = 0.999
        else:
            y = min_y + (i * y_buff)

        source_node_y[label] = y

    # Target: Order Y position alphabetically
    target_node_order = list(target_node_links.keys())

    if node_order.startswith("alphabetical"):
        target_node_no_suffix = [node[0:-1] for node in target_node_links.keys()]
        target_node_order = [
            node + TARGET_CHAR for node in sorted(target_node_no_suffix)
        ]

    # Source: Order Y position by link size
    elif node_order.startswith("size"):
        # List of tuples, lineage and size: [('XAW*', 1), ('XAY*', 4), ... ]
        target_node_order = sorted(target_node_links.items(), key=lambda x: x[1])
        target_node_order = [kv[0] for kv in target_node_order[::-1]]

    if node_order.endswith("rev"):
        target_node_order.reverse()

    # Put NA at the end
    if NO_DATA_CHAR + TARGET_CHAR in target_node_order:
        target_node_order.remove(NO_DATA_CHAR + TARGET_CHAR)
        target_node_order.append(NO_DATA_CHAR + TARGET_CHAR)

    target_node_y = {}

    if len(target_node_links) > 1:
        y_buff = 1 / (len(target_node_links) - 1)
    else:
        y_buff = 1

    for i, label in enumerate(target_node_order):
        if i == 0:
            y = min_y
        elif i == len(target_node_links) - 1:
            y = 0.999
        else:
            y = min_y + (i * y_buff)

        target_node_y[label] = y

    node_x = []
    node_y = []

    for label in labels:
        if label in source_node_y:
            x = 0.001
            y = source_node_y[label]

        elif label in target_node_y:
            x = 0.999
            y = target_node_y[label]

        node_x.append(x)
        node_y.append(y)

    # This doesn't work yet
    if node_order != "default":
        node_data["x"] = node_x
        node_data["y"] = node_y

    # -------------------------------------------------------------------------

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


def create_sankey_plot(sankey_data, node_order="default"):

    # if node_order == "default":
    #    arrangement = "snap"
    # else:
    #    arrangement = "fixed"

    fig = go.Figure(
        data=[
            go.Sankey(
                node=sankey_data["node"],
                link=sankey_data["link"],
                # arrangement=arrangement,
            )
        ]
    )
    return fig


@click.command()
@click.option("--positives-1", help="First positives table (TSV)", required=True)
@click.option("--positives-2", help="Second positives table (TSV)", required=True)
@click.option("--ver-1", help="First version for title", required=True)
@click.option("--ver-2", help="Second version for title", required=True)
@click.option("--outdir", help="Output directory", required=True)
@click.option("--log", help="Logfile", required=False)
@click.option(
    "--node-order",
    help="Method of sorting the order of nodes",
    type=click.Choice(
        ["default", "size", "alphabetical", "size-rev", "alphabetical-rev"],
        case_sensitive=True,
    ),
    required=False,
    default="alphabetical",
)
@click.option(
    "--min-y", help="Increase if nodes overlap the title", required=False, default=0.001
)
@click.option(
    "--min-link-size",
    help="Remove links smaller than this",
    required=False,
    default=1,
)
def main(
    positives_1,
    positives_2,
    ver_1,
    ver_2,
    outdir,
    log,
    node_order,
    min_y,
    min_link_size,
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

    # Try to find the lineage col for each df
    for col in LINEAGE_COLS:
        if col in positives_1_df.columns:
            lineages_1 = positives_1_df[["strain", col]]
            lineages_1 = lineages_1.rename(columns={col: "source"})
            break

    for col in LINEAGE_COLS:
        if col in positives_2_df.columns:
            lineages_2 = positives_2_df[["strain", col]]
            lineages_2 = lineages_2.rename(columns={col: "target"})
            break

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
    sankey_data = create_sankey_data(
        lineages_df, node_order=node_order, min_y=min_y, min_link_size=min_link_size
    )
    logger.info("Creating sankey plot.")
    sankey_fig = create_sankey_plot(sankey_data, node_order=node_order)
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
