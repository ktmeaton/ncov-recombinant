# CHANGELOG

## Development

### Commits

## v0.1.2

### Notes

1. Add lineage `XM` to controls.
1. Correct `XF` and `XJ` controls to match issues.
1. Create a markdown report with program versions.
1. Fix `sc2rf_recombinants` bug where samples with >2 breakpoints were being excluded.
1. Summarize recombinants by parents and dates observed.
1. Change `report.tsv` to `linelist.tsv`.
1. Use `date_to_decimal.py` to create `num_date` for auspice subtrees.
1. Add an `--exclude-clades` param to `sc2rf_recombinants.py`.
1. Add param `--ignore-shared-subs` to `sc2rf`.
1. Update breakpoints in controls metadata to reflect the output with `--ignore-shared-subs`.
1. Bump up `min_len` for `sc2rf_recombinants` to 200 bp.
1. Add column `sc2rf_lineage` to `sc2rf_recombinants` output.
1. Consolidate lineage assignments into a single column.
1. Slim down the conda environment and remove unnecessary programs.
1. Use github api to pull recombinant issues.
1. Consolidate \*_to_\* files into `resources/issues.tsv`.
1. Use the `--clades` param of `sc2rf` rather than using `exclude_clades`.
1. Disabled `--rebuild-examples` in `sc2rf` because of requests error.
1. Add column `issue` to `recombinants.tsv`.
1. Get `ncov-recombinant` version using tag.
1. Add documentation to the report.

### Pull Requests

* [```pull/10```](https://github.com/ktmeaton/ncov-recombinant/pull/10) Automated report generation and sc2rf lineage assignments

### Commits

* [```bce219b6```](https://github.com/ktmeaton/ncov-recombinant/commit/bce219b6) fix notes conflict
* [```cdb3bc7f```](https://github.com/ktmeaton/ncov-recombinant/commit/cdb3bc7f) fix duplicate pr output in autologs
* [```0a8ffd84```](https://github.com/ktmeaton/ncov-recombinant/commit/0a8ffd84) update notes for v0.1.2
* [```0075209b```](https://github.com/ktmeaton/ncov-recombinant/commit/0075209b) add issue to recombinants report
* [```0fd8fea0```](https://github.com/ktmeaton/ncov-recombinant/commit/0fd8fea0) (broken) troubleshoot usher collapse json
* [```b0ab72b9```](https://github.com/ktmeaton/ncov-recombinant/commit/b0ab72b9) update breakpoints
* [```a3058c57```](https://github.com/ktmeaton/ncov-recombinant/commit/a3058c57) update sc2rf examples
* [```b5f2a0f8```](https://github.com/ktmeaton/ncov-recombinant/commit/b5f2a0f8) update and clean controls data
* [```f69f254c```](https://github.com/ktmeaton/ncov-recombinant/commit/f69f254c) add curated breakpoints to issues
* [```4e9d2dc9```](https://github.com/ktmeaton/ncov-recombinant/commit/4e9d2dc9) add an issues script and resources file
* [```16059610```](https://github.com/ktmeaton/ncov-recombinant/commit/16059610) major environment reduction
* [```5ced9193```](https://github.com/ktmeaton/ncov-recombinant/commit/5ced9193) remove bedtools from env
* [```28777cb9```](https://github.com/ktmeaton/ncov-recombinant/commit/28777cb9) remove seaborn from env
* [```01f459c4```](https://github.com/ktmeaton/ncov-recombinant/commit/01f459c4) remove snipit from env
* [```7d6ef729```](https://github.com/ktmeaton/ncov-recombinant/commit/7d6ef729) remove augur from env
* [```9a2e948d```](https://github.com/ktmeaton/ncov-recombinant/commit/9a2e948d) fix pandas warnings in report
* [```78daee55```](https://github.com/ktmeaton/ncov-recombinant/commit/78daee55) remove script usher_plot as now we rely on auspice
* [```a7bd52f1```](https://github.com/ktmeaton/ncov-recombinant/commit/a7bd52f1) remove script update_controls which is now done manually
* [```93a30200```](https://github.com/ktmeaton/ncov-recombinant/commit/93a30200) consolidate lineage call in report
* [```5f3e3633```](https://github.com/ktmeaton/ncov-recombinant/commit/5f3e3633) hardcode columns for report
* [```6333fde4```](https://github.com/ktmeaton/ncov-recombinant/commit/6333fde4) improve type catching in date_to_decimal
* [```557627a4```](https://github.com/ktmeaton/ncov-recombinant/commit/557627a4) update controls breakpoints and add col sc2rf_lineage
* [```7e2ad531```](https://github.com/ktmeaton/ncov-recombinant/commit/7e2ad531) add param --ignore-shared-subs to sc2rf
* [```519a9eea```](https://github.com/ktmeaton/ncov-recombinant/commit/519a9eea) overhaul reporting workflow
* [```6fa674f2```](https://github.com/ktmeaton/ncov-recombinant/commit/6fa674f2) update controls metadata and dev notes
* [```46155a84```](https://github.com/ktmeaton/ncov-recombinant/commit/46155a84) add XM to controls
* [```d2d4cd80```](https://github.com/ktmeaton/ncov-recombinant/commit/d2d4cd80) update notes for v0.1.2
* [```17ae6eeb```](https://github.com/ktmeaton/ncov-recombinant/commit/17ae6eeb) add issue to recombinants report
* [```2ab8dd30```](https://github.com/ktmeaton/ncov-recombinant/commit/2ab8dd30) (broken) troubleshoot usher collapse json
* [```e4fd3352```](https://github.com/ktmeaton/ncov-recombinant/commit/e4fd3352) update breakpoints
* [```c743ad3d```](https://github.com/ktmeaton/ncov-recombinant/commit/c743ad3d) update sc2rf examples
* [```62e1ffc1```](https://github.com/ktmeaton/ncov-recombinant/commit/62e1ffc1) update and clean controls data
* [```9c401a0c```](https://github.com/ktmeaton/ncov-recombinant/commit/9c401a0c) add curated breakpoints to issues
* [```7cf953ad```](https://github.com/ktmeaton/ncov-recombinant/commit/7cf953ad) add an issues script and resources file
* [```fbf35e51```](https://github.com/ktmeaton/ncov-recombinant/commit/fbf35e51) major environment reduction
* [```1b1f16e9```](https://github.com/ktmeaton/ncov-recombinant/commit/1b1f16e9) remove bedtools from env
* [```7b650279```](https://github.com/ktmeaton/ncov-recombinant/commit/7b650279) remove seaborn from env
* [```b32608e7```](https://github.com/ktmeaton/ncov-recombinant/commit/b32608e7) remove snipit from env
* [```9cab231e```](https://github.com/ktmeaton/ncov-recombinant/commit/9cab231e) remove augur from env
* [```a69836a8```](https://github.com/ktmeaton/ncov-recombinant/commit/a69836a8) fix pandas warnings in report
* [```b3137ed3```](https://github.com/ktmeaton/ncov-recombinant/commit/b3137ed3) remove script usher_plot as now we rely on auspice
* [```06fa080d```](https://github.com/ktmeaton/ncov-recombinant/commit/06fa080d) remove script update_controls which is now done manually
* [```e8d46a64```](https://github.com/ktmeaton/ncov-recombinant/commit/e8d46a64) consolidate lineage call in report
* [```ccfea688```](https://github.com/ktmeaton/ncov-recombinant/commit/ccfea688) hardcode columns for report
* [```5172755e```](https://github.com/ktmeaton/ncov-recombinant/commit/5172755e) improve type catching in date_to_decimal
* [```74f0e528```](https://github.com/ktmeaton/ncov-recombinant/commit/74f0e528) update controls breakpoints and add col sc2rf_lineage
* [```d4664015```](https://github.com/ktmeaton/ncov-recombinant/commit/d4664015) add param --ignore-shared-subs to sc2rf
* [```659d7f83```](https://github.com/ktmeaton/ncov-recombinant/commit/659d7f83) overhaul reporting workflow
* [```e8e3444f```](https://github.com/ktmeaton/ncov-recombinant/commit/e8e3444f) update controls metadata and dev notes
* [```07a5ff52```](https://github.com/ktmeaton/ncov-recombinant/commit/07a5ff52) add XM to controls

## v0.1.1

### Notes

1. Add lineage `XD` to controls.
1. Add lineage `XQ` to controls.
1. Add lineage `XS` to controls.
1. Exclude lineage `XR` because it has no public genomes.
1. Test `sc2rf` dev to ignore clade regions that are ambiguous.
1. Add column `usher_pango_lineage_map` that maps github issues to recombinant lineages.
1. Add new rule `report`.
1. Filter non-recombinants from `sc2rf` ansi output.
1. Fix `subtrees_collapse` failing if only 1 tree specified
1. Add new rule `usher_metadata` for merge metadata for subtrees.

### Pull Requests

* [```pull/8```](https://github.com/ktmeaton/ncov-recombinant/pull/8) Add XS and XQ to controls.

### Commits

* [```b8f89d5e```](https://github.com/ktmeaton/ncov-recombinant/commit/b8f89d5e) update docs for v0.1.1
* [```2b8772ab```](https://github.com/ktmeaton/ncov-recombinant/commit/2b8772ab) update autologs for pr date matching
* [```f2a7547d```](https://github.com/ktmeaton/ncov-recombinant/commit/f2a7547d) add low_memory_mode for issue #9
* [```94fc9426```](https://github.com/ktmeaton/ncov-recombinant/commit/94fc9426) add log to report rule
* [```861ffb17```](https://github.com/ktmeaton/ncov-recombinant/commit/861ffb17) update usher output image
* [```fdee0da6```](https://github.com/ktmeaton/ncov-recombinant/commit/fdee0da6) add new rule usher_metadata
* [```c5003453```](https://github.com/ktmeaton/ncov-recombinant/commit/c5003453) add max parents param to sc2rf recombinants
* [```70cad049```](https://github.com/ktmeaton/ncov-recombinant/commit/70cad049) add max ambig filter to defaults for sc2rf
* [```b4cc40f4```](https://github.com/ktmeaton/ncov-recombinant/commit/b4cc40f4) add script to collapse usher metadata for auspice
* [```847c6d24```](https://github.com/ktmeaton/ncov-recombinant/commit/847c6d24) catch single trees in usher collapse
* [```636778e0```](https://github.com/ktmeaton/ncov-recombinant/commit/636778e0) rename sc2rf txt output to ansi
* [```bae50814```](https://github.com/ktmeaton/ncov-recombinant/commit/bae50814) change final target to report
* [```9a830085```](https://github.com/ktmeaton/ncov-recombinant/commit/9a830085) add new rule report
* [```601e1728```](https://github.com/ktmeaton/ncov-recombinant/commit/601e1728) add XD to controls
* [```baa1d64e```](https://github.com/ktmeaton/ncov-recombinant/commit/baa1d64e) relax sc2rf --unique from 2 to 1 for XQ
* [```bffbb9ad```](https://github.com/ktmeaton/ncov-recombinant/commit/bffbb9ad) add column sc2rf_clades_filter
* [```109ed5d2```](https://github.com/ktmeaton/ncov-recombinant/commit/109ed5d2) test sc2rf dev to not report ambiguous regions
* [```d9fdffef```](https://github.com/ktmeaton/ncov-recombinant/commit/d9fdffef) fix tab spaces at end of usher placement
* [```085e1764```](https://github.com/ktmeaton/ncov-recombinant/commit/085e1764) update sc2rf for tsv/csv PR
* [```d2363855```](https://github.com/ktmeaton/ncov-recombinant/commit/d2363855) set threads and cpus to 1 for all single-thread rules
* [```13027205```](https://github.com/ktmeaton/ncov-recombinant/commit/13027205) impose wildcard constraint on nextclade_dataset
* [```30e1406b```](https://github.com/ktmeaton/ncov-recombinant/commit/30e1406b) fix typo in csv path for sc2rf
* [```d6d8377a```](https://github.com/ktmeaton/ncov-recombinant/commit/d6d8377a) add XS breakpoints to metadata
* [```371e4069```](https://github.com/ktmeaton/ncov-recombinant/commit/371e4069) add XS and XQ to controls
* [```1e31e429```](https://github.com/ktmeaton/ncov-recombinant/commit/1e31e429) add breakpoints reference file in controls
* [```3088ad60```](https://github.com/ktmeaton/ncov-recombinant/commit/3088ad60) catch if sc2rf has no output
* [```64211360```](https://github.com/ktmeaton/ncov-recombinant/commit/64211360) catch all extra args in slurm
* [```c7a6b9ce```](https://github.com/ktmeaton/ncov-recombinant/commit/c7a6b9ce) remove unused nextclade_recombinants script
* [```38645ce9```](https://github.com/ktmeaton/ncov-recombinant/commit/38645ce9) remove codecov badge
* [```50fa9d89```](https://github.com/ktmeaton/ncov-recombinant/commit/50fa9d89) update CHANGELOG for v0.1.0

## v0.1.0

### Notes

1. Add Stage 1: Nextclade.
1. Add Stage 2: sc2rf.
1. Add Stage 3: UShER.
1. Add Stage 4: Summary.
1. Add Continuous Integration workflows: `lint`, `test`, `pipeline`, and `release`.
1. New representative controls dataset:

### Pull Requests

* [```pull/3```](https://github.com/ktmeaton/ncov-recombinant/pull/3) Add Continuous Integration workflows: lint, test, pipeline, and release.

### Commits

* [```34c721b7```](https://github.com/ktmeaton/ncov-recombinant/commit/34c721b7) rearrange summary cols
* [```18b389de```](https://github.com/ktmeaton/ncov-recombinant/commit/18b389de) disable usher plotting
* [```0a101dd9```](https://github.com/ktmeaton/ncov-recombinant/commit/0a101dd9) covert sc2rf_recombinants to a script
* [```494fb60c```](https://github.com/ktmeaton/ncov-recombinant/commit/494fb60c) change nextclade filtering to multi columns
* [```f0676bd8```](https://github.com/ktmeaton/ncov-recombinant/commit/f0676bd8) add python3 directive to unit tests
* [```9da626fd```](https://github.com/ktmeaton/ncov-recombinant/commit/9da626fd) update unit tests for new controls dataset
* [```46717c6f```](https://github.com/ktmeaton/ncov-recombinant/commit/46717c6f) fix summary script for new ver
* [```9fc690ed```](https://github.com/ktmeaton/ncov-recombinant/commit/9fc690ed) fix usher public-latest links
* [```1fb28ea0```](https://github.com/ktmeaton/ncov-recombinant/commit/1fb28ea0) change sc2rf to bash script
* [```ba98d936```](https://github.com/ktmeaton/ncov-recombinant/commit/ba98d936) update sc2rf params
* [```89647109```](https://github.com/ktmeaton/ncov-recombinant/commit/89647109) update sc2rf artpoon pr
* [```2b7dcab4```](https://github.com/ktmeaton/ncov-recombinant/commit/2b7dcab4) ignore my_profiles
* [```9df0f9b4```](https://github.com/ktmeaton/ncov-recombinant/commit/9df0f9b4) add debugging mode for sc2rf (lint)
* [```caaf4deb```](https://github.com/ktmeaton/ncov-recombinant/commit/caaf4deb) add debugging mode for sc2rf
* [```7ec53ac6```](https://github.com/ktmeaton/ncov-recombinant/commit/7ec53ac6) remove unecessary param exp_input
* [```a3810bca```](https://github.com/ktmeaton/ncov-recombinant/commit/a3810bca) add program versions to summary
* [```3376196b```](https://github.com/ktmeaton/ncov-recombinant/commit/3376196b) Add Continuous Integration workflows: lint, test, pipeline, and release. (#3)
* [```db45768f```](https://github.com/ktmeaton/ncov-recombinant/commit/db45768f) more instructions for visualizing output
* [```ee4c2660```](https://github.com/ktmeaton/ncov-recombinant/commit/ee4c2660) update readme keywords
* [```cb5b2c23```](https://github.com/ktmeaton/ncov-recombinant/commit/cb5b2c23) add instructions for slurm submission
* [```f04eb28b```](https://github.com/ktmeaton/ncov-recombinant/commit/f04eb28b) adjust laptop profile to use 1 cpu
* [```eafed44e```](https://github.com/ktmeaton/ncov-recombinant/commit/eafed44e) add snakefile
* [```eb214d72```](https://github.com/ktmeaton/ncov-recombinant/commit/eb214d72) add scripts
* [```cb47b046```](https://github.com/ktmeaton/ncov-recombinant/commit/cb47b046) add README.md
* [```3794d8de```](https://github.com/ktmeaton/ncov-recombinant/commit/3794d8de) add images dir
* [```f1c0cef8```](https://github.com/ktmeaton/ncov-recombinant/commit/f1c0cef8) add profiles laptop and hpc
* [```6f5fd84b```](https://github.com/ktmeaton/ncov-recombinant/commit/6f5fd84b) add release notes
* [```92b0c476```](https://github.com/ktmeaton/ncov-recombinant/commit/92b0c476) add default parameters
* [```c79bfe12```](https://github.com/ktmeaton/ncov-recombinant/commit/c79bfe12) add submodule ncov
* [```2a65e92d```](https://github.com/ktmeaton/ncov-recombinant/commit/2a65e92d) add submodule sc2rf
* [```0f8bfe33```](https://github.com/ktmeaton/ncov-recombinant/commit/0f8bfe33) add submodule autologs
* [```b6f1e1d6```](https://github.com/ktmeaton/ncov-recombinant/commit/b6f1e1d6) add report captions
* [```68fd2dec```](https://github.com/ktmeaton/ncov-recombinant/commit/68fd2dec) add conda env
* [```8907375e```](https://github.com/ktmeaton/ncov-recombinant/commit/8907375e) add reference dataset
