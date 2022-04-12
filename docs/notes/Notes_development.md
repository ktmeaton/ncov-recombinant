# Development

1. Add lineage `XD` to controls.
    - There are now publicly available samples.
1. Add lineage `XQ` to controls.
    - Has only 1 diagnostic substitution: 2832.
1. Add lineage `XS` to controls.
1. Exclude lineage `XR` because it has no public genomes.
    - `XR` decends from `XQ` in the UShER tree.
1. Test `sc2rf` dev to ignore clade regions that are ambiguous.
1. Add column `usher_pango_lineage_map` that maps github issues to recombinant lineages.
1. Add new rule `report`.
1. Filter non-recombinants from `sc2rf` ansi output.
1. Fix `subtrees_collapse` failing if only 1 tree specified

## To Do

1. Automate unit test update.
1. Move `report` output to `reporting` directory.
1. subtree metadata:

    ```bash
    csvtk grep -t -f "strain" -P results/controls/subtrees_collapse/subtree_1.txt data/public-latest/metadata.tsv \
      | csvtk rename -t -f "pangolin_lineage" -n "pango_lineage" \
      > results/controls/subtrees_collapse/subtree_1.public.tsv;

    csvtk grep -t -f "strain" -P results/controls/subtrees_collapse/subtree_1.txt results/controls/nextclade.metadata.tsv \
      | csvtk merge -t -f "strain" results/controls/usher.clades.tsv - \
      | csvtk rename -t -f "clade" -n "Nextstrain_clade" \
      | csvtk rename -t -f "Nextclade_pango" -n "pango_lineage" \
      | csvtk rename -t -f "usher_pango_lineage" -n "pango_lineage_usher" \  
      > results/controls/subtrees_collapse/subtree_1.input.tsv;

    csvtk concat -t  results/controls/subtrees_collapse/subtree_1.public.tsv results/controls/subtrees_collapse/subtree_1.input.tsv \
      | csvtk replace -t -f "pango_lineage_usher" -p "(proposed[0-9]+)" -k data/controls/usher_to_pango.tsv -r "{kv}" \
      > results/controls/subtrees_collapse/subtree_1.tsv
    ```
