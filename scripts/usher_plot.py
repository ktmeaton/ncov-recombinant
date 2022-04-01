#!/usr/bin/env python3

import click
from Bio import Phylo
import matplotlib.pyplot as plt
from matplotlib import lines
import seaborn as sns
import os

# Global plot configuration
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["savefig.facecolor"] = "white"
plt.rcParams["savefig.dpi"] = 200
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["font.size"] = 6

# ---------------------------------------------------------------------------
# Argument Parsing


@click.command()
@click.option("--tree", help="Newick phylogenetic tree.", required=True)
@click.option("--strains", help="File of strains of interest.", required=True)
@click.option("--outdir", help="Output directory", required=True)
def main(
    tree,
    strains,
    outdir,
):
    """Plot newick tree."""

    # Parse strains
    with open(strains) as infile:
        strains_list = infile.read().strip().split("\n")

    # Parse tree
    tree_path = tree
    tree_name = os.path.splitext(os.path.basename(tree_path))[0]
    tree = Phylo.read(tree_path, format="newick")
    tree.ladderize(reverse=True)
    # Phylo.draw_ascii(tree)

    figsize = [8, 8]
    fig, ax = plt.subplots(1, figsize=figsize)
    Phylo.draw(
        tree,
        axes=ax,
        label_func=lambda x: "    {}".format(x.name) if x.is_terminal() else "",
    )

    # X will be coordinates in number of mutations
    # Y will be aesthetic based on the node num in tree
    x = []
    y = []
    c = []

    y_i = 1
    root_length = tree.root.branch_length
    colors = ["#1f77b4", "#ff7f0e"]

    for t in tree.get_terminals():
        x.append(tree.distance(t) + root_length)
        y.append(y_i)
        y_i += 1
        color = colors[0]
        if t.name in strains_list:
            color = colors[1]
        c.append(color)

    plt.rcParams["font.size"] = 12

    sns.scatterplot(
        ax=ax,
        x=x,
        y=y,
        c=c,
        ec="black",
        s=20,
        zorder=2,
    )

    # Axis Formatting
    ax.set_xlabel("Mutations", fontsize=12)
    ax.set_ylabel("")
    ax.set_yticks([])
    ax.set_title(tree_name, fontsize=14, fontweight="bold", x=0.5, y=1.05)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Manual Legend
    legend_markers = [
        lines.Line2D([0], [0], color=c, markeredgecolor="black", marker="o", lw=0)
        for c in colors
    ]
    legend_labels = ["Context", "Focal"]
    legend = ax.legend(
        legend_markers, legend_labels, title="Sample Type", loc="upper left"
    )
    legend.get_frame().set_linewidth(1)
    legend.get_frame().set_edgecolor("black")
    legend.get_frame().set_boxstyle("Square")

    # Write output
    outpath = os.path.join(outdir, tree_name)
    print(outpath)
    plt.savefig(outpath + ".png", bbox_inches="tight")
    plt.savefig(outpath + ".svg", bbox_inches="tight")


if __name__ == "__main__":
    main()
