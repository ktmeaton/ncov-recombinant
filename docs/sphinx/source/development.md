## Developer's Guide

There are three main triggers to initate new development:

1. A new lineage dataset has been released: https://github.com/nextstrain/nextclade_data/releases
1. A new nextclade-cli has been released: https://github.com/nextstrain/nextclade/releases
1. A new recombinant lineage has been proposed: https://github.com/cov-lineages/pango-designation/issues?q=recombinant
1. A new recombinant lineage has been designated: https://github.com/cov-lineages/pango-designation/milestones. New designations _should_ be labelled as milestones.

Beging by creating a personal dev conda environment.

```bash
mamba env create -f workflow/envs/environment.yaml -n ncov-recombinant-dev
```

After completing a development trigger, proceed with the **Validation** section.

### Trigger 1 | New Lineage Dataset

1. Obtain the new dataset tag from: https://github.com/nextstrain/nextclade_data/releases.

1. Update all 3 dataset tags in `defaults/parameters.yaml`.

    For example, change all strings of `"2022-10-27T12:00:00Z"` to the new dataset tag for November such as `"2022-11-27T12:00:00Z"`.

    ```yaml
    - name: nextclade_dataset
      dataset: sars-cov-2
      tag: "2022-10-27T12:00:00Z"
      dataset_no-recomb: sars-cov-2-no-recomb
      tag_no-recomb: "2022-10-27T12:00:00Z"
      dataset_immune-escape: sars-cov-2-21L
      tag_immune-escape: "2022-10-27T12:00:00Z"
    ```

### Trigger 2 | New Nextclade CLI

1. Check that the new nextclade-cli has been made available on conda: https://anaconda.org
1. Update the following line in `workflow/envs/environment.yaml` to the newest version:

    ```yaml
    - bioconda::nextclade=2.8.0
    ```

1. Update the personal dev conda environment.

    ```bash
    mamba env update -f workflow/envs/environment.yaml -n ncov-recombinant-dev
    ```

### Trigger 3 | New Proposed Lineage

1. Create a new data directory.

    ```bash
    mkdir -p data/proposedXXX
    ```

1. Check the correponsing [pango-designation issue](https://github.com/cov-lineages/pango-designation/issues?q=recombinant) for a list of GISAID accessions.

1. Download 10-20 of these GISAID accessions from <https://gisaid.org/>. Please review the [GISAID Download](https://github.com/ktmeaton/ncov-recombinant#gisaid) section of the README to ensure the sequences and metadata are correctly formatted.

1. Create a new pipeline profile for this lineage.

    ```bash
    scripts/create_profile.sh --data data/proposedXXX
    ```

1. Run the pipeline up to `sc2rf` breakpoint detection.

    ```bash
    snakemake --profile my_profiles/proposedXXX results/proposedXXX/sc2rf/stats.tsv
    ```

    When finished, check the stats file and confirm whether `sc2rf_status` is `positive`, `sc2rf_parents` match the pango-designation issue information. If so, skip to the validation section.

    ```bash
    csvtk pretty -t results/proposedXXX/sc2rf/stats.tsv | less -S

    # Or
    csvtk cut -t -f "strain,sc2rf_status,sc2rf_parents,sc2rf_breakpoints" results/XBB/sc2rf/stats.tsv
    ```

1. Update/create `sc2rf` modes.  

    If `sc2rf_status` is not `positive`, command-line parameters for `sc2rf` will need to be tweaked. To begin with, run `sc2rf` manually with the following debugging parameters. And changing `--clades BA.2 BA.5.2` to a space separated list of potential parents.

    ```bash
    python3 sc2rf/sc2rf.py results/proposedXXX/nextclade/alignment.fasta \
      --ansi \
      --max-ambiguous 20 \
      --max-intermission-length 2 \
      --ignore-shared \
      --mutation-threshold 0.25 \
      --max-intermission-count 20 \
      --parents 0-10 \
      --breakpoints 0-10 \
      --unique 0 \
      --clades BA.2 BA.5.2
    ```

    If the potential parents don't appear in the output, they will need to be added to `sc2rf/mapping.csv` and the allele frequency database updated with:

    ```bash
    cd sc2rf/
    python3 sc2rf.py --rebuild-examples
    cd ..
    ```

    Then rerun the previous command and verify that the parents appear in the output. The next step is to increase the stringency of `--parents`, `--breakpoints`, `--unique`, and `--max-intermission-count` as much as possible.

    Once a parameter set is found, review the existing `sc2rf` modes in `defaults/parameters.yaml`. It is ideal to have as few modes as possible, so the first check is to see whether the new parameter set can be integrated into an existing mode. Failing that, a new mode should be created in the list to capture this recombinant.

    ```yaml
    - name: sc2rf
      mode:
      # Lineage specific validation)
        - XA:              "--clades 20I 20E 20F 20D             --ansi --parents 2   --breakpoints 1-3  --unique 2 --max-ambiguous 20 --max-intermission-length 2 --max-intermission-count 3  --ignore-shared --mutation-threshold 0.25"
        ...
        # Current Variants of Concern and Dominant Lineages
        - voc:             "--clades BA.2.10 BA.2.3.17 BA.2.3.20 BA.2.75 BA.4.6 BA.5.2 BA.5.3 XBB --ansi --parents 2-4 --breakpoints 1-5 --unique 1 --max-ambiguous 20 --max-intermission-length 2 --max-intermission-count 3  --ignore-shared --mutation-threshold 0.25"
    ```

1. Repeat steps 5 and 6, until the recombinant is successully identified by `sc2rf`.

### Trigger 4 | New Designated Lineage

1. Complete all steps for Trigger 3 | New Proposed Lineage, except:

    - Include no more than 10 representative sequences.
    - Make the data directory `data/X*` instead of `data/proposed*`.

1. Add the new designated lineage to the `gisaid-positive` dataset.

    This step expects all positive controls to be stored in individual directories starting with `data/X*`. Their metadata and sequences will be collated into `data/gisaid-positive`.

    ```bash
    # Remove authors and originating lab for non-ascii char
    cols=$(csvtk headers -t data/XA/metadata.tsv | grep -v -E "originating_lab|authors" | tr "\n" "," | sed 's/,$/\n/g')

    # Construct the metadata header
    csvtk cut -t -f "$cols" data/XA/metadata.tsv | head -n 1 > data/gisaid-positive/metadata.tsv

    # Extract metadata cols and concat for all X* lineages.
    for data_dir in $(ls -d data/X*); do
        csvtk cut -t -f "$cols" ${data_dir}/metadata.tsv | tail -n+2 >> data/gisaid-positive/metadata.tsv
    done

    # Combine all X* lineage sequences
    cat data/X*/sequences.fasta > data/gisaid-positive/sequences.fasta
    ```

1. Combine the `gisaid-positive` and `gisaid-negative` datasets into the `controls-gisaid` dataset.

    ```bash
    csvtk concat -t data/gisaid-positive/metadata.tsv data/gisaid-negative/metadata.tsv > data/controls-gisaid/metadata.tsv

    cat data/gisaid-positive/sequences.fasta data/gisaid-negative/sequences.fasta > data/controls-gisaid/sequences.fasta

    csvtk cut -t -f "strain" data/controls-gisaid/metadata.tsv | tail -n+2 > data/controls-gisaid/strains.txt
    ```

1. Run the `controls-gisaid` profile (recommend HPC with slurm).

    ```bash
    scripts/slurm.sh --profile profiles/controls-gisaid-hpc --conda-env ncov-recombinant-dev
    ```

1. Update the controls validation values if the `controls-gisaid` profile ran successfully.

    The file `defaults/validation.tsv` contains the expected values for all controlled datasets including: `tutorial`, `controls`, and `controls-gisaid`.

    ```bash
    # Construct headers
    echo -e "strain\tlineage\tbreakpoints\tparents_clade\tdataset" > defaults/validation.tsv

    # Tutorial
    csvtk cut -t -f "strain,lineage,breakpoints,parents_clade"  results/tutorial/linelists/linelist.tsv \
      | tail -n+2 \
      >> defaults/validation.tsv

    # Controls Genbank
    csvtk cut -t -f "strain,lineage,breakpoints,parents_clade"  results/controls/linelists/linelist.tsv \
      | csvtk mutate2 -t -n "dataset" -e '"controls"' \
      | tail -n+2 \
      >> defaults/validation.tsv

    # Controls GISAID
    csvtk cut -t -f "strain,lineage,breakpoints,parents_clade"  results/controls-gisaid/linelists/linelist.tsv \
      | csvtk mutate2 -t -n "dataset" -e '"controls-gisaid"' \
      | tail -n+2 \
      >> defaults/validation.tsv
    ```

### Validation

Run the `controls-gisaid` profile to test the new changes:

1. Tutorial

    ```bash
    scripts/slurm.sh --profile profiles/tutorial --conda-env ncov-recombinant-dev
    ```

2. Genbank Controls

    ```bash
    scripts/slurm.sh --profile profiles/controls-hpc --conda-env ncov-recombinant-dev
    ```

3. GISAID Controls

    ```bash
    scripts/slurm.sh --profile profiles/controls-gisaid-hpc --conda-env ncov-recombinant-dev
    ```

If the pipeline failed validation, check the end of the log for details on which samples failed and why.

```bash
less -S logs/ncov-recombinant/canada_$(date +'%Y-%m-%d').log
```

If the column that failed is only `lineage`, because lineage assignments have changed with the new dataset, simply update the values in `defaults/validation.tsv`. This is expected when upgrading nextclade-cli or the nextclade dataset.

If the column that failed is `breakpoints` or `parents_clade`, this indicates a more complicated issue with breakpoint detection. The most common reason is because `sc2rf` modes has been changed to capture a new lineage (see development trigger 3, new lineage, for more information). This presents an optimization challenge, and is solved by working through steps 5 and 6 of **Development: Trigger 3 | New Proposed Lineage** until sensitivity and specificity are restore for all lineages.
