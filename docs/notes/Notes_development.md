# Development

1. Add lineage `XM` to controls.

    - There are now publicly available samples.

1. Create a markdown report with program versions.
1. Fix `sc2rf_recombinants` bug where samples with >2 breakpoints were being excluded.
1. Summarize recombinants by parents and dates observed.
1. Change `report.tsv` to `linelist.tsv`.
1. Use `date_to_decimal.py` to create `num_date` for auspice subtrees.
1. Add an `--exclude-clades` param to `sc2rf_recombinants.py`.
1. Add param `--ignore-shared-subs` to `sc2rf`.

    - This makes regions detection more conservative.
    - The result is that regions/clade will be smaller and breakpoints larger.
    - These breakpoints more closely match pango-designation issues.

1. Bump up `min_len` for `sc2rf_recombinants` to 200 bp.

## To DO

### Priority

1. Add column `lineage_breakpoint` to `sc2rf_recombinants` output.

    - I want this to take the form of X*, or proposed{issue} to follow UShER.
    - To accomplish this, I need a mapping of breakpoints to lineages and issues.

### Misc

1. Drop redundant `XF` strains?
1. Tidy up all the x_to_x.tsv files in `data/controls`.

    - `issue_to_lineage.tsv` used by rule `usher`.

1. Investigate why X* lineages are excluded from nextclade
1. Add citations to report.
1. Update `sc2rf` to `bd2a4009` for `BA.4` and `BA.5` parents.
1. Update UShER to 0.5.3.
1. Plot recombinant breakpoints differently.
1. Edit Auspice json to change default colorings,filters,and panels.
1. Automate unit test update.
1. Not implemented recombinant lineages:

    - XA | Alpha recombinant (poor lineage accuracy)
    - XB | Conflicting designation [issue](https://github.com/summercms/covid19-pango-designation/commit/26b7359e34a0b2f122215332b6495fea97ff3fe7)
    - XC | Alpha recombinant (poor lineage accuracy)
    - XK | No public genomes
    - XL | No public genomes
    - XN
    - XP
    - XR
    - XT  
    - XU
