# v0.5.0

> Please check out the `v0.5.0` [Testing Summary Package](https://ktmeaton.github.io/ncov-recombinant/docs/testing_summary_package/ncov-recombinant_v0.4.2_v0.5.0.html) for a comprehensive report.

This is a minor release that includes the following changes:

1. Detection of all recombinants in [Nextclade dataset 2022-09-27](https://github.com/nextstrain/nextclade_data/releases/tag/2022-09-28--16-01-10--UTC): `XA` to `XBC`.
1. Create any number of custom `sc2rf` modes with CLI arguments.

## Resources

- [Issue #96](https://github.com/ktmeaton/ncov-recombinant/issues/96): Create newick phylogeny of pango lineage parent child relationships, to get accurate sublineages including aliases.
- [Issue #118](https://github.com/ktmeaton/ncov-recombinant/issues/118): Fix missing pango-designation issues for XAY and XBA.

## Datasets

- [Issue #25](https://github.com/ktmeaton/ncov-recombinant/issues/25): Reduce positive controls to one sequence per clade. Add new positive controls `XAL`, `XAP`, `XAS`, `XAU`, and `XAZ`.
- [Issue #92](https://github.com/ktmeaton/ncov-recombinant/issues/92): Reduce negative controls to one sequence per clade. Add negative control for `22D (Omicron) / BA.2.75`.
- [Issue #155](https://github.com/ktmeaton/ncov-recombinant/issues/155): Add new profile and dataset `controls-gisaid`. Only a list of strains is provided, as GISAID policy prohibits public sharing of sequences and metadata.

## Profile Creation

- [Issue #77](https://github.com/ktmeaton/ncov-recombinant/issues/77): Report slurm command for `--hpc` profiles in `scripts/create_profiles.sh`.
- [Issue #153](https://github.com/ktmeaton/ncov-recombinant/issues/153): Fix bug where build parameters `metadata` and `sequences` were not implemented.

## Nextclade

- [Issue #81](https://github.com/ktmeaton/ncov-recombinant/issues/81): Upgrade Nextclade datasets to 2022-09-27
- [Issue #91](https://github.com/ktmeaton/ncov-recombinant/issues/91): Upgrade Nextclade to v2.5.0

## sc2rf

- [Issue #78](https://github.com/ktmeaton/ncov-recombinant/issues/78): Add new parameter `max_breakpoint_len` to `sc2rf_recombinants` to mark samples with two much uncertainty in the breakpoint interval as false positives.
- [Issue #79](https://github.com/ktmeaton/ncov-recombinant/issues/79): Add new parameter `min_consec_allele` to `sc2rf_recombinants` to ignore recombinant regions with less than this number of consecutive alleles (both diagnostic SNPs and diganostic reference alleles).
- [Issue #80](https://github.com/ktmeaton/ncov-recombinant/issues/80): Migrate [sc2rf](https://github.com/lenaschimmel/sc2rf) froma submodule to a subdirectory (including LICENSE!). This is to simplify the updating process and avoid errors where submodules became out of sync with the main pipeline.
- [Issue #83](https://github.com/ktmeaton/ncov-recombinant/issues/83): Improve error handling in `sc2rf_recombinants` when the input stats files are empty.
- [Issue #89](https://github.com/ktmeaton/ncov-recombinant/issues/89): Reduce the default value of the parameter `min_len` in `sc2rf_recombinants` from `1000` to `500`.This is to handle `XAP` and `XAJ`.
- [Issue #90](https://github.com/ktmeaton/ncov-recombinant/issues/90): Auto-pass select nextclade lineages through `sc2rf`: `XN`, `XP`, `XAR`, `XAS`, and `XAZ`. This requires differentiating the nextclade inputs as separate parameters `--nextclade` and `--nextclade-no-recom`.

    `XN`,`XP`, and `XAR` have extremely small recombinant regions at the terminal ends of the genome. Depending on sequencing coverage, `sc2rf` may not reliably detect these lineages.

    The newly designated `XAS` and `XAZ` pose a challenge for recombinant detection using diagnostic alleles. The first region of `XAS` could be either `BA.5` or `BA.4` based on subsitutions, but is mostly likely `BA.5` based on deletions. Since the region contains no diagnostic alleles to discriminate `BA.5` vs. `BA.4`, breakpoints cannot be detected by `sc2rf`.

    Similarly for `XAZ`, the `BA.2` segments do not contain any `BA.2` diagnostic alleles, but instead are all reversion from `BA.5` alleles. The `BA.2` parent was discovered by deep, manual investigation in the corresponding pango-designation issue. Since the `BA.2` regions contain no diagnostic for `BA.2`, breakpoints cannot be detected by `sc2rf`.

- [Issue #95](https://github.com/ktmeaton/ncov-recombinant/issues/95): Generalize `sc2rf_recombinants` to take any number of ansi and csv input files. This allows greater flexibility in command-line arguments to `sc2rf` and are not locked into the hardcoded `primary` and `secondary` parameter sets.
- [Issue #96](https://github.com/ktmeaton/ncov-recombinant/issues/96): Include sub-lineage proportions in the `parents_lineage_confidence`. This reduces underestimating the confidence of a parental lineage.
- [Issue #150](https://github.com/ktmeaton/ncov-recombinant/issues/150): Fix bug where `sc2rf` would write empty output csvfiles if no recombinants were found.
- [Issue #151](https://github.com/ktmeaton/ncov-recombinant/issues/151): Fix bug where samples that failed to align were missing from the linelists.
- [Issue #158](https://github.com/ktmeaton/ncov-recombinant/issues/158): Reduce `sc2rf` param `--max-intermission-length` from `3` to `2` to be consistent with [Issue #79](https://github.com/ktmeaton/ncov-recombinant/issues/79).
- [Issue #161](https://github.com/ktmeaton/ncov-recombinant/issues/161): Implement selection method to pick best results from various `sc2rf` modes.
- [Issue #162](https://github.com/ktmeaton/ncov-recombinant/issues/162): Upgrade `sc2rf/virus_properties.json`.
- [Issue #163](https://github.com/ktmeaton/ncov-recombinant/issues/163): Use LAPIS `nextcladePangoLineage` instead of `pangoLineage`. Also disable default filter `max_breakpoint_len` for `XAN`.
- [Issue #164](https://github.com/ktmeaton/ncov-recombinant/issues/164): Fix bug where false positives would appear in the filter `sc2rf` ansi output (`recombinants.ansi.txt`).
- The optional `lapis` parameter for `sc2rf_recombinants` has been removed. Querying [LAPIS](https://lapis.cov-spectrum.org/) for parental lineages is no longer experimental and is now an essential component (cannot be disabled).
- The mandatory `mutation_threshold` parameter for `sc2rf` has been removed. Instead, `--mutation-threshold` can be set independently in each of the `scrf` modes.

## Linelist

- [Issue #157](https://github.com/ktmeaton/ncov-recombinant/issues/157]): Create new parameters `min_lineage_size` and `min_private_muts` to control lineage splitting into `X*-like`.

## Plot

- [Issue #17](https://github.com/ktmeaton/ncov-recombinant/issues/17]): Create script to plot lineage assignment changes between versions using a Sankey diagram.
- [Issue #82](https://github.com/ktmeaton/ncov-recombinant/issues/82]): Change epiweek start from Monday to Sunday.
- [Issue #111](https://github.com/ktmeaton/ncov-recombinant/issues/111]): Fix breakpoint distribution axis that was empty for clade.
- [Issue #152](https://github.com/ktmeaton/ncov-recombinant/issues/152): Fix file saving bug when largest lineage has `/` characters.

## Report

- [Issue #88](https://github.com/ktmeaton/ncov-recombinant/issues/88): Add pipeline and nextclade versions to powerpoint slides as footer. This required adding `--summary` as param to `report`.

## Validate

- [Issue #56](https://github.com/ktmeaton/ncov-recombinant/issues/56): Change rule `validate` from simply counting the number of positives to validating the fields `lineage`, `breakpoints`, `parents_clade`. This involves adding a new default parameter `expected` for rule `validate` in `defaults/parameters.yaml`.

### Designated Lineages

- [Issue #149](https://github.com/ktmeaton/ncov-recombinant/issues/149): `XA`
- [Issue #148](https://github.com/ktmeaton/ncov-recombinant/issues/148): `XB`
- [Issue #147](https://github.com/ktmeaton/ncov-recombinant/issues/147): `XC`
- [Issue #146](https://github.com/ktmeaton/ncov-recombinant/issues/146): `XD`
- [Issue #145](https://github.com/ktmeaton/ncov-recombinant/issues/145): `XE`
- [Issue #144](https://github.com/ktmeaton/ncov-recombinant/issues/144): `XF`
- [Issue #143](https://github.com/ktmeaton/ncov-recombinant/issues/143): `XG`
- [Issue #141](https://github.com/ktmeaton/ncov-recombinant/issues/141): `XH`
- [Issue #142](https://github.com/ktmeaton/ncov-recombinant/issues/142): `XJ`
- [Issue #140](https://github.com/ktmeaton/ncov-recombinant/issues/140): `XK`
- [Issue #139](https://github.com/ktmeaton/ncov-recombinant/issues/139): `XL`
- [Issue #138](https://github.com/ktmeaton/ncov-recombinant/issues/138): `XM`
- [Issue #137](https://github.com/ktmeaton/ncov-recombinant/issues/137): `XN`
- [Issue #136](https://github.com/ktmeaton/ncov-recombinant/issues/136): `XP`
- [Issue #135](https://github.com/ktmeaton/ncov-recombinant/issues/135): `XQ`
- [Issue #134](https://github.com/ktmeaton/ncov-recombinant/issues/134): `XR`
- [Issue #133](https://github.com/ktmeaton/ncov-recombinant/issues/133): `XS`
- [Issue #132](https://github.com/ktmeaton/ncov-recombinant/issues/132): `XT`
- [Issue #131](https://github.com/ktmeaton/ncov-recombinant/issues/131): `XU`
- [Issue #130](https://github.com/ktmeaton/ncov-recombinant/issues/130): `XV`
- [Issue #129](https://github.com/ktmeaton/ncov-recombinant/issues/129): `XW`
- [Issue #128](https://github.com/ktmeaton/ncov-recombinant/issues/128): `XY`
- [Issue #127](https://github.com/ktmeaton/ncov-recombinant/issues/127): `XZ`
- [Issue #126](https://github.com/ktmeaton/ncov-recombinant/issues/124): `XAA`
- [Issue #125](https://github.com/ktmeaton/ncov-recombinant/issues/124): `XAB`
- [Issue #124](https://github.com/ktmeaton/ncov-recombinant/issues/124): `XAC`
- [Issue #123](https://github.com/ktmeaton/ncov-recombinant/issues/123): `XAD`
- [Issue #122](https://github.com/ktmeaton/ncov-recombinant/issues/122): `XAE`
- [Issue #120](https://github.com/ktmeaton/ncov-recombinant/issues/120): `XAF`
- [Issue #121](https://github.com/ktmeaton/ncov-recombinant/issues/119): `XAG`
- [Issue #119](https://github.com/ktmeaton/ncov-recombinant/issues/119): `XAH`
- [Issue #117](https://github.com/ktmeaton/ncov-recombinant/issues/117): `XAJ`
- [Issue #116](https://github.com/ktmeaton/ncov-recombinant/issues/116): `XAK`
- [Issue #115](https://github.com/ktmeaton/ncov-recombinant/issues/115): `XAL`
- [Issue #110](https://github.com/ktmeaton/ncov-recombinant/issues/110): `XAM`
- [Issue #109](https://github.com/ktmeaton/ncov-recombinant/issues/109): `XAN`
- [Issue #108](https://github.com/ktmeaton/ncov-recombinant/issues/108): `XAP`
- [Issue #107](https://github.com/ktmeaton/ncov-recombinant/issues/107): `XAQ`
- [Issue #87](https://github.com/ktmeaton/ncov-recombinant/issues/87): `XAS`
- [Issue #105](https://github.com/ktmeaton/ncov-recombinant/issues/102): `XAT`
- [Issue #103](https://github.com/ktmeaton/ncov-recombinant/issues/103): `XAU`
- [Issue #104](https://github.com/ktmeaton/ncov-recombinant/issues/104): `XAV`
- [Issue #105](https://github.com/ktmeaton/ncov-recombinant/issues/105): `XAW`
- [Issue #85](https://github.com/ktmeaton/ncov-recombinant/issues/85): `XAY`
- [Issue #87](https://github.com/ktmeaton/ncov-recombinant/issues/87): `XAZ`
- [Issue #94](https://github.com/ktmeaton/ncov-recombinant/issues/94): `XBA`
- [Issue #114](https://github.com/ktmeaton/ncov-recombinant/issues/14): `XBB`
- [Issue #160](https://github.com/ktmeaton/ncov-recombinant/issues/160): `XBC`

### Proposed Lineages

- [Issue #99](https://github.com/ktmeaton/ncov-recombinant/issues/99): `proposed808`
