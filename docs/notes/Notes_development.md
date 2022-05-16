# Development

## Bugs

1. Fix bug in `sc2rf_recombinants` regions/breakpoints logic.
1. Fix bug in `sc2rf` where a sample has no definitive substitutions.

## Params

1. Allow `--breakpoints 0-4`, for XN. We'll determine the breakpoints in post-processing.
1. Bump up the `min_len` of `sc2rf_recombinants` to 1000 bp.
1. Add param `mutation_threshold` to `sc2rf`.
1. Reduce default `mutation_threshold` to 0.25 to catch [Issue #591](https://github.com/cov-lineages/pango-designation/issues/591_.
1. Bump up subtree size from 100 sequences to 500 sequences.

    - Trying to future proof against XE growth (200+ sequences)

1. Discovered that `--primers` interferes with breakpoint detection, use only for debugging.
1. Only use `--enable-deletions` in `sc2rf` for debug mode. Otherwise it changes breakpoints.
1. Only use `--private-mutations` to `sc2rf` for debug mode. Unreadable output for bulk sample processing.

## Report

1. Change `sc2rf_lineage` column to use NA for no lineage found.

    - This is to troubleshot when only one breakpoint matches a lineage.

1. Add `sc2rf_mutations_version` to summary based on a datestamp of `virus_properties.json`.
1. Allow multiple issues in report.
1. Use three status categories of recombinants:

    - Designated
    - Proposed
    - Unpublished

1. Add column `status` to recombinants.
1. Add column `usher_extra` to `usher_metadata` for 2022-05-06 tree.
1. Separate out columns lineage and issue in `report`.
1. Add optional columns to report.
1. Fixed growth calculations in report.
1. Add a Definitions section to the markdown/pdf report.
1. Use parent order for breakpoint matching, as we see same breakpoint different parents.
1. Add the number of usher placements to the summary.

## Output

1. Set Auspice default coloring to `lineage_usher` where possible.
1. Remove nwk output from `usher` and `usher_subtrees`:

    - Pull subtree sample names from json instead

1. Output `linelist.exclude.tsv` of false-positive recombinants.

## Programs

1. Update `nextclade_dataset` to 2022-04-28.
1. Add `taxoniumtools` and `chronumental` to environment.
1. Separate nextclade clades and pango lineage allele frequences in `sc2rf`.
1. Exclude BA.3, BA.4, and BA.5 for now, as their global prevalence is low and they are descendants of BA.2.

## Profiles

1. Add a `tutorial` profile.

    - (N=2) Designated Recombinants (pango-designation)
    - (N=2) Proposed Recombinants (issues, UCSC)
    - (N=2) Unpublished Recombinants

1. Add XL to `controls`.
1. Add XN to `controls`.
1. Add XR to `controls`.
1. Add XP to `controls`.

## Workflow

1. Split `usher_subtree` and `usher_subtree_collapse` into separate rules.

    - This speeds up testing for collapsing trees and styling the Auspice JSON.

1. Force include `Nextclade` recombinants (auto-pass through `sc2rf`).
1. Split `usher` and `usher_stats` into separate rules.

## To Do

### Priority

1. Should deletions be used to define recombinants and breakpoints?

    - Currently, no, it changes published breakpoints.

1. Troubleshoot `sc2rf` update to `bd2a4009` which drops all deltacrons.

    - The last stable commit was `5ac8d04`.

### Misc

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
    - XT | No public genomes, South Africa
    - XU | No public genomes, India, Japan, Australis
