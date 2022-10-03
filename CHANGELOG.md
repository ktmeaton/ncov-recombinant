# CHANGELOG

## Development

### Notes

### Commits

## v0.5.0

### Notes

> Please check out the `v0.5.0` [Testing Summary Package](https://ktmeaton.github.io/ncov-recombinant/docs/testing_summary_package/ncov-recombinant_v0.4.2_v0.5.0.html) for a comprehensive report.

This is a minor release that includes the following changes:

1. Detection of all recombinants in [Nextclade dataset 2022-09-27](https://github.com/nextstrain/nextclade_data/releases/tag/2022-09-28--16-01-10--UTC): `XA` to `XBC`.
1. Create any number of custom `sc2rf` modes with CLI arguments.

#### Resources

- [Issue #96](https://github.com/ktmeaton/ncov-recombinant/issues/96): Create newick phylogeny of pango lineage parent child relationships, to get accurate sublineages including aliases.
- [Issue #118](https://github.com/ktmeaton/ncov-recombinant/issues/118): Fix missing pango-designation issues for XAY and XBA.

#### Datasets

- [Issue #25](https://github.com/ktmeaton/ncov-recombinant/issues/25): Reduce positive controls to one sequence per clade. Add new positive controls `XAL`, `XAP`, `XAS`, `XAU`, and `XAZ`.
- [Issue #92](https://github.com/ktmeaton/ncov-recombinant/issues/92): Reduce negative controls to one sequence per clade. Add negative control for `22D (Omicron) / BA.2.75`.
- [Issue #155](https://github.com/ktmeaton/ncov-recombinant/issues/155): Add new profile and dataset `controls-gisaid`. Only a list of strains is provided, as GISAID policy prohibits public sharing of sequences and metadata.

#### Profile Creation

- [Issue #77](https://github.com/ktmeaton/ncov-recombinant/issues/77): Report slurm command for `--hpc` profiles in `scripts/create_profiles.sh`.
- [Issue #153](https://github.com/ktmeaton/ncov-recombinant/issues/153): Fix bug where build parameters `metadata` and `sequences` were not implemented.

#### Nextclade

- [Issue #81](https://github.com/ktmeaton/ncov-recombinant/issues/81): Upgrade Nextclade datasets to 2022-09-27
- [Issue #91](https://github.com/ktmeaton/ncov-recombinant/issues/91): Upgrade Nextclade to v2.5.0

#### sc2rf

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

#### Linelist

- [Issue #157](https://github.com/ktmeaton/ncov-recombinant/issues/157]): Create new parameters `min_lineage_size` and `min_private_muts` to control lineage splitting into `X*-like`.

#### Plot

- [Issue #17](https://github.com/ktmeaton/ncov-recombinant/issues/17]): Create script to plot lineage assignment changes between versions using a Sankey diagram.
- [Issue #82](https://github.com/ktmeaton/ncov-recombinant/issues/82]): Change epiweek start from Monday to Sunday.
- [Issue #111](https://github.com/ktmeaton/ncov-recombinant/issues/111]): Fix breakpoint distribution axis that was empty for clade.
- [Issue #152](https://github.com/ktmeaton/ncov-recombinant/issues/152): Fix file saving bug when largest lineage has `/` characters.

#### Report

- [Issue #88](https://github.com/ktmeaton/ncov-recombinant/issues/88): Add pipeline and nextclade versions to powerpoint slides as footer. This required adding `--summary` as param to `report`.

#### Validate

- [Issue #56](https://github.com/ktmeaton/ncov-recombinant/issues/56): Change rule `validate` from simply counting the number of positives to validating the fields `lineage`, `breakpoints`, `parents_clade`. This involves adding a new default parameter `expected` for rule `validate` in `defaults/parameters.yaml`.

##### Designated Lineages

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

##### Proposed Lineages

- [Issue #99](https://github.com/ktmeaton/ncov-recombinant/issues/99): `proposed808`

### Commits

- [```47da3bce```](https://github.com/ktmeaton/ncov-recombinant/commit/47da3bce) docs: add testing summary package for v0.4.2 to v0.5.0
- [```e90f5ac1```](https://github.com/ktmeaton/ncov-recombinant/commit/e90f5ac1) resources: fix breakpoints for XAE #122
- [```83cb848e```](https://github.com/ktmeaton/ncov-recombinant/commit/83cb848e) script: bugfix sc2rf ansi output for #164
- [```dae218b7```](https://github.com/ktmeaton/ncov-recombinant/commit/dae218b7) docs: update issues and validation table order
- [```a4ffd31b```](https://github.com/ktmeaton/ncov-recombinant/commit/a4ffd31b) script: implement lineage check in dups for #117 #161
- [```3e16bd5e```](https://github.com/ktmeaton/ncov-recombinant/commit/3e16bd5e) sc2rf updates for #158 #161 #162 #163
- [```11fd9f91```](https://github.com/ktmeaton/ncov-recombinant/commit/11fd9f91) dataset: update controls-gisaid strain list and validation
- [```2a3a433e```](https://github.com/ktmeaton/ncov-recombinant/commit/2a3a433e) workflow: new param dup_method for #161
- [```ae0821bb```](https://github.com/ktmeaton/ncov-recombinant/commit/ae0821bb) script: implement duplicate reconciliation for #161
- [```77d12515```](https://github.com/ktmeaton/ncov-recombinant/commit/77d12515) param: upgrade nextclade dataset for #159
- [```e14d516e```](https://github.com/ktmeaton/ncov-recombinant/commit/e14d516e) script: add more detail to validate table for failing samples
- [```028ccc48```](https://github.com/ktmeaton/ncov-recombinant/commit/028ccc48) script: add param --min-link-size to compare_positives
- [```43bce29c```](https://github.com/ktmeaton/ncov-recombinant/commit/43bce29c) workflow: added failed validate output to rule log
- [```1d5bb911```](https://github.com/ktmeaton/ncov-recombinant/commit/1d5bb911) workflow: don't use metadata for sc2rf_recombinants when exclude_negatives is true
- [```5dee5a0a```](https://github.com/ktmeaton/ncov-recombinant/commit/5dee5a0a) param: add new params min-lineage-size and min-private-muts for #157
- [```680ea520```](https://github.com/ktmeaton/ncov-recombinant/commit/680ea520) workflow: update validation strains for #155
- [```c9f08b3a```](https://github.com/ktmeaton/ncov-recombinant/commit/c9f08b3a) param: fix typo of missing --mutation-threshold
- [```22585f4b```](https://github.com/ktmeaton/ncov-recombinant/commit/22585f4b) param: remove param mutation_threshold as universal param for sc2rf
- [```dbd67523```](https://github.com/ktmeaton/ncov-recombinant/commit/dbd67523) dataset: remove false positive LC0797902 from negative controls
- [```33a18292```](https://github.com/ktmeaton/ncov-recombinant/commit/33a18292) profile: change default hpc jobs from 2 to 10
- [```1c8d3687```](https://github.com/ktmeaton/ncov-recombinant/commit/1c8d3687) workflow: update validation table
- [```17606f3a```](https://github.com/ktmeaton/ncov-recombinant/commit/17606f3a) script: fix node ordering in compare_positives
- [```f0da91d4```](https://github.com/ktmeaton/ncov-recombinant/commit/f0da91d4) ci: remove GISAID workflow for #154
- [```982691cf```](https://github.com/ktmeaton/ncov-recombinant/commit/982691cf) ci: test storing csv files as secrets for #154
- [```939b4da0```](https://github.com/ktmeaton/ncov-recombinant/commit/939b4da0) ci: experiment with secrets with test data for #154
- [```b1f55738```](https://github.com/ktmeaton/ncov-recombinant/commit/b1f55738) script: generalize compare_positives to use other lineage columns
- [```34eada3d```](https://github.com/ktmeaton/ncov-recombinant/commit/34eada3d) scripts: fix bug where metadata and sequences param were not implemented for #153
- [```aa8270c7```](https://github.com/ktmeaton/ncov-recombinant/commit/aa8270c7) resources: special handling of proposed808 issues and breakpoints for #99
- [```3d41c295```](https://github.com/ktmeaton/ncov-recombinant/commit/3d41c295) script: fix file saving bug in report for #152
- [```be60d668```](https://github.com/ktmeaton/ncov-recombinant/commit/be60d668) script: fix file saving bug in plot for #152
- [```3c1fd892```](https://github.com/ktmeaton/ncov-recombinant/commit/3c1fd892) script: fix missing samples in sc2rf output for #151
- [```1bc6cfd1```](https://github.com/ktmeaton/ncov-recombinant/commit/1bc6cfd1) script: force sc2rf to always output csvfile headers for #150
- [```99134681```](https://github.com/ktmeaton/ncov-recombinant/commit/99134681) resources: update breakpoints for proposed808 #99
- [```d0cf7d2c```](https://github.com/ktmeaton/ncov-recombinant/commit/d0cf7d2c) resources: update breakpoints for XA - XAZ
- [```7fc2a3a1```](https://github.com/ktmeaton/ncov-recombinant/commit/7fc2a3a1) resources: update breakpoints for XV #130
- [```f267a1e9```](https://github.com/ktmeaton/ncov-recombinant/commit/f267a1e9) resources: add gauntlet samples (all XA*) to validation
- [```fd160ee0```](https://github.com/ktmeaton/ncov-recombinant/commit/fd160ee0) param: add XAR to sc2rf auto-pass for 106
- [```712dd7a7```](https://github.com/ktmeaton/ncov-recombinant/commit/712dd7a7) docs: change next ver from v0.4.3 to v0.5.0
- [```b1bd79d6```](https://github.com/ktmeaton/ncov-recombinant/commit/b1bd79d6) workflow: fix bug in rule validate where path was hard-coded
- [```b4f545d7```](https://github.com/ktmeaton/ncov-recombinant/commit/b4f545d7) resources: update breakpoints for XAA #126
- [```f9e56759```](https://github.com/ktmeaton/ncov-recombinant/commit/f9e56759) resources: update breakpoints for XAG and XAH for #120 and #121
- [```b1057a68```](https://github.com/ktmeaton/ncov-recombinant/commit/b1057a68) param: add new XAJ mode for sc2rf for #117
- [```dbe5d23f```](https://github.com/ktmeaton/ncov-recombinant/commit/dbe5d23f) scripts: update rule validate for #56
- [```cde02709```](https://github.com/ktmeaton/ncov-recombinant/commit/cde02709) docs: add issues template for lineage validation #113
- [```28e5212c```](https://github.com/ktmeaton/ncov-recombinant/commit/28e5212c) script: fix bug of missing issues for #118
- [```58062156```](https://github.com/ktmeaton/ncov-recombinant/commit/58062156) docs: update validation release notes
- [```dc1eadae```](https://github.com/ktmeaton/ncov-recombinant/commit/dc1eadae) resources: update XAU breakpoints for #103
- [```6b483224```](https://github.com/ktmeaton/ncov-recombinant/commit/6b483224) docs: add XAQ issue #107 to release notes
- [```e3ebefa0```](https://github.com/ktmeaton/ncov-recombinant/commit/e3ebefa0) docs: add XAQ issue #107 to release notes
- [```c038200f```](https://github.com/ktmeaton/ncov-recombinant/commit/c038200f) docs: add issue #111 to release notes
- [```65dbcbf7```](https://github.com/ktmeaton/ncov-recombinant/commit/65dbcbf7) script: fix bug in plot_breakpoints when axis empty for #111
- [```1955a5fd```](https://github.com/ktmeaton/ncov-recombinant/commit/1955a5fd) resources: update breakpoints for XAP #108
- [```1471cc3b```](https://github.com/ktmeaton/ncov-recombinant/commit/1471cc3b) docs: fix typo in relesae notes
- [```e39df74e```](https://github.com/ktmeaton/ncov-recombinant/commit/e39df74e) docs: add issues #86 and #87 to release notes
- [```66f7aeba```](https://github.com/ktmeaton/ncov-recombinant/commit/66f7aeba) script: remove redundant --clades arg in sc2rf bash script
- [```fe2e7c86```](https://github.com/ktmeaton/ncov-recombinant/commit/fe2e7c86) param: add new sc2rf modes XB and proposed808 for #98 and #99
- [```74180a1c```](https://github.com/ktmeaton/ncov-recombinant/commit/74180a1c) docs: add issue #17 to release notes
- [```eba0ff04```](https://github.com/ktmeaton/ncov-recombinant/commit/eba0ff04) env: add plotly to conda env and control all versions
- [```f27a5655```](https://github.com/ktmeaton/ncov-recombinant/commit/f27a5655) script: improve directory creation in compare positives
- [```398814c2```](https://github.com/ktmeaton/ncov-recombinant/commit/398814c2) script: add breakpoint axis label for #97
- [```b16b5983```](https://github.com/ktmeaton/ncov-recombinant/commit/b16b5983) docs: add notes for v0.4.3
- [```322556ac```](https://github.com/ktmeaton/ncov-recombinant/commit/322556ac) env: upgrade csvtk to v0.24.0
- [```1b332054```](https://github.com/ktmeaton/ncov-recombinant/commit/1b332054) param: fix typo in mode omicron_omicron
- [```c8755f3c```](https://github.com/ktmeaton/ncov-recombinant/commit/c8755f3c) param: revert XAS mode to default for #86
- [```aed531e5```](https://github.com/ktmeaton/ncov-recombinant/commit/aed531e5) script: fix bug in postprocess where max_breakpoint_len was not checked
- [```fbcf1e6e```](https://github.com/ktmeaton/ncov-recombinant/commit/fbcf1e6e) param: add new XAS mode to default sc2rf runs for #86
- [```330deacc```](https://github.com/ktmeaton/ncov-recombinant/commit/330deacc) workflow: first draft of pango lineage tree for #96
- [```ae4d039d```](https://github.com/ktmeaton/ncov-recombinant/commit/ae4d039d) workflow: add param fix for postprocess inputs
- [```3f71310e```](https://github.com/ktmeaton/ncov-recombinant/commit/3f71310e) script: fix cli --clades arg parsing for scr2rf.sh
- [```c637057b```](https://github.com/ktmeaton/ncov-recombinant/commit/c637057b) script: add new csv col alleles to sc2rf
- [```edb71e57```](https://github.com/ktmeaton/ncov-recombinant/commit/edb71e57) workflow: generalize sc2rf_recombinants inputs for #95
- [```e8e96996```](https://github.com/ktmeaton/ncov-recombinant/commit/e8e96996) docs: update development docs
- [```ac0486c7```](https://github.com/ktmeaton/ncov-recombinant/commit/ac0486c7) resources: update breakpoints and issues
- [```a9186176```](https://github.com/ktmeaton/ncov-recombinant/commit/a9186176) dataset: reduce controls to one sequence per clade for #25,92
- [```cce21946```](https://github.com/ktmeaton/ncov-recombinant/commit/cce21946) workflow: update rules for #46, #88, #89, #90
- [```a664f892```](https://github.com/ktmeaton/ncov-recombinant/commit/a664f892) script: add new param auto_pass for #90
- [```888bc2d3```](https://github.com/ktmeaton/ncov-recombinant/commit/888bc2d3) params: update params for #46, #89, #90
- [```d68e5db5```](https://github.com/ktmeaton/ncov-recombinant/commit/d68e5db5) script: add pipeline version to report for #88
- [```1fcdef7e```](https://github.com/ktmeaton/ncov-recombinant/commit/1fcdef7e) script: remove sc2rf_ver col from summary for #80
- [```418afa98```](https://github.com/ktmeaton/ncov-recombinant/commit/418afa98) env: upgrade nextclade to v2.5.0 for #91
- [```bd4b0259```](https://github.com/ktmeaton/ncov-recombinant/commit/bd4b0259) workflow: autopass XAS through sc2rf for #86
- [```abb93a06```](https://github.com/ktmeaton/ncov-recombinant/commit/abb93a06) resources: update breakpoints and mutations
- [```44c16733```](https://github.com/ktmeaton/ncov-recombinant/commit/44c16733) workflow: upgrade nextclade dataset to 2022-08-23 for #81
- [```c6204304```](https://github.com/ktmeaton/ncov-recombinant/commit/c6204304) resources: updated curated breakpoints
- [```b0b88e9a```](https://github.com/ktmeaton/ncov-recombinant/commit/b0b88e9a) resources: update issues
- [```1d64db97```](https://github.com/ktmeaton/ncov-recombinant/commit/1d64db97) script: change epiweek to start on Sundary (cdc) for #82
- [```2fd2faaa```](https://github.com/ktmeaton/ncov-recombinant/commit/2fd2faaa) workflow: re-add sc2rf as subdirectory for #80
- [```e3d4d940```](https://github.com/ktmeaton/ncov-recombinant/commit/e3d4d940) workflow: remove sc2rf submodule again
- [```48776a6c```](https://github.com/ktmeaton/ncov-recombinant/commit/48776a6c) workflow: add sc2rf as subdirectory for #80
- [```38f4d7a7```](https://github.com/ktmeaton/ncov-recombinant/commit/38f4d7a7) workflow: remove sc2rf as submodule
- [```37f40480```](https://github.com/ktmeaton/ncov-recombinant/commit/37f40480) script: add tables to compare positives between versions for #17
- [```8eef7548```](https://github.com/ktmeaton/ncov-recombinant/commit/8eef7548) script: create new script to compare positives between versions
- [```ebf1e222```](https://github.com/ktmeaton/ncov-recombinant/commit/ebf1e222) script: compare linelists from different versions for #17
- [```8401c353```](https://github.com/ktmeaton/ncov-recombinant/commit/8401c353) workflow: add new param max_breakpoint_len for #78
- [```8bbcc041```](https://github.com/ktmeaton/ncov-recombinant/commit/8bbcc041) script: report slurm command for --hpc profiles for #77
- [```c40a6791```](https://github.com/ktmeaton/ncov-recombinant/commit/c40a6791) workflow: restrict config rules to one thread
- [```c2b1ea57```](https://github.com/ktmeaton/ncov-recombinant/commit/c2b1ea57) script: revert unpublished lineages for #76
- [```dbe359c8```](https://github.com/ktmeaton/ncov-recombinant/commit/dbe359c8) resources: add 882 to breakpoints

## v0.4.2

### Notes

This is a minor bug fix and enhancement release with the following changes:

#### Linelist

- [Issue #70](https://github.com/ktmeaton/ncov-recombinant/issues/70): Fix missing `sc2rf` version from `recombinant_classifier_dataset`
- [Issue #74](https://github.com/ktmeaton/ncov-recombinant/issues/74): Correctly identify `XN-like` and `XP-like`. Previously, these were just assigned `XN`/`XP` regardless of whether the estimated breakpoints conflicted with the curated ones.
- [Issue #76](https://github.com/ktmeaton/ncov-recombinant/issues/76): Mark undesignated lineages with no matching sc2rf lineage as `unpublished`.

#### Plot

- [Issue #71](https://github.com/ktmeaton/ncov-recombinant/issues/71): Only truncate `cluster_id` while plotting, not in table generation.
- [Issue #72](https://github.com/ktmeaton/ncov-recombinant/issues/72): For all plots, truncate the legend labels to a set number of characters. The exception to this are parent labels (clade,lineage) because the full label is informative.
- [Issue #73](https://github.com/ktmeaton/ncov-recombinant/issues/73), [#75](https://github.com/ktmeaton/ncov-recombinant/issues/75): For all plots except breakpoints, lineages will be defined by the column `recombinant_lineage_curated`. Previously it was defined by the combination of `recombinant_lineage_curated` and `cluster_id`, which made cluttered plots that were too difficult to interpret.
- New parameter `--lineage-col` was added to `scripts/plot_breakpoints.py` to have more control on whether we want to plot the raw lineage (`lineage`) or the curated lineage (`recombinant_lineage_curated`).

### Commits

- [```8953ef03```](https://github.com/ktmeaton/ncov-recombinant/commit/8953ef03) docs: add CHANGELOG for v0.4.2
- [```7ec5ccc6```](https://github.com/ktmeaton/ncov-recombinant/commit/7ec5ccc6) docs: add notes for v0.4.2
- [```1b3b1f1d```](https://github.com/ktmeaton/ncov-recombinant/commit/1b3b1f1d) script: restore column name to recombinant_classifer_dataset
- [```901caf98```](https://github.com/ktmeaton/ncov-recombinant/commit/901caf98) script: restore recombinant_lineage_curated of -like lineages
- [```d6be9611```](https://github.com/ktmeaton/ncov-recombinant/commit/d6be9611) script: change internal delim of classifier for #70
- [```cdb4a78a```](https://github.com/ktmeaton/ncov-recombinant/commit/cdb4a78a) script: fix recombinant_classifier missing sc2rf for #70
- [```bf7a4e57```](https://github.com/ktmeaton/ncov-recombinant/commit/bf7a4e57) script: mark undesignated lineages with no matching sc2rf lineage as unpublished for #76
- [```46f6d754```](https://github.com/ktmeaton/ncov-recombinant/commit/46f6d754) workflow: update linelists and plotting for #74 and #75
- [```c03dd3be```](https://github.com/ktmeaton/ncov-recombinant/commit/c03dd3be) script: don't split largest by cluster id for #73
- [```e9802e79```](https://github.com/ktmeaton/ncov-recombinant/commit/e9802e79) script: majority of plots will not split by cluster_id for #73
- [```bafb38fb```](https://github.com/ktmeaton/ncov-recombinant/commit/bafb38fb) script: fix cluster ID truncation for issue #71
- [```ab712593```](https://github.com/ktmeaton/ncov-recombinant/commit/ab712593) resources: curate and test breakpoints for proposed895

## v0.4.1

### Notes

This is a minor bug fix release with the following changes:

- [Issue #63](https://github.com/ktmeaton/ncov-recombinant/issues/63): Remove `usher` and `protobuf` from the conda environment.
- [Issue #68](https://github.com/ktmeaton/ncov-recombinant/issues/68): Remove [ncov](https://github.com/nextstrain/ncov) as a submodule.
- [Issue #69](https://github.com/ktmeaton/ncov-recombinant/issues/69): Remove 22C and 22D from `sc2rf/mapping.csv` and `sc2rf/virus_properties.json`, as these interfere with breakpoint detection for XAN.

### Commits

- [```88650696```](https://github.com/ktmeaton/ncov-recombinant/commit/88650696) docs: add CHANGELOG for v0.4.1
- [```00a2eec3```](https://github.com/ktmeaton/ncov-recombinant/commit/00a2eec3) docs: add notes for v0.4.1
- [```d74a81d3```](https://github.com/ktmeaton/ncov-recombinant/commit/d74a81d3) sc2rf: revert 22C and 22D clade addition
- [```7b662940```](https://github.com/ktmeaton/ncov-recombinant/commit/7b662940) env: remove usher for issue #63
- [```adf92399```](https://github.com/ktmeaton/ncov-recombinant/commit/adf92399) submodule: remove ncov for issue #68
- [```0790aa04```](https://github.com/ktmeaton/ncov-recombinant/commit/0790aa04) docs: update CHANGELOG for v0.4.0

## v0.4.0

### Notes

#### General

v0.4.0 has been trained and validated on the latest generation of SARS-CoV-2 Omicron clades (ex. 22A/BA.4 and 22B/BA.5). Recombinant sequences involving BA.4 and BA.5 can now be detected, unlike in v0.3.0 where they were not included in the `sc2rf` models.

v0.4.0 is also a **major** update to how sequences are categorized into lineages/clusters. A recombinant lineage is now defined as a group of sequences with a unique combination of:

- Lineage assignment (ex. `XM`)
- Parental clades (ex. `Omicron/21K,Omicron/21L`)
- Breakpoints (ex. `17411:21617`)
- **NEW**: Parental lineages (ex. `BA.1.1,BA.2.12.1`)

Novel recombinants (i.e. undesignated) can be identified by a lineage assignment that does not start with `X*` (ex. `BA.1.1`) _or_ with a lineage assignment that contains `-like` (ex. `XM-like`). A cluster of sequences may be flagged as `-like` if one of the following criteria apply:

1. The lineage assignment by [Nextclade](https://github.com/nextstrain/nextclade) conflicts with the published breakpoints for a designated lineage (`resources/breakpoints.tsv`).

    - Ex. An `XE` assigned sample has breakpoint `11538:12879`, which conflicts with the published `XE` breakpoint (`ex. 8394:12879`). This will be renamed `XE-like`.

1. The cluster has 10 or more sequences, which share at least 3 private mutations in common.

    - Ex. A large cluster of sequences (N=50) are assigned `XM`. However, these 50 samples share 5 private mutations `T2470C,C4586T,C9857T,C12085T,C26577G` which do not appear in true `XM` sequences. These will be renamed `XM-like`. Upon further review of the reported matching [pango-designation issues](https://github.com/cov-lineages/pango-designation/issues) (`460,757,781,472,798`), we find this cluster to be a match to `proposed798`.

The ability to identify parental lineages and private mutations is largely due to improvements in the [newly released nextclade datasets](https://github.com/nextstrain/nextclade_data/releases/tag/2022-07-26--13-04-52--UTC), , which have increased recombinant lineage accuracy. As novel recombinants can now be identified without the use of the custom UShER annotations (ex. proposed771), all UShER rules and output have been removed. This significantly improves runtime, and reduces the need to drop non-recombinant samples for performance. The result is more comparable output between different dataset sizes (4 samples vs. 400,000 samples).

> **Note!** Default parameters have been updated! Please regenerate your profiles/builds with:
>
> ```bash
> scripts/create_profile.sh --data data/custom
> ```

#### Datasets

- [Issue #49](https://github.com/ktmeaton/ncov-recombinant/issues/49):  The tutorial lineages were changed from `XM`,`proposed467`, `miscBA1BA2Post17k`, to `XD`, `XH`, `XAN`. The previous tutorial sequences had genome quality issues.
- [Issue #51](https://github.com/ktmeaton/ncov-recombinant/issues/51):  Add `XAN` to the controls dataset. This is BA.2/BA.5 recombinant.
- [Issue #62](https://github.com/ktmeaton/ncov-recombinant/issues/62):  Add `XAK` to the controls dataset. This is BA.2/BA.1 VUM recombinant monitored by the ECDC.

#### Nextclade

- [Issue #46](https://github.com/ktmeaton/ncov-recombinant/issues/46): `nextclade` is now run twice. Once with the regular `sars-cov-2` dataset and once with the `sars-cov-2-no-recomb`  dataset. The `sars-cov-2-no-recomb` dataset is used to get the nucleotide substitutions before recombination occurred. These are identified by taking the `substitutions` column, and excluding the substitutions found in `privateNucMutations.unlabeledSubstitutions`. The pre-recombination substitutions allow us to identify the parental lineages by querying [cov-spectrum](https://cov-spectrum.org/).
- [Issue #48](https://github.com/ktmeaton/ncov-recombinant/issues/48): Make the `exclude_clades` completely optional. Otherwise an error would be raised if the user didn't specify any.
- [Issue #50](https://github.com/ktmeaton/ncov-recombinant/issues/50): Upgrade from `v1.11.0` to `v2.3.0`. Also upgrade the default dataset tags to [2022-07-26T12:00:00Z](https://github.com/nextstrain/nextclade_data/releases/tag/2022-07-26--13-04-52--UTC) which had significant bug fixes.
- [Issue #51](https://github.com/ktmeaton/ncov-recombinant/issues/51):  Relax the recombinant criteria, by flagging sequences with ANY labelled private mutations as a potential recombinant for further downstream analysis. This was specifically for BA.5 recombinants (ex. `XAN`) as no other columns from the `nextclade` output indicated this could be a recombinant.
- Restrict `nextclade` output to `fasta,tsv` (alignment and QC table). This saves on file storage, as the other default output is not used.

#### sc2rf

- [Issue #51](https://github.com/ktmeaton/ncov-recombinant/issues/51): `sc2rf` is now run twice. First, to detect recombination between clades (ex. `Delta/21J` & `Omicron/21K`). Second, to detect recombination within Omicron (ex. `Omicron/BA.2/21L` & `Omicron/BA.5/22B`). It was not possible to define universal parameters for `sc2rf` that worked for both distantly related clades, and the closely related Omicron lineages.
- [Issue #51](https://github.com/ktmeaton/ncov-recombinant/issues/51): Rename parameter `clades` to `primary_clades` and add new parameter `secondary_clades` for detecting BA.5.
- [Issue #53](https://github.com/ktmeaton/ncov-recombinant/issues/53): Identify the parental lineages by splitting up the observed mutations (from `nextclade`) into regions by breakpoint. Then query the list of mutations in <https://cov-spectrum.org> and report the lineage with the highest prevalence.
- Tested out `--enable-deletions` again, which caused issues for `XD`. This confirms that using deletions is still ineffective for defining breakpoints.
- Add `B.1.631` and `B.1.634` to `sc2rf/mapping.tsv` and as potential clades in the default parameters. These are parents for `XB`.
- Add `B.1.438.1` to `sc2rf/mapping.tsv` and as a otential clade in the default parameters. This is a parent for [`proposed808`](https://github.com/cov-lineages/pango-designation/issues/808).
- Require a recombinant region to have at least one substitution unique to the parent (i.e. diagnostic). This reduces false positives.
- Remove the debugging mode, as it produced overly verbose output. It is more efficient to rerun manually with custom parameters tailored to the kind of debugging required.
- Change parent clade nomenclature from `Omicron/21K` to the more comprehensive `Omicron/BA.1/21K`. This makes it clear which lineage is involved, since it's not always obvious how Nextclade clades map to pango lineages.

#### UShER

- [Issue #63](https://github.com/ktmeaton/ncov-recombinant/issues/63): All UShER rules and output have been removed. First, because the latest releases of nextclade datasets (tag `2022-07-26T12:00:00Z`) have dramatically improved lineage assignment accuracy for recombinants. Second, was to improve runtime and simplicity of the workflow, as UShER adds significantly to runtime.

#### Linelist

- [Issue #30](https://github.com/ktmeaton/ncov-recombinant/issues/30):  Fixed the bug where distinct recombinant lineages would occasionally be grouped into one `cluster_id`. This is due to the new definition for recombinant lineages (see General) section, which now includes parental _lineages_ and have sufficient resolving power.
- [Issue #46](https://github.com/ktmeaton/ncov-recombinant/issues/46): Added new column `parents_subs`, which are the substitutions found in the parental lineages _before_ recombination occurred using the `sars-cov-2-no-recomb` nextclade dataset. Also added new columns: `parents_lineage`, `parents_lineage_confidence`, based on querying `cov-spectrum` for the substitutions found in `parents_subs`.
- [Issue #53](https://github.com/ktmeaton/ncov-recombinant/issues/53): Added new column `cov-spectrum_query` which includes the substitutions that are shared by ALL sequences of the recombinant lineage.
- Added new column `cluster_privates` which includes the private substitutions shared by ALL sequences of the recombinant lineage.
- Renamed `parents` column to `parents_clade`, to differentiate it from the new column `parents_lineage`.

#### Plot

- [Issue #4](https://github.com/ktmeaton/ncov-recombinant/issues/4), [Issue #57](https://github.com/ktmeaton/ncov-recombinant/issues/57): Plot distributions of each parent separately, rather than stacking on one axis. Also plot the substitutions as ticks on the breakpoints figure.

| v0.3.0                                                                                                                                 | v0.4.0                                                                                                                                 |
| -------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| ![breakpoints_clade_v0.3.0](https://raw.githubusercontent.com/ktmeaton/ncov-recombinant/4fbde4b90/images/breakpoints_clade_v0.3.0.png) | ![breakpoints_clade_v0.4.0](https://raw.githubusercontent.com/ktmeaton/ncov-recombinant/4fbde4b90/images/breakpoints_clade_v0.4.0.png) |

- [Issue #46](https://github.com/ktmeaton/ncov-recombinant/issues/46): Plot breakpoints separately by clade _and_ lineage.  In addition, distinct clusters within the same recombinant lineage are noted by including their cluster ID as a suffix. As an example, please see `XM (USA) and X (England)` below. Where the lineage is the same (`XM`), but the breakpoints differ, as do the parental lineages (`BA.2` vs `BA.2.12.1`). These clusters are distinct because `XM (England)` lacks substitutions occurring around position 20000.

|                                                        Clade                                                         |                                                 Lineage                                                 |
|:--------------------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------:|
| ![breakpoints_clade](https://github.com/ktmeaton/ncov-recombinant/raw/432b6b79/images/breakpoints_clade_v0.4.0.png) | ![breakpoints_clade](https://github.com/ktmeaton/ncov-recombinant/raw/432b6b79/images/breakpoints_lineage_v0.4.0.png) |

- [Issue #58](https://github.com/ktmeaton/ncov-recombinant/issues/58):  Fix breakpoint plotting from all lineages to just those observed in the reporting period. Except for the breakpoint plots in `plots_historical`.
- [Issue #59](https://github.com/ktmeaton/ncov-recombinant/issues/59):  Improved error handling of breakpoint plotting when a breakpoint could not be identified by `sc2rf`. This is possible if `nextclade` was the only program to detect recombination (and thus, we have no breakpoint data from `sc2rf`).
- [Issue #64](https://github.com/ktmeaton/ncov-recombinant/issues/64): Improved error handling for when the lag period (ex. 4 weeks) falls outside the range of collection dates (ex. 2 weeks).
- [Issue #65](https://github.com/ktmeaton/ncov-recombinant/issues/65): Improved error handling of distribution plotting when only one sequence is present.
- [Issue #67](https://github.com/ktmeaton/ncov-recombinant/issues/67): Plot legends are placed above the figure and are dynamically sized.

| v0.3.0                                                                                                                                                            | v0.4.0                                                                                                                                                            |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ![lineages_output_v0.3.0](https://raw.githubusercontent.com/ktmeaton/ncov-recombinant/af2f25d3c5e7c1d56244390ee90bec405b23949a/images/lineages_output_v0.3.0.png) | ![lineages_output_v0.4.0](https://raw.githubusercontent.com/ktmeaton/ncov-recombinant/af2f25d3c5e7c1d56244390ee90bec405b23949a/images/lineages_output_v0.4.0.png) |

#### Report

- [Issue #60](https://github.com/ktmeaton/ncov-recombinant/issues/60): Remove changelog from final slide, as this content did not display correctly
- [Issue #61](https://github.com/ktmeaton/ncov-recombinant/issues/61):  Fixed bug in the `report.xlsx` where the number of proposed and unpublished recombinant lineages/sequences was incorrect.

#### Validation

- [Issue #58](https://github.com/ktmeaton/ncov-recombinant/issues/58): New rule (`validate`) to validate the number of positives in controlled datasets (ex. controls, tutorials) against `defaults/validation.tsv`. If validation fails based on an incorrect number of positives, the pipeline will exit with an error. This is to make it more obvious when results have changed during Continuous Integration (CI)

### Pull Requests

- [```pull/44```](https://github.com/ktmeaton/ncov-recombinant/pull/44) Breakpoint plotting

### Commits

- [```c027027b```](https://github.com/ktmeaton/ncov-recombinant/commit/c027027b) docs: remove dev notes
- [```77d9f01b```](https://github.com/ktmeaton/ncov-recombinant/commit/77d9f01b) ci: remove unit test workflow
- [```574f8c15```](https://github.com/ktmeaton/ncov-recombinant/commit/574f8c15) docs: update instructions in README
- [```79b61fe2```](https://github.com/ktmeaton/ncov-recombinant/commit/79b61fe2) ci: remove unit tests
- [```3d53ebd2```](https://github.com/ktmeaton/ncov-recombinant/commit/3d53ebd2) docs: update notes for v0.4.0
- [```b968dc6d```](https://github.com/ktmeaton/ncov-recombinant/commit/b968dc6d) script: add more subs columns to lineages linelist
- [```75477ec4```](https://github.com/ktmeaton/ncov-recombinant/commit/75477ec4) script: adjust lag epiweek by 1 when overlaps
- [```20409f5c```](https://github.com/ktmeaton/ncov-recombinant/commit/20409f5c) sc2rf: mapping change 22C to BA.2.12.1 and add 22D
- [```432b6b79```](https://github.com/ktmeaton/ncov-recombinant/commit/432b6b79) docs: add breakpoints lineage output for v0.4.0
- [```4fbde4b9```](https://github.com/ktmeaton/ncov-recombinant/commit/4fbde4b9) docs: add breakts output image to compare v0.3.0 and v0.4.0
- [```af2f25d3```](https://github.com/ktmeaton/ncov-recombinant/commit/af2f25d3) docs: add lineage output image for v0.4.0 to compare
- [```5615f113```](https://github.com/ktmeaton/ncov-recombinant/commit/5615f113) docs: add lineage output image for v0.3.0 to compare
- [```57a08096```](https://github.com/ktmeaton/ncov-recombinant/commit/57a08096) profile: adjust plotting min and max dates for tutorial
- [```4226c85b```](https://github.com/ktmeaton/ncov-recombinant/commit/4226c85b) script: mark nextclade recombinants unverified by sc2rf as false positives
- [```d6700e7a```](https://github.com/ktmeaton/ncov-recombinant/commit/d6700e7a) docs: rearrange sections in README
- [```7f773ba7```](https://github.com/ktmeaton/ncov-recombinant/commit/7f773ba7) docs: update report and slides images and links
- [```3599a7f4```](https://github.com/ktmeaton/ncov-recombinant/commit/3599a7f4) script: don't use proposed* lineages from sc2rf as consensus lineage
- [```76106b50```](https://github.com/ktmeaton/ncov-recombinant/commit/76106b50) docs: add new image for lineages plot
- [```86c2fa2e```](https://github.com/ktmeaton/ncov-recombinant/commit/86c2fa2e) docs: update README and images
- [```488ea6c7```](https://github.com/ktmeaton/ncov-recombinant/commit/488ea6c7) script: dynamic legends for #67
- [```bec01845```](https://github.com/ktmeaton/ncov-recombinant/commit/bec01845) script: move plot legend to top for #67
- [```42d1281b```](https://github.com/ktmeaton/ncov-recombinant/commit/42d1281b) script: make sure X*-like lineages have proposed status
- [```230f9495```](https://github.com/ktmeaton/ncov-recombinant/commit/230f9495) resources: update issues
- [```3c2f4c84```](https://github.com/ktmeaton/ncov-recombinant/commit/3c2f4c84) script: detect novel recombinants based on private mutations
- [```d9e279be```](https://github.com/ktmeaton/ncov-recombinant/commit/d9e279be) resources: update breakpoints for XAF and XAG
- [```2d070cb2```](https://github.com/ktmeaton/ncov-recombinant/commit/2d070cb2) script: improve linelist efficiency for assigning cluster ids
- [```b65437f2```](https://github.com/ktmeaton/ncov-recombinant/commit/b65437f2) script: add create_logger function to general functions import
- [```489154f6```](https://github.com/ktmeaton/ncov-recombinant/commit/489154f6) sc2rf: explicitly call variables \_primary and \_secondary
- [```8f464a14```](https://github.com/ktmeaton/ncov-recombinant/commit/8f464a14) script: simplify extra columns for summary script
- [```30f90443```](https://github.com/ktmeaton/ncov-recombinant/commit/30f90443) workflow: formally run sc2rf in primary/secondary mode in parallel
- [```6688c828```](https://github.com/ktmeaton/ncov-recombinant/commit/6688c828) defaults: restore validation counts for XN and XP
- [```043b691e```](https://github.com/ktmeaton/ncov-recombinant/commit/043b691e) script: add special processing for XN and XP
- [```939cc967```](https://github.com/ktmeaton/ncov-recombinant/commit/939cc967) script: only adjust lineage status in linelist if positive
- [```28d91363```](https://github.com/ktmeaton/ncov-recombinant/commit/28d91363) dataset: update tutorial strains for #49
- [```09e53a94```](https://github.com/ktmeaton/ncov-recombinant/commit/09e53a94) workflow: remove usher for #63
- [```22c63de0```](https://github.com/ktmeaton/ncov-recombinant/commit/22c63de0) workflow: add XAK to controls for Issue #62
- [```342fa2a3```](https://github.com/ktmeaton/ncov-recombinant/commit/342fa2a3) script: create separate slides for designated, proposed, and unpublished for issue #61
- [```84c9b57d```](https://github.com/ktmeaton/ncov-recombinant/commit/84c9b57d) script: create separate plots for designated, proposed, and unpublished for issue #61
- [```81c58931```](https://github.com/ktmeaton/ncov-recombinant/commit/81c58931) script: if lineage is proposed* use as curated lineage rather than cluster_id
- [```2db6100b```](https://github.com/ktmeaton/ncov-recombinant/commit/2db6100b) ci: fix typo in profile creation job names
- [```18102431```](https://github.com/ktmeaton/ncov-recombinant/commit/18102431) script: remove changelog from report slides for issue #60
- [```b7784b30```](https://github.com/ktmeaton/ncov-recombinant/commit/b7784b30) docs: use new breakpoints path for README
- [```66ee7d1d```](https://github.com/ktmeaton/ncov-recombinant/commit/66ee7d1d) nextclade: upgrade datasets to tag 2022-07-26 for issue #50
- [```7880327c```](https://github.com/ktmeaton/ncov-recombinant/commit/7880327c) ci: don't trigger pipeline on images changes
- [```e8c71171```](https://github.com/ktmeaton/ncov-recombinant/commit/e8c71171) docs: update breakpoints images
- [```e13138e8```](https://github.com/ktmeaton/ncov-recombinant/commit/e13138e8) script: rename NA to Unknown parent when plotting breakpoints
- [```fc1b6129```](https://github.com/ktmeaton/ncov-recombinant/commit/fc1b6129) script: remove unneeded constants in plot
- [```77d3614a```](https://github.com/ktmeaton/ncov-recombinant/commit/77d3614a) dataset: change controls proposed771 to XAN
- [```f2d72330```](https://github.com/ktmeaton/ncov-recombinant/commit/f2d72330) script: catch empty plot when using tight_layout for breakpoints
- [```b55dbe95```](https://github.com/ktmeaton/ncov-recombinant/commit/b55dbe95) workflow: include unpublished in positive status for rule validate
- [```557295b5```](https://github.com/ktmeaton/ncov-recombinant/commit/557295b5) script: plotting catch when breakpoints are NA
- [```2306305d```](https://github.com/ktmeaton/ncov-recombinant/commit/2306305d) profile: set exclusions for tutorial to default
- [```c049ccba```](https://github.com/ktmeaton/ncov-recombinant/commit/c049ccba) resource: update curated breakpoints
- [```218bab52```](https://github.com/ktmeaton/ncov-recombinant/commit/218bab52) env: upgrade nextclade to v2.3.0 for issue #50
- [```a9ea0bd4```](https://github.com/ktmeaton/ncov-recombinant/commit/a9ea0bd4) workflow: fix typo in rule validate that hard-coded controls
- [```cf613c34```](https://github.com/ktmeaton/ncov-recombinant/commit/cf613c34) workflow: control breakpoint plotting by clusters file
- [```0d4b50a4```](https://github.com/ktmeaton/ncov-recombinant/commit/0d4b50a4) resource: update breakpoints figures
- [```6520457a```](https://github.com/ktmeaton/ncov-recombinant/commit/6520457a) script: plot subs along with breakpoints for issue #57
- [```8110faa7```](https://github.com/ktmeaton/ncov-recombinant/commit/8110faa7) script: create a plot for cluster_id mostly for breakpoint plotting
- [```6f02f09c```](https://github.com/ktmeaton/ncov-recombinant/commit/6f02f09c) script: for plot import function categorical_palette
- [```1f6195df```](https://github.com/ktmeaton/ncov-recombinant/commit/1f6195df) profile: by default do not retry jobs
- [```2842a4f9```](https://github.com/ktmeaton/ncov-recombinant/commit/2842a4f9) workflow: add rule validate for issue #56
- [```693b07df```](https://github.com/ktmeaton/ncov-recombinant/commit/693b07df) script: empty df catching in plot breakpoints
- [```12567fde```](https://github.com/ktmeaton/ncov-recombinant/commit/12567fde) workflow: classify any sequence with unlabeled private mutations as a potential positive
- [```534ac899```](https://github.com/ktmeaton/ncov-recombinant/commit/534ac899) docs: add more comments to summary script
- [```82b6a696```](https://github.com/ktmeaton/ncov-recombinant/commit/82b6a696) script: fix bug in parent palette for plot breakpoints
- [```42510719```](https://github.com/ktmeaton/ncov-recombinant/commit/42510719) config: remove explicit conda activation in slurm script and profiles
- [```ab44e5d7```](https://github.com/ktmeaton/ncov-recombinant/commit/ab44e5d7) docs: update readme contributors
- [```e8e2b134```](https://github.com/ktmeaton/ncov-recombinant/commit/e8e2b134) dataset: upgrade nextclade dataset
- [```086768c7```](https://github.com/ktmeaton/ncov-recombinant/commit/086768c7) parameters: restrict breakpoints and parents to 10 for sc2rf
- [```83af3a73```](https://github.com/ktmeaton/ncov-recombinant/commit/83af3a73) sc2rf: output NA for false positives breakpoints
- [```4baee0de```](https://github.com/ktmeaton/ncov-recombinant/commit/4baee0de) script: catch empty dataframe in script plot
- [```1dc84bf6```](https://github.com/ktmeaton/ncov-recombinant/commit/1dc84bf6) profile: adjust plot end date for positive controls
- [```be431cdf```](https://github.com/ktmeaton/ncov-recombinant/commit/be431cdf) workflow: restrict nextclade clades again
- [```76e31f68```](https://github.com/ktmeaton/ncov-recombinant/commit/76e31f68) resources: add breakpoints by clade
- [```07d96a1e```](https://github.com/ktmeaton/ncov-recombinant/commit/07d96a1e) workflow: fix bug in plot_historical
- [```2086b254```](https://github.com/ktmeaton/ncov-recombinant/commit/2086b254) sc2rf: update lineage mapping
- [```0d911b20```](https://github.com/ktmeaton/ncov-recombinant/commit/0d911b20) env: reorganize dependencies
- [```c165074b```](https://github.com/ktmeaton/ncov-recombinant/commit/c165074b) workflow: separate plot_breakpoints into separate script
- [```0497dffd```](https://github.com/ktmeaton/ncov-recombinant/commit/0497dffd) profile: controls-negative include false positives
- [```8bb41c45```](https://github.com/ktmeaton/ncov-recombinant/commit/8bb41c45) script: add separate report slides for clade/lineage parent breakpoints
- [```411bc235```](https://github.com/ktmeaton/ncov-recombinant/commit/411bc235) workflow: remove subtree params and add secondary clades
- [```f80386aa```](https://github.com/ktmeaton/ncov-recombinant/commit/f80386aa) sc2rf: catch empty secondary csv
- [```6d1b03e0```](https://github.com/ktmeaton/ncov-recombinant/commit/6d1b03e0) sc2rf: add optional secondary csv for #51
- [```a629eb06```](https://github.com/ktmeaton/ncov-recombinant/commit/a629eb06) workflow: detect recombination with BA.5 for #51
- [```c44b468a```](https://github.com/ktmeaton/ncov-recombinant/commit/c44b468a) env: remove plotly and kaleido from env
- [```a485215d```](https://github.com/ktmeaton/ncov-recombinant/commit/a485215d) dataset: add proposed771 to controls for #51
- [```eba827a9```](https://github.com/ktmeaton/ncov-recombinant/commit/eba827a9) script: define lineages by parental lineages for #46
- [```d6319bad```](https://github.com/ktmeaton/ncov-recombinant/commit/d6319bad) workflow: relax nextclade exclusion filter for #48
- [```fb7a0a4f```](https://github.com/ktmeaton/ncov-recombinant/commit/fb7a0a4f) env: upgrade nextclade to v2.2.0 for #50
- [```31ec45be```](https://github.com/ktmeaton/ncov-recombinant/commit/31ec45be) resources: update breakpoints parents nomenclature
- [```7f00564d```](https://github.com/ktmeaton/ncov-recombinant/commit/7f00564d) (unverified) sc2rf,postprocess: add unique_subs to output
- [```3e3e46c2```](https://github.com/ktmeaton/ncov-recombinant/commit/3e3e46c2) workflow: implement cov-spectrum query to identify parent lineages
- [```041de538```](https://github.com/ktmeaton/ncov-recombinant/commit/041de538) workflow: customize nextclade to run with our without recombinant dataset
- [```7acc598f```](https://github.com/ktmeaton/ncov-recombinant/commit/7acc598f) script: remove edges from stacked bar plots for issue #43
- [```ab589bb7```](https://github.com/ktmeaton/ncov-recombinant/commit/ab589bb7) docs: add mark horsman for ideas and design
- [```151e481d```](https://github.com/ktmeaton/ncov-recombinant/commit/151e481d) bug: fix svg font export for issues #42
- [```b34c1452```](https://github.com/ktmeaton/ncov-recombinant/commit/b34c1452) bug: fix ouput typo in issues_download
- [```601a0c7a```](https://github.com/ktmeaton/ncov-recombinant/commit/601a0c7a) resources: also output svg for issues breakpoints
- [```a2a8b00d```](https://github.com/ktmeaton/ncov-recombinant/commit/a2a8b00d) workflow: add plotting issues breakpoints to rule issues_download
- [```5a5a2f41```](https://github.com/ktmeaton/ncov-recombinant/commit/5a5a2f41) resources: update breakpoints plot
- [```2113f6f9```](https://github.com/ktmeaton/ncov-recombinant/commit/2113f6f9) script: plot breakpoints of curate lineages in resources
- [```5f4b901d```](https://github.com/ktmeaton/ncov-recombinant/commit/5f4b901d) docs: add new breakpoints image to readme
- [```bfdf2191```](https://github.com/ktmeaton/ncov-recombinant/commit/bfdf2191) workflow: cleanup Thumbs
- [```869f3b4e```](https://github.com/ktmeaton/ncov-recombinant/commit/869f3b4e) script: add breakpoints as a plot and report slide
- [```e988f251```](https://github.com/ktmeaton/ncov-recombinant/commit/e988f251) bug: fix missing rule\_name for _historical
- [```8bc6aef4```](https://github.com/ktmeaton/ncov-recombinant/commit/8bc6aef4) env: add plotly and kaleido to env
- [```066e0c00```](https://github.com/ktmeaton/ncov-recombinant/commit/066e0c00) resources: add 781 789 798 to curated breakpoints
- [```4ff587c5```](https://github.com/ktmeaton/ncov-recombinant/commit/4ff587c5) resources: update issues and curated breakpoints
- [```cc146425```](https://github.com/ktmeaton/ncov-recombinant/commit/cc146425) docs: add instructions for updating conda env
- [```8592a156```](https://github.com/ktmeaton/ncov-recombinant/commit/8592a156) bug: fix usher_collapse metadata output to allow for hCoV-19 prefix
- [```9ea4f1b3```](https://github.com/ktmeaton/ncov-recombinant/commit/9ea4f1b3) docs: add --recurse-submodules instruction to updating

## v0.3.0

### Notes

#### Major Changes

1. Default parameters have been updated! Please regenerate your profiles/builds with:

    ```bash
    bash scripts/create_profile.sh --data data/custom
    ```

1. Rule outputs are now in sub-directories for a cleaner `results` directory.
1. The in-text report (`report.pptx`) statistics are no longer cumulative counts of all sequences. Instead they, will match the reporting period in the accompanying plots.

#### Bug Fixes

1. Improve subtree collapse effiency (#35).
1. Improve subtree aesthetics and filters (#20).
1. Fix issues rendering as float (#29).
1. Explicitly control the dimensions of plots for powerpoint embedding.
1. Remove hard-coded `extra_cols` (#26).
1. Fix mismatch in lineages plot and description (#21).
1. Downstream steps no longer fail if there are no recombinant sequences (#7).

#### Workflow

1. Add new rule `usher_columns` to augment the base usher metadata.
1. Add new script `parents.py`, plots, and report slide to summarize recombinant sequences by parent.
1. Make rules `plot` and `report` more dynamic with regards to plots creation.
1. Exclude the reference genome from alignment until `faToVcf`.
1. Include the log path and expected outputs in the message for each rule.
1. Use sub-functions to better control optional parameters.
1. Make sure all rules write to a log if possible (#34).
1. Convert all rule inputs to snakemake rule variables.
1. Create and document a `create_profile.sh` script.
1. Implement the `--low-memory` mode parameter within the script `usher_metadata.sh`.

#### Data

1. Create new controls datasets:

    - `controls-negatives`
    - `controls-positives`
    - `controls`

1. Add versions to `genbank_accessions` for `controls`.

#### Programs

1. Upgrade UShER to v0.5.4 (possibly this was done in a prior ver).
1. Remove `taxonium` and `chronumental` from the conda env.

#### Parameters

1. Add parameters to control whether negatives and false_positives should be excluded:

    - `exclude_negatives: false`
    - `false_positives: false`

1. Add new optional param `max_placements` to rule `linelist`.
1. Remove `--show-private-mutations` from `debug_args` of rule `sc2rf`.
1. Add optional param `--sc2rf-dir` to `sc2rf` to enable execution outside of `sc2rf` dir.
1. Add params `--output-csv` and `--output-ansi` to the wrapper `scripts/sc2rf.sh`.
1. Remove params `nextclade_ref` and `custom_ref` from rule `nextclade`.
1. Change `--breakpoints 0-10` in `sc2rf`.

#### Continuous Integration

1. Re-rename tutorial action to pipeline, and add different jobs for different profiles:

    - Tutorial
    - Controls (Positive)
    - Controls (Negative)
    - Controls (All)

#### Output

1. Output new `_historical` plots and slides for plotting all data over time.
1. Output new file `parents.tsv` to summarize recombinant sequences by parent.
1. Order the colors/legend of the stacked bar `plots` by number of sequences.
1. Include lineage and cluster id in filepaths of largest plots and tables.
1. Rename the linelist output:

    - `linelist.tsv`
    - `positives.tsv`  
    - `negatives.tsv`
    - `false_positives.tsv`
    - `lineages.tsv`
    - `parents.tsv`

1. The `report.xlsx` now includes the following tables:

    - lineages
    - parents
    - linelist
    - positives
    - negatives
    - false_positives
    - summary
    - issues

### Pull Requests

- [```pull/15```](https://github.com/ktmeaton/ncov-recombinant/pull/15) New rule: parents
- [```pull/19```](https://github.com/ktmeaton/ncov-recombinant/pull/19) docs: add lenaschimmel as a contributor for code
- [```pull/40```](https://github.com/ktmeaton/ncov-recombinant/pull/40) v0.3.0 stability update part 2
- [```pull/39```](https://github.com/ktmeaton/ncov-recombinant/pull/39) v0.3.0 stability update

### Commits

- [```2f8b498a```](https://github.com/ktmeaton/ncov-recombinant/commit/2f8b498a) docs: update changelog for v0.3.0
- [```0486d3be```](https://github.com/ktmeaton/ncov-recombinant/commit/0486d3be) docs: add updating section to readme for issue #33
- [```e8eda400```](https://github.com/ktmeaton/ncov-recombinant/commit/e8eda400) resources: updates issues with curate breakpoints
- [```12e3700f```](https://github.com/ktmeaton/ncov-recombinant/commit/12e3700f) bug: catch empty dataframe in plot
- [```d1ccca2a```](https://github.com/ktmeaton/ncov-recombinant/commit/d1ccca2a) workflow: first successful high-throughput run
- [```cd741a10```](https://github.com/ktmeaton/ncov-recombinant/commit/cd741a10) workflow: add new rules plot_historical and report_historical
- [```c2cc1380```](https://github.com/ktmeaton/ncov-recombinant/commit/c2cc1380) env: remove openpyxl from environment
- [```7dc7c039```](https://github.com/ktmeaton/ncov-recombinant/commit/7dc7c039) workflow: remove rule report_redact #31
- [```9ca5f822```](https://github.com/ktmeaton/ncov-recombinant/commit/9ca5f822) script: rearrange merge file order in summary
- [```aa28eb9f```](https://github.com/ktmeaton/ncov-recombinant/commit/aa28eb9f) workflow: create new rule report_redact for #31
- [```4748815d```](https://github.com/ktmeaton/ncov-recombinant/commit/4748815d) env: add openpyxl to environment for excel parsing in python
- [```0060904a```](https://github.com/ktmeaton/ncov-recombinant/commit/0060904a) script: template duplicate labelling in usher_collapse for later
- [```a82359a7```](https://github.com/ktmeaton/ncov-recombinant/commit/a82359a7) data: add accession versions to controls metadata
- [```af7341aa```](https://github.com/ktmeaton/ncov-recombinant/commit/af7341aa) data: add accession versions to controls metadata
- [```d860a4c8```](https://github.com/ktmeaton/ncov-recombinant/commit/d860a4c8) workflow: add new rule usher_columns to augment the base usher metadata
- [```2511673d```](https://github.com/ktmeaton/ncov-recombinant/commit/2511673d) improve subtree collapse effiency (#35) and output aesthetics (#20)
- [```1e81be3b```](https://github.com/ktmeaton/ncov-recombinant/commit/1e81be3b) bug: remove non-existant param --log in rule usher_metadata
- [```02198b4c```](https://github.com/ktmeaton/ncov-recombinant/commit/02198b4c) script: add logging to usher_collapse
- [```d40d3d78```](https://github.com/ktmeaton/ncov-recombinant/commit/d40d3d78) ci: don't run pipeline just for images changes
- [```b880d9c8```](https://github.com/ktmeaton/ncov-recombinant/commit/b880d9c8) docs: update powerpoint image to proper ver
- [```2d6514a0```](https://github.com/ktmeaton/ncov-recombinant/commit/2d6514a0) docs: update demo excel and slides with links and content
- [```59c24ffe```](https://github.com/ktmeaton/ncov-recombinant/commit/59c24ffe) bug: fix typo that prevented low_memory_mode from activating
- [```4d94df1d```](https://github.com/ktmeaton/ncov-recombinant/commit/4d94df1d) bug: continue supply missing build param to _params_ functions
- [```c16c3377```](https://github.com/ktmeaton/ncov-recombinant/commit/c16c3377) bug: supply missing build param to _params_linelist
- [```c31c2204```](https://github.com/ktmeaton/ncov-recombinant/commit/c31c2204) docs: remove plotting data table from FAQ
- [```5461cbf2```](https://github.com/ktmeaton/ncov-recombinant/commit/5461cbf2) docs: describe how to include more custom metadata columns
- [```7295c8c0```](https://github.com/ktmeaton/ncov-recombinant/commit/7295c8c0) script: implement low memory mode within usher_metadata script
- [```6588f619```](https://github.com/ktmeaton/ncov-recombinant/commit/6588f619) workflow: restore original config merge logic
- [```ae96cf3d```](https://github.com/ktmeaton/ncov-recombinant/commit/ae96cf3d) docs: rearrange sections in README
- [```e99cdef9```](https://github.com/ktmeaton/ncov-recombinant/commit/e99cdef9) docs: add tips for speeding up usher in FAQ
- [```753d1e1d```](https://github.com/ktmeaton/ncov-recombinant/commit/753d1e1d) resources: add proposed759 to curated breakpoints
- [```1ea5610e```](https://github.com/ktmeaton/ncov-recombinant/commit/1ea5610e) docs: change troubleshooting section to FAQ
- [```42152710```](https://github.com/ktmeaton/ncov-recombinant/commit/42152710) workflow: add logging to sc2rf_recombinants for issue #34
- [```ca930fe3```](https://github.com/ktmeaton/ncov-recombinant/commit/ca930fe3) bug: fix status of designated recombinants missed by sc2rf (XB)
- [```2c6102a6```](https://github.com/ktmeaton/ncov-recombinant/commit/2c6102a6) script: in plotting data replace counts that are empty string with 0
- [```0c7fa988```](https://github.com/ktmeaton/ncov-recombinant/commit/0c7fa988) docs: tidy up comments in default parameters.yaml
- [```43c61d43```](https://github.com/ktmeaton/ncov-recombinant/commit/43c61d43) bug: fix sc2rf postprocessing bug where sequences with only parent were missing filtered regions
- [```6a00c866```](https://github.com/ktmeaton/ncov-recombinant/commit/6a00c866) ci: split jobs by profile for testing profile creation (#27)
- [```aeabf009```](https://github.com/ktmeaton/ncov-recombinant/commit/aeabf009) ci: add new action profile_creation to test script create_profile.sh
- [```9a6758e2```](https://github.com/ktmeaton/ncov-recombinant/commit/9a6758e2) add controls section to README
- [```ef250a22```](https://github.com/ktmeaton/ncov-recombinant/commit/ef250a22) script: add -controls suffix to profiles created with --controls param
- [```150a3e17```](https://github.com/ktmeaton/ncov-recombinant/commit/150a3e17) docs: update troubleshooting section
- [```90b406c8```](https://github.com/ktmeaton/ncov-recombinant/commit/90b406c8) script: remove --partition flag to scripts/slurm.sh
- [```a0c6ece2```](https://github.com/ktmeaton/ncov-recombinant/commit/a0c6ece2) docs: update google drive link to example slides
- [```a37afeea```](https://github.com/ktmeaton/ncov-recombinant/commit/a37afeea) docs: update instructions for create_profile.sh
- [```f9d050d2```](https://github.com/ktmeaton/ncov-recombinant/commit/f9d050d2) add execute permissions to scripts
- [```38b5b422```](https://github.com/ktmeaton/ncov-recombinant/commit/38b5b422) bug: use a full loop to check issue formatting
- [```307b4f67```](https://github.com/ktmeaton/ncov-recombinant/commit/307b4f67) catch issues list when converting to str
- [```639f8c26```](https://github.com/ktmeaton/ncov-recombinant/commit/639f8c26) bug: fix issues rendering as float in tables for issue #29
- [```35ea4be1```](https://github.com/ktmeaton/ncov-recombinant/commit/35ea4be1) remove param --sc2rf-dir from scripts/sc2rf.sh
- [```5a2a9520```](https://github.com/ktmeaton/ncov-recombinant/commit/5a2a9520) docs: update images for excel and powerpoint
- [```3ae737d5```](https://github.com/ktmeaton/ncov-recombinant/commit/3ae737d5) env: comment out yarn which is a dev dependency
- [```3842e898```](https://github.com/ktmeaton/ncov-recombinant/commit/3842e898) improve logging in create_profile
- [```84c684ca```](https://github.com/ktmeaton/ncov-recombinant/commit/84c684ca) workflow: separate profiles for controls,controls-positive,controls-negative
- [```ad5e8e4b```](https://github.com/ktmeaton/ncov-recombinant/commit/ad5e8e4b) limit missing strains output from create_profile
- [```a4898ecf```](https://github.com/ktmeaton/ncov-recombinant/commit/a4898ecf) docs: update development notes
- [```34ee2fff```](https://github.com/ktmeaton/ncov-recombinant/commit/34ee2fff) docs: add links to contributors plugins
- [```b6b0c999```](https://github.com/ktmeaton/ncov-recombinant/commit/b6b0c999) revert to automated all-contributors
- [```e1a248f8```](https://github.com/ktmeaton/ncov-recombinant/commit/e1a248f8) add @yatisht and @AngieHinrichs to credits for usher
- [```e3f432c4```](https://github.com/ktmeaton/ncov-recombinant/commit/e3f432c4) start adding contributors
- [```862757bd```](https://github.com/ktmeaton/ncov-recombinant/commit/862757bd) docs: create .all-contributorsrc [skip ci]
- [```a0532792```](https://github.com/ktmeaton/ncov-recombinant/commit/a0532792) docs: update README.md [skip ci]
- [```6e67e73f```](https://github.com/ktmeaton/ncov-recombinant/commit/6e67e73f) update unpublished regex to solve #21
- [```5ba6b37b```](https://github.com/ktmeaton/ncov-recombinant/commit/5ba6b37b) remove taxonium and chronumental from env
- [```2a5fc627```](https://github.com/ktmeaton/ncov-recombinant/commit/2a5fc627) add artifacts for all pipelines
- [```664b2e9b```](https://github.com/ktmeaton/ncov-recombinant/commit/664b2e9b) fix trailing whitespace in metadata
- [```eada2fa3```](https://github.com/ktmeaton/ncov-recombinant/commit/eada2fa3) fix negative controls metadata
- [```9aecd69a```](https://github.com/ktmeaton/ncov-recombinant/commit/9aecd69a) fix plot dimensions for pptx embed
- [```657e8838```](https://github.com/ktmeaton/ncov-recombinant/commit/657e8838) fix outdir for linelist
- [```6fb389dc```](https://github.com/ktmeaton/ncov-recombinant/commit/6fb389dc) fix input type for controls build
- [```8ed69ce0```](https://github.com/ktmeaton/ncov-recombinant/commit/8ed69ce0) upload tutorial pptx as artifact
- [```c6e647d2```](https://github.com/ktmeaton/ncov-recombinant/commit/c6e647d2) update ci profile for test action
- [```19cdb8ed```](https://github.com/ktmeaton/ncov-recombinant/commit/19cdb8ed) lint pipeline
- [```22e3aa6b```](https://github.com/ktmeaton/ncov-recombinant/commit/22e3aa6b) split controls action into positives,negatives,and all
- [```33491320```](https://github.com/ktmeaton/ncov-recombinant/commit/33491320) rename action Tutorial to Pipeline
- [```da2890d6```](https://github.com/ktmeaton/ncov-recombinant/commit/da2890d6) fix profile in install action
- [```8a4d4fbb```](https://github.com/ktmeaton/ncov-recombinant/commit/8a4d4fbb) lint all files
- [```b167ea45```](https://github.com/ktmeaton/ncov-recombinant/commit/b167ea45) update readme with profile creation instructions
- [```4d2848b9```](https://github.com/ktmeaton/ncov-recombinant/commit/4d2848b9) add script to generate new profiles and builds
- [```407f8aba```](https://github.com/ktmeaton/ncov-recombinant/commit/407f8aba) checkpoint before auto-generating builds
- [```ccb3471b```](https://github.com/ktmeaton/ncov-recombinant/commit/ccb3471b) add new negatives dataset
- [```964a22f8```](https://github.com/ktmeaton/ncov-recombinant/commit/964a22f8) (broken) script overhaul
- [```1f1ca1b4```](https://github.com/ktmeaton/ncov-recombinant/commit/1f1ca1b4) add param --sc2rf-dir to allow execution outside of main directory
- [```21541f02```](https://github.com/ktmeaton/ncov-recombinant/commit/21541f02) add exclude_negatives and exclude_false_positives to parameters
- [```0b5854a2```](https://github.com/ktmeaton/ncov-recombinant/commit/0b5854a2) update docs
- [```58b6396a```](https://github.com/ktmeaton/ncov-recombinant/commit/58b6396a) split controls data into positives and negatives
- [```11f9f6a4```](https://github.com/ktmeaton/ncov-recombinant/commit/11f9f6a4) consolidate positives and negatives profiles into controls
- [```581255c8```](https://github.com/ktmeaton/ncov-recombinant/commit/581255c8) generalize hpc profiles
- [```1e2a70a4```](https://github.com/ktmeaton/ncov-recombinant/commit/1e2a70a4) update HPC instructions in README
- [```a18b19e3```](https://github.com/ktmeaton/ncov-recombinant/commit/a18b19e3) (broken) add negatives data and profile
- [```11817639```](https://github.com/ktmeaton/ncov-recombinant/commit/11817639) (broken) make plots and report dynamic
- [```e833d151```](https://github.com/ktmeaton/ncov-recombinant/commit/e833d151) create tutorial-hpc profile
- [```c4ac5699```](https://github.com/ktmeaton/ncov-recombinant/commit/c4ac5699) remove redundant profile laptop
- [```c5107017```](https://github.com/ktmeaton/ncov-recombinant/commit/c5107017) remove ci profile
- [```4be07e79```](https://github.com/ktmeaton/ncov-recombinant/commit/4be07e79) actually rename pipeline to tutorial
- [```89c4d6b5```](https://github.com/ktmeaton/ncov-recombinant/commit/89c4d6b5) rename pipeline action to tutorial
- [```7614b399```](https://github.com/ktmeaton/ncov-recombinant/commit/7614b399) exclude alpha beta gamma by default from Nextclade
- [```d2c2461c```](https://github.com/ktmeaton/ncov-recombinant/commit/d2c2461c) update dev docs
- [```f9368d11```](https://github.com/ktmeaton/ncov-recombinant/commit/f9368d11) remove proposed636 which is now XZ
- [```4fbd0ce4```](https://github.com/ktmeaton/ncov-recombinant/commit/4fbd0ce4) add XAA and XAB to resources
- [```65efd145```](https://github.com/ktmeaton/ncov-recombinant/commit/65efd145) add xz to resources
- [```f3641b19```](https://github.com/ktmeaton/ncov-recombinant/commit/f3641b19) add parents slide to report and excel
- [```4e25f665```](https://github.com/ktmeaton/ncov-recombinant/commit/4e25f665) add new script parents to summarize recombinants by parent
- [```0decd47a```](https://github.com/ktmeaton/ncov-recombinant/commit/0decd47a) catch when no designated sequences are present
- [```189fbb2a```](https://github.com/ktmeaton/ncov-recombinant/commit/189fbb2a) update resources breakpoints
- [```3c5b4965```](https://github.com/ktmeaton/ncov-recombinant/commit/3c5b4965) update sc2rf with new logic for terminal deletions
- [```e37d68d9```](https://github.com/ktmeaton/ncov-recombinant/commit/e37d68d9) update issues and breakpoints
- [```761d41bf```](https://github.com/ktmeaton/ncov-recombinant/commit/761d41bf) use date in changelog for report
- [```3c486dbc```](https://github.com/ktmeaton/ncov-recombinant/commit/3c486dbc) add zip to environment
- [```1ff37195```](https://github.com/ktmeaton/ncov-recombinant/commit/1ff37195) add more info about system config

## v0.2.1

### Notes

#### Params

1. New optional param `motifs` for rule `sc2rf_recombinants`.
1. New param `weeks` for new rule `plot`.
1. Removed `prev_linelist` param.

#### Output

1. Switch from a pdf `report` to powerpoint slides for better automation.
1. Create summary plots.
1. Split `report` rule into `linelist` and `report`.
1. Output `svg` plots.

#### Workflow

1. New rule `plot`.
1. Changed growth calculation from a comparison to the previous week to a score of sequences per day.
1. Assign a `cluster_id` according to the first sequence observed in the recombinant lineage.
1. Define a recombinant lineage as a group of sequences that share the same:
    - Lineage assignment
    - Parents
    - Breakpoints or phylogenetic placement (subtree)
1. For some sequences, the breakpoints are inaccurate and shifted slightly due to ambiguous bases. These sequences can be assigned to their corresponding cluster because they belong to the same subtree.
1. For some lineages, global prevalence has exceeded 500 sequences (which is the subtree size used). Sequences of these lineages are split into different subtrees. However, they can be assigned to the correct cluster/lineage, because they have the same breakpoints.
1. Confirmed not to use deletions define recombinants and breakpoints (differs from published)?

#### Programs

1. Move `sc2rf_recombinants.py` to `postprocess.py` in ktmeaton fork of `sc2rf`.
1. Add false positives filtering to `sc2rf_recombinants` based on parents and breakpoints.

#### Docs

1. Add section `Configuration` to `README.md`.

### Pull Requests

- [```pull/14```](https://github.com/ktmeaton/ncov-recombinant/pull/14) Plots and PowerPoints

### Commits

- [```c2369c75```](https://github.com/ktmeaton/ncov-recombinant/commit/c2369c75) update CHANGELOG after README overhaul
- [```9c8a774e```](https://github.com/ktmeaton/ncov-recombinant/commit/9c8a774e) update autologs to exclude first blank line in notes
- [```2a8a7af5```](https://github.com/ktmeaton/ncov-recombinant/commit/2a8a7af5) overhaul README
- [```9c2bd2f5```](https://github.com/ktmeaton/ncov-recombinant/commit/9c2bd2f5) change asterisks to dashes
- [```46d4ec81```](https://github.com/ktmeaton/ncov-recombinant/commit/46d4ec81) update autologs to allow more complex notes content
- [```a01a903c```](https://github.com/ktmeaton/ncov-recombinant/commit/a01a903c) split docs into dev and todo
- [```23e8d715```](https://github.com/ktmeaton/ncov-recombinant/commit/23e8d715) change color palette for plotting
- [```785b8a19```](https://github.com/ktmeaton/ncov-recombinant/commit/785b8a19) add optional param motifs for sc2rf_recombinants
- [```d1c1559e```](https://github.com/ktmeaton/ncov-recombinant/commit/d1c1559e) restore pptx template to regular view
- [```6adc5d32```](https://github.com/ktmeaton/ncov-recombinant/commit/6adc5d32) add seaborn to environment
- [```35a04471```](https://github.com/ktmeaton/ncov-recombinant/commit/35a04471) add changelog to report pptx
- [```99e98aa7```](https://github.com/ktmeaton/ncov-recombinant/commit/99e98aa7) add epiweeks to environment
- [```1644b1fc```](https://github.com/ktmeaton/ncov-recombinant/commit/1644b1fc) add pptx report
- [```1ab93aff```](https://github.com/ktmeaton/ncov-recombinant/commit/1ab93aff) (broken) start plotting
- [```094530f0```](https://github.com/ktmeaton/ncov-recombinant/commit/094530f0) swithc sc2rf to a postprocess script
- [```02193d6e```](https://github.com/ktmeaton/ncov-recombinant/commit/02193d6e) try generalizing sc2rf post-processing

## v0.2.0

### Notes

#### Bugs

1. Fix bug in `sc2rf_recombinants` regions/breakpoints logic.
1. Fix bug in `sc2rf` where a sample has no definitive substitutions.

#### Params

1. Allow `--breakpoints 0-4`, for XN. We'll determine the breakpoints in post-processing.
1. Bump up the `min_len` of `sc2rf_recombinants` to 1000 bp.
1. Add param `mutation_threshold` to `sc2rf`.
1. Reduce default `mutation_threshold` to 0.25 to catch [Issue #591](https://github.com/cov-lineages/pango-designation/issues/591_.
1. Bump up subtree size from 100 sequences to 500 sequences.

    - Trying to future proof against XE growth (200+ sequences)

1. Discovered that `--primers` interferes with breakpoint detection, use only for debugging.
1. Only use `--enable-deletions` in `sc2rf` for debug mode. Otherwise it changes breakpoints.
1. Only use `--private-mutations` to `sc2rf` for debug mode. Unreadable output for bulk sample processing.

#### Report

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

#### Output

1. Set Auspice default coloring to `lineage_usher` where possible.
1. Remove nwk output from `usher` and `usher_subtrees`:

    - Pull subtree sample names from json instead

1. Output `linelist.exclude.tsv` of false-positive recombinants.

#### Programs

1. Update `nextclade_dataset` to 2022-04-28.
1. Add `taxoniumtools` and `chronumental` to environment.
1. Separate nextclade clades and pango lineage allele frequences in `sc2rf`.
1. Exclude BA.3, BA.4, and BA.5 for now, as their global prevalence is low and they are descendants of BA.2.

#### Profiles

1. Add a `tutorial` profile.

    - (N=2) Designated Recombinants (pango-designation)
    - (N=2) Proposed Recombinants (issues, UCSC)
    - (N=2) Unpublished Recombinants

1. Add XL to `controls`.
1. Add XN to `controls`.
1. Add XR to `controls`.
1. Add XP to `controls`.

#### Workflow

1. Split `usher_subtree` and `usher_subtree_collapse` into separate rules.

    - This speeds up testing for collapsing trees and styling the Auspice JSON.

1. Force include `Nextclade` recombinants (auto-pass through `sc2rf`).
1. Split `usher` and `usher_stats` into separate rules.

### Pull Requests

- [```pull/13```](https://github.com/ktmeaton/ncov-recombinant/pull/13) Three status categories: designated, proposed, unpublished

### Commits

- [```10388a6e```](https://github.com/ktmeaton/ncov-recombinant/commit/10388a6e) update docs for v0.2.0
- [```32b9e8ab```](https://github.com/ktmeaton/ncov-recombinant/commit/32b9e8ab) separate usher and usher_stats rule and catch 3 or 4 col usher
- [```70da837c```](https://github.com/ktmeaton/ncov-recombinant/commit/70da837c) update github issues and breakpoints for 636 and 637
- [```9ed10f17```](https://github.com/ktmeaton/ncov-recombinant/commit/9ed10f17) skip parsing github issues that don't have body
- [```216cb28e```](https://github.com/ktmeaton/ncov-recombinant/commit/216cb28e) put the date in the usher data for tutorial
- [```c95cca0e```](https://github.com/ktmeaton/ncov-recombinant/commit/c95cca0e) update usher v0.5.3
- [```98c91bee```](https://github.com/ktmeaton/ncov-recombinant/commit/98c91bee) finish reporting cycle 2022-05-11
- [```e4755f16```](https://github.com/ktmeaton/ncov-recombinant/commit/e4755f16) new sc2rf mutation data by clade
- [```4a501d56```](https://github.com/ktmeaton/ncov-recombinant/commit/4a501d56) separate omicron lineages from omicron clades
- [```d6185aaf```](https://github.com/ktmeaton/ncov-recombinant/commit/d6185aaf) testing change to auto-pass nextclade recombinants
- [```2e02922f```](https://github.com/ktmeaton/ncov-recombinant/commit/2e02922f) add XL XN XR XP to controls
- [```e2c9675b```](https://github.com/ktmeaton/ncov-recombinant/commit/e2c9675b) add usher_extra and qc file to sc2rf recombinants
- [```941a64c5```](https://github.com/ktmeaton/ncov-recombinant/commit/941a64c5) update github issues
- [```943cde95```](https://github.com/ktmeaton/ncov-recombinant/commit/943cde95) add usher placements to summary
- [```0d0ffbd4```](https://github.com/ktmeaton/ncov-recombinant/commit/0d0ffbd4) combine show-private-mutations with ignore-shared
- [```f1d7e6c1```](https://github.com/ktmeaton/ncov-recombinant/commit/f1d7e6c1) update sc2rf after terminal bugfixes
- [```8f4fd95a```](https://github.com/ktmeaton/ncov-recombinant/commit/8f4fd95a) add country England to geo res
- [```efeeb6ca```](https://github.com/ktmeaton/ncov-recombinant/commit/efeeb6ca) add mutation threshold param sep for sc2rf
- [```9c42bc6c```](https://github.com/ktmeaton/ncov-recombinant/commit/9c42bc6c) limit table col width size in report
- [```7d746e3f```](https://github.com/ktmeaton/ncov-recombinant/commit/7d746e3f) fix growth calculation
- [```0dc7f464```](https://github.com/ktmeaton/ncov-recombinant/commit/0dc7f464) identify sc2rf lineage by breakpoints and parents
- [```19fc3721```](https://github.com/ktmeaton/ncov-recombinant/commit/19fc3721) add parents to breakpoints and issues
- [```27bbff0a```](https://github.com/ktmeaton/ncov-recombinant/commit/27bbff0a) generate geo_resolutions from ncov defaults lat longs
- [```86aa78ba```](https://github.com/ktmeaton/ncov-recombinant/commit/86aa78ba) add map to auspice subtrees
- [```2499827e```](https://github.com/ktmeaton/ncov-recombinant/commit/2499827e) add taxoniumtools and chronumental to env
- [```ec46a569```](https://github.com/ktmeaton/ncov-recombinant/commit/ec46a569) change tutorial seq names from underscores to dashes
- [```27170a0b```](https://github.com/ktmeaton/ncov-recombinant/commit/27170a0b) fix issues line endings
- [```e8eb1215```](https://github.com/ktmeaton/ncov-recombinant/commit/e8eb1215) update nextclade dataset to 2022-04-28
- [```89335c3a```](https://github.com/ktmeaton/ncov-recombinant/commit/89335c3a) (broken) updating columns in report
- [```67475ecc```](https://github.com/ktmeaton/ncov-recombinant/commit/67475ecc) update sc2rf
- [```79b7b2b9```](https://github.com/ktmeaton/ncov-recombinant/commit/79b7b2b9) add tip to readme
- [```10df6a54```](https://github.com/ktmeaton/ncov-recombinant/commit/10df6a54) remove all sample extraction from usher
- [```2ffbcb61```](https://github.com/ktmeaton/ncov-recombinant/commit/2ffbcb61) switch sc2rf submodule to ktmeaton fork
- [```e2adaabe```](https://github.com/ktmeaton/ncov-recombinant/commit/e2adaabe) disable snakemake report in pipeline ci
- [```f12fef14```](https://github.com/ktmeaton/ncov-recombinant/commit/f12fef14) edit line linst preview instructions
- [```d10eb730```](https://github.com/ktmeaton/ncov-recombinant/commit/d10eb730) add collection date to tutorial
- [```d4e0aa86```](https://github.com/ktmeaton/ncov-recombinant/commit/d4e0aa86) very preliminary credits and tutorial
- [```e9c41e6e```](https://github.com/ktmeaton/ncov-recombinant/commit/e9c41e6e) change ci pipeline to tutorial build
- [```4de7370d```](https://github.com/ktmeaton/ncov-recombinant/commit/4de7370d) add tutorial data
- [```8d8c88fc```](https://github.com/ktmeaton/ncov-recombinant/commit/8d8c88fc) set min version for click to troubleshoot env creation
- [```c7fb50a4```](https://github.com/ktmeaton/ncov-recombinant/commit/c7fb50a4) better issue reporting
- [```b2699823```](https://github.com/ktmeaton/ncov-recombinant/commit/b2699823) update sc2rf

## v0.1.2

### Notes

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
1. Add documentation to the report.

    - What the sequences column format means: X (+X)
    - What the different lineage classifers.

### Pull Requests

- [```pull/10```](https://github.com/ktmeaton/ncov-recombinant/pull/10) Automated report generation and sc2rf lineage assignments

### Commits

- [```941f0c08```](https://github.com/ktmeaton/ncov-recombinant/commit/941f0c08) update CHANGELOG
- [```bce219b6```](https://github.com/ktmeaton/ncov-recombinant/commit/bce219b6) fix notes conflict
- [```cdb3bc7f```](https://github.com/ktmeaton/ncov-recombinant/commit/cdb3bc7f) fix duplicate pr output in autologs
- [```0a8ffd84```](https://github.com/ktmeaton/ncov-recombinant/commit/0a8ffd84) update notes for v0.1.2
- [```0075209b```](https://github.com/ktmeaton/ncov-recombinant/commit/0075209b) add issue to recombinants report
- [```0fd8fea0```](https://github.com/ktmeaton/ncov-recombinant/commit/0fd8fea0) (broken) troubleshoot usher collapse json
- [```b0ab72b9```](https://github.com/ktmeaton/ncov-recombinant/commit/b0ab72b9) update breakpoints
- [```a3058c57```](https://github.com/ktmeaton/ncov-recombinant/commit/a3058c57) update sc2rf examples
- [```b5f2a0f8```](https://github.com/ktmeaton/ncov-recombinant/commit/b5f2a0f8) update and clean controls data
- [```f69f254c```](https://github.com/ktmeaton/ncov-recombinant/commit/f69f254c) add curated breakpoints to issues
- [```4e9d2dc9```](https://github.com/ktmeaton/ncov-recombinant/commit/4e9d2dc9) add an issues script and resources file
- [```16059610```](https://github.com/ktmeaton/ncov-recombinant/commit/16059610) major environment reduction
- [```5ced9193```](https://github.com/ktmeaton/ncov-recombinant/commit/5ced9193) remove bedtools from env
- [```28777cb9```](https://github.com/ktmeaton/ncov-recombinant/commit/28777cb9) remove seaborn from env
- [```01f459c4```](https://github.com/ktmeaton/ncov-recombinant/commit/01f459c4) remove snipit from env
- [```7d6ef729```](https://github.com/ktmeaton/ncov-recombinant/commit/7d6ef729) remove augur from env
- [```9a2e948d```](https://github.com/ktmeaton/ncov-recombinant/commit/9a2e948d) fix pandas warnings in report
- [```78daee55```](https://github.com/ktmeaton/ncov-recombinant/commit/78daee55) remove script usher_plot as now we rely on auspice
- [```a7bd52f1```](https://github.com/ktmeaton/ncov-recombinant/commit/a7bd52f1) remove script update_controls which is now done manually
- [```93a30200```](https://github.com/ktmeaton/ncov-recombinant/commit/93a30200) consolidate lineage call in report
- [```5f3e3633```](https://github.com/ktmeaton/ncov-recombinant/commit/5f3e3633) hardcode columns for report
- [```6333fde4```](https://github.com/ktmeaton/ncov-recombinant/commit/6333fde4) improve type catching in date_to_decimal
- [```557627a4```](https://github.com/ktmeaton/ncov-recombinant/commit/557627a4) update controls breakpoints and add col sc2rf_lineage
- [```7e2ad531```](https://github.com/ktmeaton/ncov-recombinant/commit/7e2ad531) add param --ignore-shared-subs to sc2rf
- [```519a9eea```](https://github.com/ktmeaton/ncov-recombinant/commit/519a9eea) overhaul reporting workflow
- [```6fa674f2```](https://github.com/ktmeaton/ncov-recombinant/commit/6fa674f2) update controls metadata and dev notes
- [```46155a84```](https://github.com/ktmeaton/ncov-recombinant/commit/46155a84) add XM to controls
- [```d2d4cd80```](https://github.com/ktmeaton/ncov-recombinant/commit/d2d4cd80) update notes for v0.1.2
- [```17ae6eeb```](https://github.com/ktmeaton/ncov-recombinant/commit/17ae6eeb) add issue to recombinants report
- [```2ab8dd30```](https://github.com/ktmeaton/ncov-recombinant/commit/2ab8dd30) (broken) troubleshoot usher collapse json
- [```e4fd3352```](https://github.com/ktmeaton/ncov-recombinant/commit/e4fd3352) update breakpoints
- [```c743ad3d```](https://github.com/ktmeaton/ncov-recombinant/commit/c743ad3d) update sc2rf examples
- [```62e1ffc1```](https://github.com/ktmeaton/ncov-recombinant/commit/62e1ffc1) update and clean controls data
- [```9c401a0c```](https://github.com/ktmeaton/ncov-recombinant/commit/9c401a0c) add curated breakpoints to issues
- [```7cf953ad```](https://github.com/ktmeaton/ncov-recombinant/commit/7cf953ad) add an issues script and resources file
- [```fbf35e51```](https://github.com/ktmeaton/ncov-recombinant/commit/fbf35e51) major environment reduction
- [```1b1f16e9```](https://github.com/ktmeaton/ncov-recombinant/commit/1b1f16e9) remove bedtools from env
- [```7b650279```](https://github.com/ktmeaton/ncov-recombinant/commit/7b650279) remove seaborn from env
- [```b32608e7```](https://github.com/ktmeaton/ncov-recombinant/commit/b32608e7) remove snipit from env
- [```9cab231e```](https://github.com/ktmeaton/ncov-recombinant/commit/9cab231e) remove augur from env
- [```a69836a8```](https://github.com/ktmeaton/ncov-recombinant/commit/a69836a8) fix pandas warnings in report
- [```b3137ed3```](https://github.com/ktmeaton/ncov-recombinant/commit/b3137ed3) remove script usher_plot as now we rely on auspice
- [```06fa080d```](https://github.com/ktmeaton/ncov-recombinant/commit/06fa080d) remove script update_controls which is now done manually
- [```e8d46a64```](https://github.com/ktmeaton/ncov-recombinant/commit/e8d46a64) consolidate lineage call in report
- [```ccfea688```](https://github.com/ktmeaton/ncov-recombinant/commit/ccfea688) hardcode columns for report
- [```5172755e```](https://github.com/ktmeaton/ncov-recombinant/commit/5172755e) improve type catching in date_to_decimal
- [```74f0e528```](https://github.com/ktmeaton/ncov-recombinant/commit/74f0e528) update controls breakpoints and add col sc2rf_lineage
- [```d4664015```](https://github.com/ktmeaton/ncov-recombinant/commit/d4664015) add param --ignore-shared-subs to sc2rf
- [```659d7f83```](https://github.com/ktmeaton/ncov-recombinant/commit/659d7f83) overhaul reporting workflow
- [```e8e3444f```](https://github.com/ktmeaton/ncov-recombinant/commit/e8e3444f) update controls metadata and dev notes
- [```07a5ff52```](https://github.com/ktmeaton/ncov-recombinant/commit/07a5ff52) add XM to controls

## v0.1.1

### Notes

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
1. Add new rule `usher_metadata` for merge metadata for subtrees.

### Commits

- [```b8f89d5e```](https://github.com/ktmeaton/ncov-recombinant/commit/b8f89d5e) update docs for v0.1.1
- [```2b8772ab```](https://github.com/ktmeaton/ncov-recombinant/commit/2b8772ab) update autologs for pr date matching
- [```f2a7547d```](https://github.com/ktmeaton/ncov-recombinant/commit/f2a7547d) add low_memory_mode for issue #9
- [```94fc9426```](https://github.com/ktmeaton/ncov-recombinant/commit/94fc9426) add log to report rule
- [```861ffb17```](https://github.com/ktmeaton/ncov-recombinant/commit/861ffb17) update usher output image
- [```fdee0da6```](https://github.com/ktmeaton/ncov-recombinant/commit/fdee0da6) add new rule usher_metadata
- [```c5003453```](https://github.com/ktmeaton/ncov-recombinant/commit/c5003453) add max parents param to sc2rf recombinants
- [```70cad049```](https://github.com/ktmeaton/ncov-recombinant/commit/70cad049) add max ambig filter to defaults for sc2rf
- [```b4cc40f4```](https://github.com/ktmeaton/ncov-recombinant/commit/b4cc40f4) add script to collapse usher metadata for auspice
- [```847c6d24```](https://github.com/ktmeaton/ncov-recombinant/commit/847c6d24) catch single trees in usher collapse
- [```636778e0```](https://github.com/ktmeaton/ncov-recombinant/commit/636778e0) rename sc2rf txt output to ansi
- [```bae50814```](https://github.com/ktmeaton/ncov-recombinant/commit/bae50814) change final target to report
- [```9a830085```](https://github.com/ktmeaton/ncov-recombinant/commit/9a830085) add new rule report
- [```601e1728```](https://github.com/ktmeaton/ncov-recombinant/commit/601e1728) add XD to controls
- [```baa1d64e```](https://github.com/ktmeaton/ncov-recombinant/commit/baa1d64e) relax sc2rf --unique from 2 to 1 for XQ
- [```bffbb9ad```](https://github.com/ktmeaton/ncov-recombinant/commit/bffbb9ad) add column sc2rf_clades_filter
- [```109ed5d2```](https://github.com/ktmeaton/ncov-recombinant/commit/109ed5d2) test sc2rf dev to not report ambiguous regions
- [```d9fdffef```](https://github.com/ktmeaton/ncov-recombinant/commit/d9fdffef) fix tab spaces at end of usher placement
- [```085e1764```](https://github.com/ktmeaton/ncov-recombinant/commit/085e1764) update sc2rf for tsv/csv PR
- [```d2363855```](https://github.com/ktmeaton/ncov-recombinant/commit/d2363855) set threads and cpus to 1 for all single-thread rules
- [```13027205```](https://github.com/ktmeaton/ncov-recombinant/commit/13027205) impose wildcard constraint on nextclade_dataset
- [```30e1406b```](https://github.com/ktmeaton/ncov-recombinant/commit/30e1406b) fix typo in csv path for sc2rf
- [```d6d8377a```](https://github.com/ktmeaton/ncov-recombinant/commit/d6d8377a) add XS breakpoints to metadata
- [```371e4069```](https://github.com/ktmeaton/ncov-recombinant/commit/371e4069) add XS and XQ to controls
- [```1e31e429```](https://github.com/ktmeaton/ncov-recombinant/commit/1e31e429) add breakpoints reference file in controls
- [```3088ad60```](https://github.com/ktmeaton/ncov-recombinant/commit/3088ad60) catch if sc2rf has no output
- [```64211360```](https://github.com/ktmeaton/ncov-recombinant/commit/64211360) catch all extra args in slurm
- [```c7a6b9ce```](https://github.com/ktmeaton/ncov-recombinant/commit/c7a6b9ce) remove unused nextclade_recombinants script
- [```38645ce9```](https://github.com/ktmeaton/ncov-recombinant/commit/38645ce9) remove codecov badge
- [```50fa9d89```](https://github.com/ktmeaton/ncov-recombinant/commit/50fa9d89) update CHANGELOG for v0.1.0

## v0.1.0

### Notes

1. Add Stage 1: Nextclade.
1. Add Stage 2: sc2rf.
1. Add Stage 3: UShER.
1. Add Stage 4: Summary.
1. Add Continuous Integration workflows: `lint`, `test`, `pipeline`, and `release`.
1. New representative controls dataset:

    - Exclude XA because this is an Alpha recombinant (poor lineage accuracy).
    - Exclude XB because of [current issue](https://github.com/summercms/covid19-pango-designation/commit/26b7359e34a0b2f122215332b6495fea97ff3fe7)
    - Exclude XC because this is an Alpha recombinant (poor lineage accuracy).
    - Exclude XD because there are no public genomes.
    - Exclude XK because there are no public genomes.

### Pull Requests

- [```pull/3```](https://github.com/ktmeaton/ncov-recombinant/pull/3) Add Continuous Integration workflows: lint, test, pipeline, and release.

### Commits

- [```34c721b7```](https://github.com/ktmeaton/ncov-recombinant/commit/34c721b7) rearrange summary cols
- [```18b389de```](https://github.com/ktmeaton/ncov-recombinant/commit/18b389de) disable usher plotting
- [```0a101dd9```](https://github.com/ktmeaton/ncov-recombinant/commit/0a101dd9) covert sc2rf_recombinants to a script
- [```494fb60c```](https://github.com/ktmeaton/ncov-recombinant/commit/494fb60c) change nextclade filtering to multi columns
- [```f0676bd8```](https://github.com/ktmeaton/ncov-recombinant/commit/f0676bd8) add python3 directive to unit tests
- [```9da626fd```](https://github.com/ktmeaton/ncov-recombinant/commit/9da626fd) update unit tests for new controls dataset
- [```46717c6f```](https://github.com/ktmeaton/ncov-recombinant/commit/46717c6f) fix summary script for new ver
- [```9fc690ed```](https://github.com/ktmeaton/ncov-recombinant/commit/9fc690ed) fix usher public-latest links
- [```1fb28ea0```](https://github.com/ktmeaton/ncov-recombinant/commit/1fb28ea0) change sc2rf to bash script
- [```ba98d936```](https://github.com/ktmeaton/ncov-recombinant/commit/ba98d936) update sc2rf params
- [```89647109```](https://github.com/ktmeaton/ncov-recombinant/commit/89647109) update sc2rf artpoon pr
- [```2b7dcab4```](https://github.com/ktmeaton/ncov-recombinant/commit/2b7dcab4) ignore my_profiles
- [```9df0f9b4```](https://github.com/ktmeaton/ncov-recombinant/commit/9df0f9b4) add debugging mode for sc2rf (lint)
- [```caaf4deb```](https://github.com/ktmeaton/ncov-recombinant/commit/caaf4deb) add debugging mode for sc2rf
- [```7ec53ac6```](https://github.com/ktmeaton/ncov-recombinant/commit/7ec53ac6) remove unecessary param exp_input
- [```a3810bca```](https://github.com/ktmeaton/ncov-recombinant/commit/a3810bca) add program versions to summary
- [```3376196b```](https://github.com/ktmeaton/ncov-recombinant/commit/3376196b) Add Continuous Integration workflows: lint, test, pipeline, and release. (#3)
- [```db45768f```](https://github.com/ktmeaton/ncov-recombinant/commit/db45768f) more instructions for visualizing output
- [```ee4c2660```](https://github.com/ktmeaton/ncov-recombinant/commit/ee4c2660) update readme keywords
- [```cb5b2c23```](https://github.com/ktmeaton/ncov-recombinant/commit/cb5b2c23) add instructions for slurm submission
- [```f04eb28b```](https://github.com/ktmeaton/ncov-recombinant/commit/f04eb28b) adjust laptop profile to use 1 cpu
- [```eafed44e```](https://github.com/ktmeaton/ncov-recombinant/commit/eafed44e) add snakefile
- [```eb214d72```](https://github.com/ktmeaton/ncov-recombinant/commit/eb214d72) add scripts
- [```cb47b046```](https://github.com/ktmeaton/ncov-recombinant/commit/cb47b046) add README.md
- [```3794d8de```](https://github.com/ktmeaton/ncov-recombinant/commit/3794d8de) add images dir
- [```f1c0cef8```](https://github.com/ktmeaton/ncov-recombinant/commit/f1c0cef8) add profiles laptop and hpc
- [```6f5fd84b```](https://github.com/ktmeaton/ncov-recombinant/commit/6f5fd84b) add release notes
- [```92b0c476```](https://github.com/ktmeaton/ncov-recombinant/commit/92b0c476) add default parameters
- [```c79bfe12```](https://github.com/ktmeaton/ncov-recombinant/commit/c79bfe12) add submodule ncov
- [```2a65e92d```](https://github.com/ktmeaton/ncov-recombinant/commit/2a65e92d) add submodule sc2rf
- [```0f8bfe33```](https://github.com/ktmeaton/ncov-recombinant/commit/0f8bfe33) add submodule autologs
- [```b6f1e1d6```](https://github.com/ktmeaton/ncov-recombinant/commit/b6f1e1d6) add report captions
- [```68fd2dec```](https://github.com/ktmeaton/ncov-recombinant/commit/68fd2dec) add conda env
- [```8907375e```](https://github.com/ktmeaton/ncov-recombinant/commit/8907375e) add reference dataset
