# ncov-recombinant
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-6-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/ktmeaton/ncov-recombinant/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/ktmeaton/ncov-recombinant.svg)](https://github.com/ktmeaton/ncov-recombinant/issues)
[![Install CI](https://github.com/ktmeaton/ncov-recombinant/actions/workflows/install.yaml/badge.svg)](https://github.com/ktmeaton/ncov-recombinant/actions/workflows/install.yaml)
[![Test CI](https://github.com/ktmeaton/ncov-recombinant/actions/workflows/test.yaml/badge.svg)](https://github.com/ktmeaton/ncov-recombinant/actions/workflows/test.yaml)
[![Pipeline CI](https://github.com/ktmeaton/ncov-recombinant/actions/workflows/pipeline.yaml/badge.svg)](https://github.com/ktmeaton/ncov-recombinant/actions/workflows/pipeline.yaml)

SARS-CoV-2 recombinant sequence detection inspired by [nextstrain/ncov](https://github.com/nextstrain/ncov).

1. Align sequences and perform clade/lineage assignments with [Nextclade](https://github.com/nextstrain/nextclade).
1. Identify parental clades and plot recombination breakpoints with [sc2rf](https://github.com/lenaschimmel/sc2rf).
1. Phylogenetically place recombinant sequences with [UShER](https://github.com/yatisht/usher).
1. Create spreadssheets and powerpoint slides for reporting.

## Table of Contents

1. [Output](https://github.com/ktmeaton/ncov-recombinant#output)
1. [Install](https://github.com/ktmeaton/ncov-recombinant#install)
1. [Tutorial](https://github.com/ktmeaton/ncov-recombinant#tutorial)
1. [Configuration](https://github.com/ktmeaton/ncov-recombinant#configuration)
1. [High Performance Computing](https://github.com/ktmeaton/ncov-recombinant#high-performance-computing)
1. [Troubleshooting](https://github.com/ktmeaton/ncov-recombinant#troubleshooting)
1. [Credits](https://github.com/ktmeaton/ncov-recombinant#credits)

## Output

### Tables

Linelists are collated into a spreadsheet for excel/google sheets:

1. `lineage`: The recombinant lineages observed.
1. `parents`: The parental combinations observed.
1. `linelist`: Results from <u>all</u> input sequences (minimal statistics).
1. `summary`: Results from <u>all</u> input sequences (all possible statistics, for troubleshooting).
1. `positives`: Results from sequences classified as a <u>recombinant</u> by at least 2 of 3 classifiers.
1. `false_positives`: Results from sequences flagged as recombinants by Nextclade, that were not verified by [sc2rf](https://github.com/lenaschimmel/sc2rf) or [UShER](https://github.com/yatisht/usher).
1. `negatives`: Results from sequences classifed as a <u>non-recombinant</u> by nextclade.
1. `issues`: Metadata of issues related to recombinant lineages posted in the [pango-designation](https://github.com/cov-lineages/pango-designation/issues) repository.

[![excel_output](images/excel_output.png)](
https://docs.google.com/spreadsheets/d/1EH-JmXFTAnzUHavxPOZnNNgHIBZcyhSMRSQJ8J6qWsk/edit#gid=103507248)

### Slides

Powerpoint/google slides with acommpanying plots for presenting.

[![powerpoint_output](images/powerpoint_output.png)](https://docs.google.com/presentation/d/17EDrQk34VUGOfPtpqdNQiBv5OfWPkULpZwgERWeZf-8/edit#slide=id.p2)

### Breakpoints

Visualization of breakpoints by parent from [sc2rf](https://github.com/lenaschimmel/sc2rf).

![sc2rf_output](images/sc2rf_output.png)

### Phylogenetic Context

Placement of samples on the latest global phylogeny using [UShER](https://github.com/yatisht/usher).

![usher_output](images/usher_output.png)

## Install

1. Clone the repository, using the `--recursive` flag for submodules:

    ```bash
    git clone --recursive https://github.com/ktmeaton/ncov-recombinant.git
    cd ncov-recombinant
    ```

2. Install dependencies in a conda environment (`ncov-recombinant`):

    ```bash
    mamba env create -f workflow/envs/environment.yaml
    conda activate ncov-recombinant
    ```

## Tutorial

> Tip: Remember to run `conda activate ncov-recombinant` first!

1. Preview the steps that are going to be run.

    ```bash
    snakemake --profile profiles/tutorial --dryrun
    ```

1. Run the workflow.

    ```bash
    snakemake --profile profiles/tutorial
    ```

1. Explore the output:

    - Slides | `results/tutorial/report/report.pptx`
    - Tables<sup>*</sup> | `results/tutorial/report/report.xlsx`
    - Breakpoints<sup>†</sup> | `results/tutorial/sc2rf/recombinants.ansi.txt`
    - Trees<sup>‡</sup> | `results/tutorial/subtrees`

<sup>*</sup> Individual tables are available as TSV linelists in `results/tutorial/linelists`.  
<sup>†</sup> Visualize breakpoints with `less -S` or [Visual Studio ANSI Colors](https://marketplace.visualstudio.com/items?itemName=iliazeus.vscode-ansi).  
<sup>‡</sup>  Upload Auspice JSON trees to <https://auspice.us/>.

## Configuration

1. Create a new directory for your data.

    ```bash
    mkdir -p data/custom
    ```

1. Copy over your `metadata.tsv` and unaligned `sequences.fasta` to `data/custom`.

    > - Note: `metadata.tsv` MUST have at minimum the columns `strain`, `date`, `country`.  
    > - Note: The first column MUST be `strain`.

1. Create a profile for your custom build.

    ```bash
    scripts/create_profile.sh --data data/custom
    ```

    ```text
    2022-06-17 09:15:06     Searching for metadata (data/custom/metadata.tsv)
    2022-06-17 09:15:06     SUCCESS: metadata found
    2022-06-17 09:15:06     Checking for 3 required metadata columns (strain date country)
    2022-06-17 09:15:06     SUCCESS: 3 columns found.
    2022-06-17 09:15:06     Searching for sequences (data/custom/sequences.fasta)
    2022-06-17 09:15:06     SUCCESS: Sequences found
    2022-06-17 09:15:06     Checking that the metadata strains match the sequence names
    2022-06-17 09:15:06     SUCCESS: Strain column matches sequence names
    2022-06-17 09:15:06     Creating new profile directory (my_profiles/custom)
    2022-06-17 09:15:06     Creating build file (my_profiles/custom/builds.yaml)
    2022-06-17 09:15:06     Adding default input data (defaults/inputs.yaml)
    2022-06-17 09:15:06     Adding custom input data (data/custom)
    2022-06-17 09:15:06     Adding `custom` as a build
    2022-06-17 09:15:06     Creating system configuration (my_profiles/custom/config.yaml)
    2022-06-17 09:15:06     Adding default system resources
    2022-06-17 09:15:06     Done! The custom profile is ready to be run with:

                            snakemake --profile my_profiles/custom
    ```

    > - Note: you can add the param `--controls` to add a `controls` build that will run in parallel.
    > - Note: The `controls` build analyzes a dataset of positive and negative recombinant sequences, and adds \~30 min to the runtime.

1. Edit `my_profiles/custom/config.yaml`, so that the `jobs` and `default-resources` match your system.

    > Note: For HPC environments, see the [High Performance Computing](https://github.com/ktmeaton/ncov-recombinant#high-performance-computing) section.

    ```yaml
    #------------------------------------------------------------------------------#
    # System config
    #------------------------------------------------------------------------------#

    # Maximum number of jobs to run
    jobs : 2

    # Default resources for a SINGLE JOB
    default-resources:
    - cpus=2
    - mem_mb=8000
    - time_min=120
    ```

1. Do a dry run to confirm setup.

    ```bash
    snakemake --profile my_profiles/custom --dry-run
    ```

1. Run your custom profile.

    ```bash
    snakemake --profile my_profiles/custom
    ```

## High Performance Computing (HPC)

`ncov-recombinant` can alternatively be dispatched using the SLURM job submission system.

1. Create an HPC-compatible profile to store your build configuration.

    ```bash
    scripts/create_profile.sh --data data/custom --hpc
    ```

    ```text
    2022-06-17 09:16:55     Searching for metadata (data/custom/metadata.tsv)
    2022-06-17 09:16:55     SUCCESS: metadata found
    2022-06-17 09:16:55     Checking for 3 required metadata columns (strain date country)
    2022-06-17 09:16:55     SUCCESS: 3 columns found.
    2022-06-17 09:16:55     Searching for sequences (data/custom/sequences.fasta)
    2022-06-17 09:16:55     SUCCESS: Sequences found
    2022-06-17 09:16:55     Checking that the metadata strains match the sequence names
    2022-06-17 09:16:55     SUCCESS: Strain column matches sequence names
    2022-06-17 09:16:55     Creating new profile directory (my_profiles/custom-hpc)
    2022-06-17 09:16:55     Creating build file (my_profiles/custom-hpc/builds.yaml)
    2022-06-17 09:16:55     Adding default input data (defaults/inputs.yaml)
    2022-06-17 09:16:55     Adding custom input data (data/custom)
    2022-06-17 09:16:55     Adding `custom` as a build
    2022-06-17 09:16:55     Creating system configuration (my_profiles/custom-hpc/config.yaml)
    2022-06-17 09:16:55     Adding default HPC system resources
    2022-06-17 09:16:56     Done! The custom-hpc profile is ready to be run with:

                            snakemake --profile my_profiles/custom-hpc
    ```

2. Edit `my_profiles/custom-hpc/config.yaml` to specify the number of `jobs` and `default-resources` to use.

    ```yaml
    # Maximum number of jobs to run
    jobs : 4

    # Default resources for a SINGLE JOB
    default-resources:
    - cpus=64
    - mem_mb=64000
    - time_min=720
    ```

3. Dispatch the workflow using the slurm wrapper script:

    ```bash
    scripts/slurm.sh --profile my_profiles/custom-hpc
    ```

4. Use the `--help` parameter to get additional options for SLURM dispatch.

    ```bash
    scripts/slurm.sh --help
    ```

    ```text
    usage: bash slurm.sh [-h] [--profile PROFILE] [--conda-env CONDA_ENV] [--target TARGET] [--partition PARTITION] [--cpus CPUS] [--mem MEM]

            Dispatch a Snakemake pipeline using SLURM.

            Required arguments:
                    --profile PROFILE                Snakemake profile to execute (ex. profiles/tutorial-hpc)

            Optional arguments:
                    --partition PARTITION            Partition to submit jobs to with SLURM.
                    --conda-env CONDA_ENV            Conda environment to use. (default: ncov-recombinant)
                    --target TARGET                  Snakemake target(s) to execute (default: all)
                    --cpus CPUS                      CPUS to use for the main pipeline. (default: 1)
                    --mem MEM                        Memory to use for the ain pipeline. (default: 4GB)
                    -h, --help                       Show this help message and exit.
    ```

## Troubleshooting

- Unlock the workflow after a failed run:

    ```bash
    snakemake --profile profiles/tutorial --unlock
    ```

- Logs for each rule will be stored at: `logs/<rule>/<build>_<date>.txt`
- If using slurm (`profiles/hpc`) the master log will be at: `logs/ncov-recombinant/ncov-recombinant_<date>_<jobid>.log`

## Credits

[ncov-recombinant](https://github.com/ktmeaton/ncov-recombinant) is built and maintained by [Katherine Eaton](https://ktmeaton.github.io/) at the [National Microbiology Laboratory (NML)](https://github.com/phac-nml) of the Public Health Agency of Canada (PHAC).

<table>
  <tr>
    <td align="center"><a href="https://ktmeaton.github.io"><img src="https://s.gravatar.com/avatar/0b9dc28b3e64b59f5ce01e809d214a4e?s=80" width="100px;" alt=""/><br /><sub><b>Katherine Eaton</b></sub></a><br /><a href="https://github.com/ktmeaton/ncov-recombinant/commits?author=ktmeaton" title="Code">💻</a> <a href="https://github.com/ktmeaton/ncov-recombinant/commits?author=ktmeaton" title="Documentation">📖</a> <a href="#design-ktmeaton" title="Design">🎨</a> <a href="#ideas-ktmeaton" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-ktmeaton" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#maintenance-ktmeaton" title="Maintenance">🚧</a></td>
  </tr>
</table>

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/nextstrain/nextclade"><img src="https://avatars.githubusercontent.com/u/22159334?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Nextstrain (Nextclade)</b></sub></a><br /><a href="#data-nextstrain" title="Data">🔣</a> <a href="#plugin-nextstrain" title="Plugin/utility libraries">🔌</a></td>
    <td align="center"><a href="https://github.com/lenaschimmel/sc2rf"><img src="https://avatars.githubusercontent.com/u/1325019?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Lena Schimmel (sc2rf)</b></sub></a><br /><a href="#plugin-lenaschimmel" title="Plugin/utility libraries">🔌</a></td>
    <td align="center"><a href="https://github.com/yatisht/usher"><img src="https://avatars.githubusercontent.com/u/34664884?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Yatish Turakhia (UShER)</b></sub></a><br /><a href="#data-yatisht" title="Data">🔣</a> <a href="#plugin-yatisht" title="Plugin/utility libraries">🔌</a></td>
    <td align="center"><a href="https://github.com/yatisht/usher"><img src="https://avatars.githubusercontent.com/u/186983?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Angie Hinrichs (UShER)</b></sub></a><br /><a href="#data-AngieHinrichs" title="Data">🔣</a> <a href="#plugin-AngieHinrichs" title="Plugin/utility libraries">🔌</a></td>
    <td align="center"><a href="https://www.inspq.qc.ca/en/auteurs/2629/all"><img src="https://ui-avatars.com/api/?name=Benjamin-Delisle?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Benjamin Delisle</b></sub></a><br /><a href="https://github.com/ktmeaton/ncov-recombinant/issues?q=author%3Abenjamindeslisle" title="Bug reports">🐛</a> <a href="https://github.com/ktmeaton/ncov-recombinant/commits?author=benjamindeslisle" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://ca.linkedin.com/in/dr-vani-priyadarsini-ikkurti-4a2ab676"><img src="https://ui-avatars.com/api/?name=Vani Priyadarsini Ikkurthi?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Vani Priyadarsini Ikkurthi</b></sub></a><br /><a href="https://github.com/ktmeaton/ncov-recombinant/issues?q=author%3Avanipriyadarsiniikkurthi" title="Bug reports">🐛</a> <a href="https://github.com/ktmeaton/ncov-recombinant/commits?author=vanipriyadarsiniikkurthi" title="Tests">⚠️</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
