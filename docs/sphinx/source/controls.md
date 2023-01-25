## Controls

### Genbank

- After completing the tutorial, a good next step is to run the `controls` build.
- This build analyzes publicly available sequences in [`data/controls`](https://github.com/ktmeaton/ncov-recombinant/tree/master/data/controls), which include recombinant ("positive") and non-recombinant ("negative") sequences.
- Instructions for how to include the `controls` in your custom build are in the [configuration](https://github.com/ktmeaton/ncov-recombinant#configuration) section.

1. Run the workflow.

    ```bash
    snakemake --profile profiles/controls
    ```

### GISAID

- For GISAID users, a [comprehensive strain list](https://github.com/ktmeaton/ncov-recombinant/blob/dev/data/controls-gisaid/strains.txt) is provided that includes all designated recombinants to date (`XA` - `XBE`). This dataset includes 600+ sequences, and can be used for in-depth validation and testing.
- It is recommended to use the "Input for the Augur pipeline" option, to download a `tar` compressed archive of metadata and sequences to `data/controls-gisaid/`.
    [![gisaid_download](../../../images/gisaid_download.png)](https://www.epicov.org/)

1. Prep the input metadata and sequences.

    ```bash
    cd data/controls-gisaid
    tar -xvf gisaid_auspice_input_hcov-19_*.tar
    mv *sequences.fasta sequences.fasta
    # Retain minimal metadata columns, to avoid non-ascii characters
     csvtk cut -t -l -f 'strain,date,country,gisaid_epi_isl,pangolin_lineage' *.metadata.tsv > metadata.tsv
    cd ../..
    ```

1. Run the workflow.

    ```bash
    # Option 1: Local testing
    snakemake --profile profiles/controls-gisaid

    # Option 2: High Performance Computing with SLURM
    scripts/slurm.sh --profile profiles/controls-gisaid
    ```
