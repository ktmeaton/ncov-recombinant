# Development

1. Fix bug in `sc2rf_recombinants` regions/breakpoints logic.
1. Fix bug in `sc2rf` where a sample has no definitive substitutions.
1. Change `sc2rf_lineage` column to use NA for no lineage found.

    - This is to troubleshot when only one breakpoint matches a lineage.

1. Bump up the `min_len` of `sc2rf_recombinants` to 1000 bp.
1. Add parameters `primer` and `primer_name` to `sc2rf`.
1. Add `sc2rf_mutations_version` to summary based on a datestamp of `virus_properties.json`.
1. Change `--mutation-threshold` of `sc2rf` back to 0.50 for majority vote.
1. Allow multiple issues in report.

## To DO

### Priority

1. Growth calculations is currently broken for report.
1. Recombinant clades are now larger enough (ex. XE, > 100) to be split over multiple trees.
1. Add a `tutorial` profile.

    - (N=2) Designated Recombinants (pango-designation)
    - (N=2) Proposed Recombinants (issues, UCSC)
    - (N=2) Unpublished Recombinants
    - (N=2) Non Recombinant

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
