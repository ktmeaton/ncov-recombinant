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

1. Update breakpoints in controls metadata to reflect the output with `--ignore-shared-subs`.
1. Bump up `min_len` for `sc2rf_recombinants` to 200 bp.
1. Add column `sc2rf_lineage` to `sc2rf_recombinants` output.

    - Takes the form of X*, or proposed{issue} to follow UShER.

1. Consolidate lineage assignments into a single column.

    - sc2rf takes priority if a single lineage is identified.
    - usher is next, to resolve ties or if sc2rf had no lineage.

1. Slim down the conda environment and remove unnecessary programs.

    - `augur`
    - `seaborn`
    - `snipit`
    - `bedtools`
    - Comment out `git` and `pre-commit`.

## To DO

### Priority

1. Add documentation to the report.

    - What the sequences column format means: X (+X)
    - What the different lineage assignments are ()

### Misc

1. Drop redundant `XF` strains?
1. Tidy up all the x_to_x.tsv files in `data/controls`.

    - `issue_to_lineage.tsv` used by rule `usher`.
    - `lineage_to_issue.tsv` used by rule `report`.

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
