# v0.5.0

This is a major release where all recombinant lineages from `XA` to `XAZ` were validated.

## Validation

### Designated

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

### Proposed (Monitor)

- [Issue #99](https://github.com/ktmeaton/ncov-recombinant/issues/99): `proposed808`

## Resources

- [Issue #96](https://github.com/ktmeaton/ncov-recombinant/issues/96): Create a newick phylogeny of pango lineage parent child relationships, to get accurate sublineages including aliases.
- [Issue #118](https://github.com/ktmeaton/ncov-recombinant/issues/118): Fix missing pango-designation issues for XAY and XBA

## Datasets

- [Issue #25](https://github.com/ktmeaton/ncov-recombinant/issues/25): Positive controls were reduced to one sequence per clade. New positive controls include `XAL`, `XAP`, `XAS`, `XAU`, and `XAZ`.
- [Issue #92](https://github.com/ktmeaton/ncov-recombinant/issues/92): Negative controls were reduced to one sequence per clade. A negative control for `22D (Omicron) / BA.2.75` was added.

## Profile Creation

- [Issue #77](https://github.com/ktmeaton/ncov-recombinant/issues/77): Report slurm command for --hpc profiles in create_profiles
- [Issue #153](https://github.com/ktmeaton/ncov-recombinant/issues/153): Fix bug where build parameters `metadata` and `sequences` were not implemented.

## Nextclade

- [Issue #81](https://github.com/ktmeaton/ncov-recombinant/issues/81): Upgrade Nextclade datasets to 2022-09-09
- [Issue #91](https://github.com/ktmeaton/ncov-recombinant/issues/91): Upgrade Nextclade to v2.5.0

## sc2rf

- [Issue #78](https://github.com/ktmeaton/ncov-recombinant/issues/78): Add new parameter `max_breakpoint_len` to `sc2rf_recombinants` to mark samples with two much uncertainty in the breakpoint interval as false positives.
- [Issue #79](https://github.com/ktmeaton/ncov-recombinant/issues/79): Add new parameter `min_consec_allele` to `sc2rf_recombinants` to ignore recombinant regions with less than this number of consecutive alleles (both diagnostic SNPs and diganostic reference alleles).
- [Issue #80](https://github.com/ktmeaton/ncov-recombinant/issues/80): Migrate [sc2rf](https://github.com/lenaschimmel/sc2rf) froma submodule to a subdirectory (including LICENSE!). This is to simplify the updating process and avoid errors where submodules became out of sync with the main pipeline.
- [Issue #83](https://github.com/ktmeaton/ncov-recombinant/issues/83): Improve error handling in `sc2rf_recombinants` when the input stats files are empty.
- [Issue #89](https://github.com/ktmeaton/ncov-recombinant/issues/89): Reduce the default value of the parmaeter `min_len` in `sc2rf_recombinants` from `1000` to `800`.This is to handle `XAP`, which has a `BA.1` recombinant regions of `854` nucleotides.
- [Issue #90](https://github.com/ktmeaton/ncov-recombinant/issues/90): Auto-pass select nextclade lineages through `sc2rf`: `XN`, `XP`, `XAS`, and `XAZ`. This requires differentiating the nextclade inputs as separate parameters `--nextclade` and `--nextclade-no-recom`.

    `XN` and `XP` have extremely small recombinant regions at the terminal ends of the genome. Depending on sequencing coverage, `sc2rf` may not reliably detect these lineages.

    The newly designated `XAS` and `XAZ` pose a challenge for recombinant detection using diagnostic alleles. The first region of `XAS` could be either `BA.5` or `BA.4` based on subsitutions, but is mostly likely `BA.5` based on deletions. Since the region contains no diagnostic alleles to discriminate `BA.5` vs. `BA.4`, breakpoints cannot be detected by `sc2rf`.

    Similarly for `XAZ`, the `BA.2` segments do not contain any `BA.2` diagnostic alleles, but instead are all reversion from `BA.5` alleles. The `BA.2` parent was discovered by deep, manual investigation in the corresponding pango-designation issue. Since the `BA.2` regions contain no diagnostic for `BA.2`, breakpoints cannot be detected by `sc2rf`.

- [Issue #95](https://github.com/ktmeaton/ncov-recombinant/issues/95): Generalize `sc2rf_recombinants` to take any number of ansi and csv input files. This allows greater flexibility in command-line arguments to `sc2rf` and are not locked into the hardocded `primary` and `secondary` parameter sets.
- [Issue #96](https://github.com/ktmeaton/ncov-recombinant/issues/96): Include sub-lineage proportions in the `parents_lineage_confidence`. This reduces underestimating the confidence of a parental lineage.
- [Issue #150](https://github.com/ktmeaton/ncov-recombinant/issues/150): Fix bug where `sc2rf` would write empty output csvfiles if no recombinants were found.

The optional `lapis` parameter for `sc2rf_recombinants` has been removed. Querying [LAPIS](https://lapis.cov-spectrum.org/) for parental lineages is no longer experimental and is now an essential component (cannot be disabled).

The mandatory `mutation_threshold` parameter for `sc2rf` has been removed. Instead, `--mutation-threshold` can be set independently in each of the `scrf` modes.

## Plot

- [Issue #17](https://github.com/ktmeaton/ncov-recombinant/issues/17]): Created an optional script to plot lineage assignment changes between versions using a Sankey diagram.
- [Issue #82](https://github.com/ktmeaton/ncov-recombinant/issues/82]): Change epiweek start from Monday to Sunday.
- [Issue #111](https://github.com/ktmeaton/ncov-recombinant/issues/111]): Fix breakpoint distribution axis empty for clade.
- [Issue #152](https://github.com/ktmeaton/ncov-recombinant/issues/152): Fix file saving bug when largest lineage has `/` characters.

## Report

- [Issue #88](https://github.com/ktmeaton/ncov-recombinant/issues/88): Add pipeline and nextclade versions to powerpoint slides as footer. This required adding `--summary` as param to `report`.

## Validate

- [Issue #56](https://github.com/ktmeaton/ncov-recombinant/issues/56): Changed rule `validate` from simply counting the number of positives to validating the fields `lineage`, `breakpoints`, `parents_clade`. This involved adding a new default parameter `expected` for rule `validate` in `defaults/parameters.yaml`.
