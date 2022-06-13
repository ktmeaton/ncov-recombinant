#!/usr/bin/env python3
import click
import filecmp
import os
import json

NO_DATA_CHAR = "NA"
GEO_RESOLUTIONS = "resources/geo_resolutions.json"


def json_get_strains(json_tree):
    if "children" not in json_tree:
        return json_tree["name"]
    else:
        return ",".join([json_get_strains(c) for c in json_tree["children"]])


@click.command()
@click.option("--indir", help="Input directory of subtrees.", required=True)
@click.option("--outdir", help="Output directory for collapsed trees.", required=True)
def main(
    indir,
    outdir,
):
    """Collect and condense UShER subtrees"""

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    trees_list = [
        os.path.join(indir, f) for f in os.listdir(indir) if f.endswith("json")
    ]
    subtrees = {}

    print("Parsed: {} trees".format(len(trees_list)))

    # If there was only 1 tree...
    if len(trees_list) == 1:
        subtrees[1] = [trees_list[0]]

    else:
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
        with open(in_path) as infile:
            json_data = json.load(infile)

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
            if coloring["key"] == color_col:
                color_col_found = True

        if color_col_found:
            json_data["meta"]["display_defaults"]["color_by"] = color_col

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
            # outfile.write(json.dumps(json_data, indent=2))
            outfile.write(json.dumps(json_data))


if __name__ == "__main__":
    main()
