#!/usr/bin/env python3
import click
import os
import json
import logging
import sys

NO_DATA_CHAR = "NA"
GEO_RESOLUTIONS = "resources/geo_resolutions.json"
COLS_RENAME = {
    "clade_nextclade": "Clade (Nextclade)",
    "clade_usher": "Clade (UShER)",
    "country": "Country",
    "num_date": "Date",
    "date": "Date (Raw)",
    "division": "Division",
    "genbank_accession": "Genbank Accession",
    "gisaid_epi_isl": "GISAID Accession",
    "lineage_nextclade": "Lineage (Nextclade)",
    "lineage_usher": "Lineage (UShER)",
    "usher_placements": "Number of Placements",
    "parents": "Parents",
    "breakpoints": "Recombination Breakpoints",
    "parents_regions": "Recombination Regions",
}


def json_get_strains(json_tree):
    if "children" not in json_tree:
        return json_tree["name"]
    else:
        return ",".join([json_get_strains(c) for c in json_tree["children"]])


@click.command()
@click.option("--indir", help="Input directory of subtrees.", required=True)
@click.option("--outdir", help="Output directory for collapsed trees.", required=True)
@click.option("--log", help="Logfile.", required=False)
# @click.option(
#     "--duplicate-col",
#     help="Label duplicate sequences based on the ID in this column.",
#     required=False,
# )
def main(
    indir,
    outdir,
    log,
    # duplicate_col,
):
    """Collect and condense UShER subtrees"""

    # Check for directory
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    if log:
        fh = logging.FileHandler(log)
    else:
        fh = logging.StreamHandler(sys.stdout)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    # Store a list of tree filepaths
    logging.info("Identifying tree file paths.")
    trees_list = [
        os.path.join(indir, f) for f in os.listdir(indir) if f.endswith("json")
    ]
    logging.info("Parsing JSON content of {} trees.".format(len(trees_list)))
    # Store a list of tree content
    trees_json = [json.load(open(t)) for t in trees_list]
    logging.info("JSON content successfully parsed.")

    # Grab strain lists
    logging.info("Parsing strains from {} trees.".format(len(trees_json)))
    trees_strains = [json_get_strains(tree_data["tree"]) for tree_data in trees_json]
    logging.info("Strains successfully parsed.")

    subtrees = {}

    logging.info("Comparing strains across {} trees.".format(len(trees_strains)))

    # If there was only 1 tree...
    if len(trees_list) == 1:
        subtrees[1] = [trees_list[0]]

    else:
        for tree_1 in trees_list:
            tree_1_idx = trees_list.index(tree_1)
            logging.info("Comparing tree: {}".format(tree_1_idx + 1))
            tree_1_strains = trees_strains[tree_1_idx]

            for tree_2 in trees_list[tree_1_idx + 1 :]:

                tree_2_idx = trees_list.index(tree_2)

                # Do these trees have the same strains?
                tree_2_strains = trees_strains[tree_2_idx]
                same_tree = tree_1_strains == tree_2_strains

                # How many subtrees are there currently
                num_subtrees = len(subtrees)

                # -----------------------------------------------------------------------
                # Case 1: No subtrees added yet
                if num_subtrees == 0:

                    if same_tree:
                        num_subtrees += 1
                        subtrees[num_subtrees] = [tree_1, tree_2]
                    else:
                        num_subtrees += 1
                        subtrees[num_subtrees] = [tree_1]
                        num_subtrees += 1
                        subtrees[num_subtrees] = [tree_2]

                # -----------------------------------------------------------------------
                # Case 2: Search existing trees
                else:

                    for tree in [tree_1, tree_2]:

                        subtree_found = False
                        subtree_match = None
                        tree_idx = trees_list.index(tree)
                        tree_strains = trees_strains[tree_idx]

                        # Iterate over subtrees
                        for i in subtrees:
                            # Get the representative tree from this subtree (1st)
                            subtree = subtrees[i][0]
                            subtree_idx = trees_list.index(subtree)
                            subtree_strains = trees_strains[subtree_idx]
                            subtree_found = tree_strains == subtree_strains
                            if subtree_found:
                                subtree_match = i
                                break

                        # If we found a match
                        if subtree_found:
                            subtrees[subtree_match].append(tree)
                            # Remove duplicates
                            subtrees[subtree_match] = list(set(subtrees[subtree_match]))

                        # If we couldn't find a match
                        else:
                            num_subtrees += 1
                            subtrees[num_subtrees] = [tree]

    # -------------------------------------------------------------------------
    # Write Output Metadata

    # Sample to subtree mapping
    num_trees = 0
    subtrees_collapse = {}

    out_path_metadata = os.path.join(outdir, "metadata.tsv")
    logging.info("Writing metadata to table: {}".format(out_path_metadata))

    with open(out_path_metadata, "w") as outfile:
        header = "strain\tusher_subtree"
        outfile.write(header + "\n")

        for i in subtrees:
            for filename in subtrees[i]:
                # Use first file as representative
                if filename == subtrees[i][0]:
                    subtrees_collapse[i] = filename
                strain = os.path.basename(filename).replace("_context.json", "")
                # Replace the first and last underscores with "/"
                if "_" in strain:
                    country = strain.split("_")[0]
                    collection_date = strain.split("_")[-1]
                    middle = "_".join(strain.split("_")[1:-1])
                    strain = "/".join([country, middle, collection_date])

                line = "{}\t{}".format(strain, i)
                outfile.write(line + "\n")
                num_trees += 1

    logging.info(
        "Collapsed {} trees into {} trees".format(num_trees, len(subtrees_collapse))
    )

    # -------------------------------------------------------------------------
    # Write Output Trees

    # Duplicate checking is to be done
    # if duplicate_col:
    #    logging.info("Checking for duplicate strains.")

    logging.info("Writing output trees to {}.".format(outdir))
    for i in subtrees_collapse:

        subtree_idx = trees_list.index(subtrees_collapse[i])
        json_data = trees_json[subtree_idx]

        # Strain List
        strains_csv = json_get_strains(json_data["tree"])
        strains_text = strains_csv.replace(",", "\n")
        out_path_strains = os.path.join(outdir, "subtree_{}.txt".format(i))
        with open(out_path_strains, "w") as outfile:
            outfile.write(strains_text + "\n")

        # Set Visualization Defaults
        # Color By: lineage_usher
        color_col = "lineage_usher"
        color_col_found = False

        for coloring in json_data["meta"]["colorings"]:
            var_name = coloring["key"]
            if var_name == color_col:
                color_col_found = True

            # Add coloring as filter
            if var_name not in json_data["meta"]["filters"]:
                json_data["meta"]["filters"].append(var_name)

            # Give nice name to coloring
            if var_name in COLS_RENAME:
                coloring["title"] = COLS_RENAME[var_name]

            # Otherwise use generic title case
            else:
                coloring["title"] = var_name.replace("_", " ").title()

        if color_col_found:
            json_data["meta"]["display_defaults"]["color_by"] = color_col

        # Sort the order of coloring columns
        colorings_sort = []
        colorings_order = [
            coloring["title"] for coloring in json_data["meta"]["colorings"]
        ]
        colorings_order.sort()
        for key_sort in colorings_order:
            for key_unsort in json_data["meta"]["colorings"]:
                if key_sort == key_unsort["title"]:
                    colorings_sort.append(key_unsort)
                    break

        json_data["meta"]["colorings"] = colorings_sort

        # Map
        with open(GEO_RESOLUTIONS) as infile:
            geo_json_data = json.load(infile)
        json_data["meta"]["panels"] = ["tree", "map"]
        json_data["meta"]["geo_resolutions"] = geo_json_data

        # Repeating map
        json_data["meta"]["display_defaults"]["map_triplicate"] = True

        # Write Output
        out_path = os.path.join(outdir, "subtree_{}.json".format(i))
        with open(out_path, "w") as outfile:
            # For a small analysis, use pretty json formatting (ident)
            if len(subtrees) <= 10:
                outfile.write(json.dumps(json_data, indent=2))
            # Otherwise save on space
            else:
                outfile.write(json.dumps(json_data))

    logging.info("Done")


if __name__ == "__main__":
    main()
