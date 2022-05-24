# CHANGELOG

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
- [```pull/12```](https://github.com/ktmeaton/ncov-recombinant/pull/12) Tutorial dataset and map panel for Auspice subtrees
- [```pull/11```](https://github.com/ktmeaton/ncov-recombinant/pull/11) Add a tutorial profile

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

### Pull Requests

- [```pull/8```](https://github.com/ktmeaton/ncov-recombinant/pull/8) Add XS and XQ to controls.

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
