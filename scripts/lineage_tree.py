#!/usr/bin/env python3

import click
import os
from Bio import Phylo
from Bio.Phylo.BaseTree import Clade
import requests
from pango_aliasor.aliasor import Aliasor

LINEAGES_URL = (
    "https://raw.githubusercontent.com/cov-lineages/pango-designation/master/"
    + "lineage_notes.txt"
)


@click.command()
@click.option("--output", help="Output newick phylogeny.", required=True)
def main(output):
    """Create a newick tree out of the nextclade dataset Auspice JSON"""

    # Create output directory if it doesn't exist
    outdir = os.path.dirname(output)
    if not os.path.exists(outdir) and outdir != "":
        os.mkdir(outdir)

    # -------------------------------------------------------------------------
    # Download Latest designated lineages from pango-designation

    print("Downloading list of lineages: {}".format(LINEAGES_URL))
    r = requests.get(LINEAGES_URL)
    lineage_text = r.text

    # Convert the text table to list
    lineages = []
    for line in lineage_text.split("\n"):
        if "Withdrawn" in line or line.startswith("Lineage"):
            continue

        lineage = line.split("\t")[0]
        if lineage == "":
            continue
        lineages.append(lineage)

    # Initialize the aliasor, which will download the latest aliases
    aliasor = Aliasor()

    # -------------------------------------------------------------------------
    # Construct Tree

    print("Constructing tree.")

    # Create a tree with a root node "MRCA"
    tree = Clade(name="MRCA", clades=[], branch_length=1)

    for lineage in lineages:

        # Identify the parent
        lineage_uncompress = aliasor.uncompress(lineage)
        parent_uncompress = ".".join(lineage_uncompress.split(".")[0:-1])
        parent = aliasor.compress(parent_uncompress)

        # Manual parents setting for A and B
        if lineage == "A":
            parent = "MRCA"

        elif lineage == "B":
            parent = "A"

        # Special handling for recombinants
        elif lineage.startswith("X") and parent == "":
            parent = "X"

        parent_clade = [c for c in tree.find_clades(parent)]
        # If we found a parent, as long as the input list is formatted correctly
        # this should always be true
        if len(parent_clade) == 1:
            parent_clade = parent_clade[0]
            clade = Clade(name=lineage, clades=[], branch_length=1)
            parent_clade.clades.append(clade)

    # -------------------------------------------------------------------------
    # Export

    tree_outpath = os.path.join(output)
    print("Exporting tree: {}".format(tree_outpath))
    Phylo.write(tree, tree_outpath, "newick")


if __name__ == "__main__":
    main()
