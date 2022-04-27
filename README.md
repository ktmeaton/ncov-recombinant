# ncov-recombinant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/ktmeaton/ncov-recombinant/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/ktmeaton/ncov-recombinant.svg)](https://github.com/ktmeaton/ncov-recombinant/issues)
[![Install CI](https://github.com/ktmeaton/ncov-recombinant/actions/workflows/install.yaml/badge.svg)](https://github.com/ktmeaton/ncov-recombinant/actions/workflows/install.yaml)
[![Test CI](https://github.com/ktmeaton/ncov-recombinant/actions/workflows/test.yaml/badge.svg)](https://github.com/ktmeaton/ncov-recombinant/actions/workflows/test.yaml)
[![Pipeline CI](https://github.com/ktmeaton/ncov-recombinant/actions/workflows/pipeline.yaml/badge.svg)](https://github.com/ktmeaton/ncov-recombinant/actions/workflows/pipeline.yaml)

SARS-CoV-2 recombinant sequence detection inspired by [nextstrain/ncov](https://github.com/nextstrain/ncov).

1. Align sequences and perform clade/lineage assignments with [Nextclade](https://github.com/nextstrain/nextclade).
1. Identify parental clades and plot recombination breakpoints with [sc2rf](https://github.com/lenaschimmel/sc2rf).
1. Phylogenetically place recombinant sequences with [UShER](https://github.com/yatisht/usher).

## Output

### Line list

|                 strain                  | lineage | parents                           |    date    | country  | breakpoints |
|:---------------------------------------:|:-------:| --------------------------------- |:----------:|:--------:|:-----------:|
|        England/BRBR-3899D04/2022        |   XE    | Omicron/BA.1/21K,Omicron/BA.2/21L | 2022-02-27 | England  | 10450:11536 |
|        England/ALDP-31AE19E/2022        |   XF    | Delta/21J,Omicron/BA.1/21K        | 2022-01-06 | England  | 21619:21761 |
|        England/PLYM-336A651/2022        |   XF    | Delta/21J,Omicron/BA.1/21K        | 2022-01-20 | England  | 21619:21761 |
|      USA/TN-CDC-ASC210559252/2021       |   XF    | Delta/21J,Omicron/BA.1/21K        | 2021-12-31 |   USA    | 21988:22577 |
|       Scotland/QEUH-37E04A0/2022        |   XG    | Omicron/BA.1/21K,Omicron/BA.2/21L | 2022-02-21 | Scotland |  5387:8392  |
|        England/MILK-385C31A/2022        |   XH    | Omicron/BA.1/21K,Omicron/BA.2/21L | 2022-02-24 | England  | 10450:11536 |
| USA/VT-CDCBI-CRSP_3IGFKAUB6STYVNPK/2022 |   XJ    | Omicron/BA.1/21K,Omicron/BA.2/21L | 2022-02-14 |   USA    | 15241:15713 |
| USA/NY-Broad-CRSP_WH5TJZ42BYV4BC3T/2022 |   XM    | Omicron/BA.1/21K,Omicron/BA.2/21L | 2022-03-28 |   USA    | 18164:19954 |
|        England/MILK-38AA91B/2022        |   XQ    | Omicron/BA.1/21K,Omicron/BA.2/21L | 2022-02-28 | England  |  4322:5385  |
|        USA/CO-CDC-FG-248528/2022        |   XS    | Delta/21J,Omicron/BA.1/21K        | 2022-01-19 |   USA    | 10030:10448 |

### Breakpoints

![sc2rf_output](images/sc2rf_output.png)

### Phylogenetic Context

![usher_output](images/usher_output.png)

## Install

1. Clone the repository:

    ```bash
    # https
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

1. Preview the commands that are going to be run.

    ```bash
    snakemake --profile profiles/tutorial --dryrun --printshellcmds
    ```

1. Run the workflow.

    ```bash
    snakemake --profile profiles/tutorial
    ```

1. Inspect the output

    - Sample line list:

        ```bash
        csvtk pretty -t results/tutorial/linelist.tsv | less -S
        ```

    - Breakpoints:

        ```bash
        less -S results/tutorial/sc2rf.recombinants.ansi.txt
        ```

    - Trees: Upload Auspice JSON in `results/tutorial/subtrees_collapse/` to <https://auspice.us/>

## SLURM

The workflow can be dispatched using the SLURM job submission system. In `profiles/hpc`, modify the `partition` name in `default-resources` according to your system partition. Then dispatch the workflow using the following command, where `MyPartition` is replaced with your local value:

```bash
bash scripts/slurm.sh --profile profiles/hpc --partition MyPartition
```

## Troubleshooting

- Unlock the workflow after a failed run:

    ```bash
    snakemake --profile profiles/tutorial --unlock
    ```

- Logs for each rule will be stored at: `logs/<rule>/<build>_<date>.txt`
- If using slurm (`profiles/hpc`) the master log will be at: `logs/ncov-recombinant/ncov-recombinant_<date>_<jobid>.log`

## Credits

- nextstrain/ncov: https://github.com/nextstrain/ncov
- nextstrain/nextclade: https://github.com/nextstrain/nextclade
- lenaschimmel/sc2rf: https://github.com/lenaschimmel/sc2rf
- yatisht/usher: https://github.com/yatisht/usher
