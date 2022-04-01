# ncov-recombinant

SARS-CoV-2 recombinant sequence detection.

1. Align sequences and perform clade/lineage assignments with [Nextclade](https://github.com/nextstrain/nextclade).
1. Identify parental clades and plot breakpoints with [sc2rf](https://github.com/lenaschimmel/sc2rf).
1. Phylogenetically place recombinant sequences with [UShER](https://github.com/yatisht/usher).

## Output

### Line list

| strain                    | country | date       | Nextclade_clade | Nextclade_pango | sc2rf_clades | usher_pango_lineage | usher_subtree |
| ------------------------- | ------- | ---------- | --------------- | --------------- | ------------ | ------------------- | ------------- |
| England/PLYM-332E079/2022 | England | 2022-01-18 | recombinant     | XF              | 21J/BA.1     | proposed441         | 1             |
| England/PLYM-336A651/2022 | England | 2022-01-20 | recombinant     | XF              | 21J/BA.1     | proposed441         | 1             |
| England/ALDP-31AE19E/2022 | England | 2022-01-06 | recombinant     | XF              | 21J/BA.1     | proposed422         | 1             |
|USA/VT-CDCBI-CRSP_LEYQGGQYKC7CTXDR/2022|USA|2022-02-03|recombinant|XE|BA.1/BA.2|proposed467|2|
|USA/VT-CDCBI-CRSP_3IGFKAUB6STYVNPK/2022|USA|2022-02-14|recombinant|XE|BA.1/BA.2|proposed467|2|
|USA/VT-CDCBI-CRSP_HOVIFDUIEJBVOGLK/2022|USA|2022-02-16|recombinant|XE|BA.1/BA.2|proposed467|2|

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

2. Install dependencies in a conda environment (`ncov-recombinant`). This will take a while ☕:

    ```bash
    mamba env create -f workflow/envs/environment.yaml
    conda activate ncov-recombinant
    ```

## Test

- Testing uses the "controls" dataset `data/controls`.
- These are publicly available recombinant sequences from [pango-designation](https://github.com/cov-lineages/pango-designation) issues.
- Testing uses the system profile `profiles/laptop`.
- This specifies system resources of 1 cpus and 4 GB of memory.

> Tip: Remember to run `conda activate ncov-recombinant` before running the commands below!

1. Preview the run configuration.

    ```bash
    snakemake --profile profiles/laptop print_config
    ```

1. Preview the commands that are going to be run.

    ```bash
    snakemake --profile profiles/laptop --dryrun --printshellcmds
    ```

1. Run the workflow.

    ```bash
    snakemake --profile profiles/laptop
    ```

1. Inspect the output:
    - Line list: `results/controls/summary.tsv`
    - Breakpoints: `results/controls/sc2rf.txt`
    - Trees: `results/controls/subtrees_collapse`

## SLURM

The workflow can be dispatched using the SLURM job submission system. In `profiles/hpc`, modify the `partition` name in `default-resources` according to your system partition. Then dispatch the workflow using the following command, where `MyPartition` is replaced with your local value:

```bash
bash scripts/slurm.sh --profile profiles/hpc --partition MyPartition
```

## Troubleshooting

- Unlock the workflow after a failed run:

    ```bash
    snakemake --profile profiles/laptop --unlock
    ```

- Logs for each rule will be stored at: `logs/<rule>/<build>_<date>.txt`
- If using slurm (`profiles/hpc`) the master log will be at: `logs/slurm/ncov-recombinant_<date>_<jobid>.log`
