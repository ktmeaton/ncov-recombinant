#!/usr/bin/env python3

import click
import pandas as pd
import plotly.graph_objects as go
from matplotlib import colors

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
            node_palette.append("blue")

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
        color = "rgba(212,212,212,0.8)"
        if s.rstrip(SOURCE_CHAR) != t.rstrip(TARGET_CHAR):
            color = "rgba(255,0,0,0.2)"

        link_palette.append(color)
    link_data["color"] = link_palette

    # Source: Order Y position by link size
    source_labels = [l for l in labels if l.endswith(SOURCE_CHAR)]
    print(source_labels)
    print(source_node_links)
    print(sorted(source_node_links.items()))
    quit()
    source_node_links = {k: v for k, v in reversed(sorted(source_node_links.items()))}
    source_node_rank = [label for label in source_node_links.values()]
    source_node_y = {}

    y_buff = 1 / len(source_node_links)
    for i, label in enumerate(source_node_rank):
        y = 1 - (i * y_buff)
        source_node_y[label] = y

    # Target: Order Y position by link size
    target_node_links = {size: node for node, size in target_node_links.items()}
    target_node_links = {k: v for k, v in reversed(sorted(target_node_links.items()))}
    target_node_rank = [label for label in target_node_links.values()]
    target_node_y = {}

    y_buff = 1 / len(target_node_links)
    for i, label in enumerate(target_node_rank):
        y = 1 - (i * y_buff)
        target_node_y[label] = y

    print(len([l for l in labels if l.endswith(SOURCE_CHAR)]))
    quit()
    print(source_node_y)
    print(source_node_y.keys())
    print(labels)
    # print(target_node_y)

    node_x = []
    node_y = []

    for label in labels:
        if label in source_node_y:
            x = 0
            y = source_node_y[label]

        elif label in target_node_y:
            x = 1
            y = target_node_y[label]
        else:
            print(label)
            quit()

        node_x.append(x)
        node_y.append(y)

    for l, x, y in zip(labels, node_x, node_y):
        print(l, x, y)

    quit()

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
@click.option("--positives-1", help="Positives table (TSV)", required=True)
@click.option("--positives-2", help="Positives table (TSV)", required=True)
@click.option("--output", help="Output figure", required=True)
@click.option("--title", help="Figure title", required=True)
def main(
    positives_1,
    positives_2,
    output,
    title,
):
    """Compare positive recombinants between two tables."""

    positives_1_df = pd.read_csv(positives_1, sep="\t")
    positives_2_df = pd.read_csv(positives_2, sep="\t")

    lineages_1 = positives_1_df[["strain", "recombinant_lineage_curated"]]
    lineages_2 = positives_2_df[["strain", "recombinant_lineage_curated"]]

    lineages_1 = lineages_1.rename(columns={"recombinant_lineage_curated": "source"})
    lineages_2 = lineages_2.rename(columns={"recombinant_lineage_curated": "target"})

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
    no_change_df = lineages_df[lineages_df["source"] == lineages_df["target"]]
    change_df = lineages_df[lineages_df["source"] != lineages_df["target"]]

    num_sequences = len(lineages_df)
    num_change = len(change_df)
    num_no_change = len(no_change_df)

    # Put suffix char on end to separate source and target
    lineages_df["source"] = [s + SOURCE_CHAR for s in lineages_df["source"]]
    lineages_df["target"] = [t + TARGET_CHAR for t in lineages_df["target"]]

    title += (
        "<br><sup>"
        + "Sequences: {}".format(num_sequences)
        + ", Unchanged Sequences: {}".format(num_no_change)
        + ", Changed Sequences: {}".format(num_change)
        + "</sup>"
    )

    # Create sankey data and plot
    sankey_data = create_sankey_data(lineages_df)
    sankey_fig = create_sankey_plot(sankey_data)
    sankey_fig.update_layout(title_text=title, font_size=10)
    sankey_fig.write_html(output)


if __name__ == "__main__":
    main()
