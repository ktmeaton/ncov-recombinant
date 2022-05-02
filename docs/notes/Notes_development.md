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
1. Add a `tutorial` profile.

    - (N=2) Designated Recombinants (pango-designation)
    - (N=2) Proposed Recombinants (issues, UCSC)
    - (N=2) Unpublished Recombinants

1. Bump up subtree size from 100 sequences to 500 sequences.

    - Trying to future proof against XE growth (200+ sequences)

1. Remove nwk output from `usher` and `usher_subtrees`:

    - Pull subtree sample names from json instead

1. Use three categories of recombinants:

    - Designated
    - Proposed
    - Unpublished

1. Add column `status` to recombinants.
1. Update `nextclade_dataset` to 2022-04-28.
1. Separate out columns lineage and issue in `report`.
1. Set Auspice default coloring to `lineage_usher` where possible.
1. Add `taxoniumtools` and `chronumental` to environment.
1. Split `usher_subtree` and `usher_subtree_collapse` into separate rules.

    - This speeds up testing for collapsing trees and styling the Auspice JSON.

## To DO

### Priority

1. Add optional columns to report.
1. Clarify what "breakpoints" mean in terms of coordinates.
1. Sort report table by category (designated, proposed, unpublished)
1. Add doc about what "subtree" means in report.
1. Add doc about how a recombinant type is defined.
1. Split `recombinants.tsv` by subtree as well.
1. Use parent order for breakpoint matching, as we see same breakpoint different parents.
1. Growth calculations is currently broken for report.

### Misc

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
