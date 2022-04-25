# Development

1. Add lineage `XM` to controls.

    - There are now publicly available samples.

1. Correct `XF` and `XJ` controls to match issues.
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
    - Comment out dev tools: `git` and `pre-commit`.

1. Use github api to pull recombinant issues.
1. Consolidate \*_to_\* files into `resources/issues.tsv`.
1. Use the `--clades` param of `sc2rf` rather than using `exclude_clades`.
1. Disabled `--rebuild-examples` in `sc2rf` because of requests error.
1. Add column `issue` to `recombinants.tsv`.
1. Get `ncov-recombinant` version using tag.

## To DO

### Priority

1. Add a `tutorial` profile.

    - (N=2) Designated Recombinants (pango-designation)
    - (N=2) Proposed Recombinants (issues, UCSC)
    - (N=2) Unpublished Recombinants
    - (N=2) Non Recombinant

1. Add documentation to the report.

    - What the sequences column format means: X (+X)
    - What the different lineage assignments are ()

### Misc

1. Remove nwk output from `usher` and `usher_subtrees`:

    - Pull subtree sample names from json instead

1. Troubleshoot `sc2rf` update to `bd2a4009` which drops all deltacrons.

    - The last stable commit was `5ac8d04`.

1. Remove the `resources` in config.yaml.
1. Investigate the reasons that X* lineages are excluded by `sc2rf`.
1. Add citations to report.
1. Update UShER to 0.5.3.
1. Plot recombinant breakpoints differently.
1. Edit Auspice json to change default colorings,filters,and panels (also sort).
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
