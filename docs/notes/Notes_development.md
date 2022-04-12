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
1. Test the `exclude_clades` param of Nextclade to make sure isn't removing.
