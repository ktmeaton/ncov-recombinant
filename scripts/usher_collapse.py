#!/usr/bin/env python3
import click
import filecmp
import shutil
import os
import json
from Bio import Phylo
from augur.utils import json_to_tree

NO_DATA_CHAR = "NA"


@click.command()
@click.option("--indir", help="Input directory of subtrees.", required=True)
@click.option("--outdir", help="Output directory for collapsed trees.", required=True)
def main(
    indir,
    outdir,
):
    """Collect and condense UShER subtrees"""

    trees_list = [
        os.path.join(indir, f) for f in os.listdir(indir) if f.endswith("json")
    ]
    subtrees = {}

    print("Parsed: {} trees".format(len(trees_list)))

    for tree_1 in trees_list:
        tree_1_idx = trees_list.index(tree_1)

        for tree_2 in trees_list[tree_1_idx + 1 :]:

            # Are these trees the same?
            same_tree = filecmp.cmp(tree_1, tree_2)

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

                    # Iterate over subtrees
                    for i in subtrees:
                        # Iterate over files associated with subtree
                        for filename in subtrees[i]:
                            subtree_found = filecmp.cmp(filename, tree)
                            subtree_match = i
                            if subtree_found:
                                break
                        if subtree_found:
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

    # Write Output

    # Sample to subtree mapping

    num_trees = 0
    subtrees_collapse = {}

    out_path_metadata = os.path.join(outdir, "metadata.tsv")

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

    print("Collapsed: {} trees".format(num_trees))
    print("Final: {} trees".format(len(subtrees_collapse)))

    # Trees
    for i in subtrees_collapse:

        # JSONS
        in_path = subtrees_collapse[i]
        out_path = os.path.join(outdir, "subtree_{}.json".format(i))
        shutil.copyfile(in_path, out_path)

        # Convert to newick
        out_path_nwk = os.path.join(outdir, "subtree_{}.nwk".format(i))
        with open(out_path) as infile:
            tree_json = json.load(infile)
        tree = json_to_tree(tree_json)
        Phylo.write(tree, out_path_nwk, "newick")


if __name__ == "__main__":
    main()
