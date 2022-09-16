#!/usr/bin/env python3

import click
import os
import requests
import json
import yaml
from functions import create_logger
from Bio import Phylo
from Bio.Phylo.BaseTree import Clade

ALIAS_URL = "https://raw.githubusercontent.com/cov-lineages/pangolin-data/main/pangolin_data/data/alias_key.json"
PARENT_URL = "https://raw.githubusercontent.com/cov-lineages/lineages-website/master/_data/lineages.yml"


def dict_to_tree(data, aliases, logger):

    # -------------------------------------------------------------------------
    # TRAVERSAL 1: No Aliases
    # At the start, create the tree
    logger.info("INFO:\tTraversal 1 Constructing tree WITHOUT aliases")
    tree = Clade(name="MRCA", clades=[], branch_length=1)

    for lineage in list(data.keys()):
        clade = Clade(name=lineage, clades=[], branch_length=1)

        # Processing the root of the tree
        if "parent" not in data[lineage]:
            tree.clades.append(clade)

        else:
            parent = data[lineage]["parent"]
            parent_clade = [c for c in tree.find_clades(parent)]

            # If we found a parent
            if len(parent_clade) == 1:
                parent_clade = parent_clade[0]
                parent_clade.clades.append(clade)

    # Store all clades added so far
    clade_names = [c.name for c in tree.find_clades()]

    # -------------------------------------------------------------------------
    # TRAVERSAL 2: With Aliases
    logger.info("INFO:\tTraversal 2 Constructing tree WITH aliases")

    for lineage in list(data.keys()):

        # Skip over lineages that were already added to the tree
        if lineage in clade_names:
            continue

        clade = Clade(name=lineage, clades=[], branch_length=1)
        parent = data[lineage]["parent"]

        # If there isn't a parent, this is a recombinant lineage
        # Add it as a child of the MRCA
        if not parent:
            parent = "MRCA"

        parent_clade = [c for c in tree.find_clades(parent)]

        clade_added = False

        # Use a simple add if the parent exists
        # This will be for later sublineages (ex. BM.1.1) after the
        # parent (BM.1.) has been added.
        if len(parent_clade) == 1:
            parent_clade = parent_clade[0]
            parent_clade.clades.append(clade)
            clade_added = True

        # Otherwise, we need to do an alias search
        else:

            # Example 1: BC.1

            #   The full path parent is:     B.1.1.529.1.1.1
            #   The parental node is:        BA.1.1.1
            #   Create new node:             BC.1 as child of BA.1.1.1

            #   Finding these nodes:
            #     BC aliased to:             B.1.1.529.1.1.1
            #     B.1.1.529 is aliased to:   BA
            #     Using the alias:           BA.1.1.1

            for a_lin in aliases:

                # Ex 1 (BC.1): parent  (B.1.1.529.1.1.1) starts with B.1.1.529 (alias: BA)
                if parent.startswith(a_lin):
                    alias = aliases[a_lin]
                    # Ex 1 (BC.1): B.1.1.529.1.1.1 becomes BA.1.1.1
                    tmp_parent = parent.replace(a_lin, alias)
                    tmp_parent_clade = [c for c in tree.find_clades(tmp_parent)]

                    # If the parent's parent isn't in the tree, this is the wrong alias
                    if len(tmp_parent_clade) != 1:
                        continue

                    parent_clade = tmp_parent_clade[0]
                    parent = parent_clade.name
                    parent_clade.clades.append(clade)
                    clade_added = True

        # Log success
        if clade_added:
            logger.info(
                "INFO:\tLineage {} added under parent {}".format(lineage, parent)
            )
        # Log Failure
        else:
            logger.warning(
                "WARNING:\tLineage {} could not be added under parent {}".format(
                    lineage, parent
                )
            )

    return tree


@click.command()
@click.option("--log", help="Log file.", required=False)
@click.option("--outdir", help="Output directory.", required=False, default="resources")
def main(outdir, log):
    """Create a newick tree of pangolin lineage parents and children"""

    # Check output directory
    if not os.path.exists(outdir) and outdir != "":
        os.mkdir(outdir)

    # create logger
    logger = create_logger(log)

    # -------------------------------------------------------------------------
    # Download

    # ALIAS data
    logger.info("INFO:\tDownloading alias data: {}".format(ALIAS_URL))
    r = requests.get(ALIAS_URL)
    alias_data = r.json()

    # Parent for tree
    logger.info("INFO:\tDownloading parent data: {}".format(PARENT_URL))
    r = requests.get(PARENT_URL)
    parent_data = yaml.safe_load(r.text)

    # -------------------------------------------------------------------------
    # Analysis

    # # For testing, when you want to skip downloading
    # alias_inpath = "resources/alias_key.json"
    # with open(alias_inpath) as infile:
    #     alias_data = json.load(infile)
    # parent_inpath = "resources/lineages.yml"
    # with open(parent_inpath) as infile:
    #     parent_data = yaml.safe_load(infile)

    # Convert the parent_child list to a dict where "name" is the keys
    parent_dict = {}
    for rec in parent_data:
        parent_dict[rec["name"]] = rec

    parent_data = parent_dict

    # Add additional records to reverse alias -> lineage to lineage -> alias
    alias_rev_data = {}
    for alias, lineage in alias_data.items():
        # Skip over recombinants with multiple lineage aliases
        if type(lineage) == list or lineage == "":
            continue
        alias_rev_data[lineage] = alias

    logger.info("INFO:\tCreating tree from parent and alias data.")
    tree = dict_to_tree(data=parent_data, aliases=alias_rev_data, logger=logger)

    # -------------------------------------------------------------------------
    # Export

    alias_outpath = os.path.join(outdir, "alias_key.json")
    logger.info("INFO:\tExporting alias data: {}".format(alias_outpath))
    with open(alias_outpath, "w") as outfile:
        json.dump(alias_data, outfile, indent=2)

    parent_outpath = os.path.join(outdir, "lineages.yml")
    logger.info("INFO:\tExporting parent data: {}".format(parent_outpath))
    with open(parent_outpath, "w") as outfile:
        yaml.dump(parent_data, outfile, indent=2)

    tree_outpath = os.path.join(outdir, "lineages.nwk")
    logger.info("INFO:\tExporting tree: {}".format(tree_outpath))
    Phylo.write(tree, tree_outpath, "newick")


if __name__ == "__main__":
    main()
