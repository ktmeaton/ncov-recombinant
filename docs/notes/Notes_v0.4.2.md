# v0.4.2

This is a minor bug fix and enhancement release with the following changes:

## Linelist

- [Issue #70](https://github.com/ktmeaton/ncov-recombinant/issues/70): Fix missing `sc2rf` version from `recombinant_classifier_dataset`
- [Issue #74](https://github.com/ktmeaton/ncov-recombinant/issues/74): Correctly identify `XN-like` and `XP-like`. Previously, these were just assigned `XN`/`XP` regardless of whether the estimated breakpoints conflicted with the curated ones.
- [Issue #76](https://github.com/ktmeaton/ncov-recombinant/issues/76): Mark undesignated lineages with no matching sc2rf lineage as `unpublished`.

## Plot

- [Issue #71](https://github.com/ktmeaton/ncov-recombinant/issues/71): Only truncate `cluster_id` while plotting, not in table generation.
- [Issue #72](https://github.com/ktmeaton/ncov-recombinant/issues/72): For all plots, truncate the legend labels to a set number of characters. The exception to this are parent labels (clade,lineage) because the full label is informative.
- [Issue #73](https://github.com/ktmeaton/ncov-recombinant/issues/73), [#75](https://github.com/ktmeaton/ncov-recombinant/issues/75): For all plots except breakpoints, lineages will be defined by the column `recombinant_lineage_curated`. Previously it was defined by the combination of `recombinant_lineage_curated` and `cluster_id`, which made cluttered plots that were too difficult to interpret.
- New parameter `--lineage-col` was added to `scripts/plot_breakpoints.py` to have more control on whether we want to plot the raw lineage (`lineage`) or the curated lineage (`recombinant_lineage_curated`).
