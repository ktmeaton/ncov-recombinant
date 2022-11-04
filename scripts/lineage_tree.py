#!/usr/bin/env python3

import click
import os
import json
from functions import create_logger
from Bio import Phylo
from Bio.Phylo.BaseTree import Clade


def build_tree(tree_data, tree=None, parent=None):

    node_name = tree_data["name"]

    # ----------------------------------------------------------------------
    # Node name parsing

    # for internal nodes, use the pango lineage annot as the name
    if "NODE_" in node_name or "internal" in node_name:
        node_name = tree_data["node_attrs"]["Nextclade_pango"]["value"]

    # Handle rec_parent as parent node of recombinants
    elif node_name == "rec_parent":
        node_name = "X"

    # Nodes with non-lineage names, we will use the pango lineage instead
    incorrect_node_names = ["21M", "22612T", "BA2754"]

    if node_name in incorrect_node_names:
        node_name = tree_data["node_attrs"]["Nextclade_pango"]["value"]

    # Nodes with the wrong parent
    if node_name == "CK.2.1":
        parent = "CK.2"

    # ----------------------------------------------------------------------
    # Clade construction

    # Check if we're just starting (create a root)
    if not tree:
        node_name = "MRCA"
        tree = Clade(name=node_name, clades=[], branch_length=1)

    # Otherwise, this is not the root and has a parent
    else:
        # Check if the node_name is already in the tree
        tree_clades = [c.name for c in tree.find_clades()]
        if node_name not in tree_clades:
            parent_clade = [c for c in tree.find_clades(parent)]
            # If we found a parent
            if len(parent_clade) == 1:
                parent_clade = parent_clade[0]
                clade = Clade(name=node_name, clades=[], branch_length=1)
                parent_clade.clades.append(clade)

    # Recurse through children
    if "children" in tree_data.keys():
        for child in tree_data["children"]:
            tree = build_tree(child, tree, parent=node_name)

    return tree


@click.command()
@click.option(
    "--tree-json", help="Auspice phylogeny JSON from nextclade dataset.", required=True
)
@click.option("--output", help="Output newick phylogeny.", required=True)
@click.option("--log", help="Log file.", required=False)
def main(tree_json, output, log):
    """Create a newick tree out of the nextclade dataset Auspice JSON"""

    # Check output directory
    outdir = os.path.dirname(output)
    if not os.path.exists(outdir) and outdir != "":
        os.mkdir(outdir)

    # create logger
    logger = create_logger(log)

    # read in Auspice JSON
    logger.info("INFO:\tReading JSON.")
    with open(tree_json) as infile:
        tree_data = json.load(infile)["tree"]

    # construct the tree
    logger.info("INFO:\tConstructing tree.")
    tree = build_tree(tree_data)

    # export
    tree_outpath = os.path.join(output)
    logger.info("INFO:\tExporting tree: {}".format(tree_outpath))
    Phylo.write(tree, tree_outpath, "newick")


if __name__ == "__main__":
    main()
