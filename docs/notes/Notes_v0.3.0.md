# v0.3.0

## Major Changes

1. Default parameters have been updated! Please regenerate your profiles/builds with:

    ```bash
    bash scripts/create_profile.sh --data data/custom
    ```

1. Rule outputs are now in sub-directories for a cleaner `results` directory.
1. The in-text report (`report.pptx`) statistics are no longer cumulative counts of all sequences. Instead they, will match the reporting period in the accompanying plots.

## Bug Fixes

1. Improve subtree collapse effiency (#35).
1. Improve subtree aesthetics and filters (#20).
1. Fix issues rendering as float (#29).
1. Explicitly control the dimensions of plots for powerpoint embedding.
1. Remove hard-coded `extra_cols` (#26).
1. Fix mismatch in lineages plot and description (#21).
1. Downstream steps no longer fail if there are no recombinant sequences (#7).

## Workflow

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

## Data

1. Create new controls datasets:

    - `controls-negatives`
    - `controls-positives`
    - `controls`

1. Add versions to `genbank_accessions` for `controls`.

## Programs

1. Upgrade UShER to v0.5.4 (possibly this was done in a prior ver).
1. Remove `taxonium` and `chronumental` from the conda env.

## Parameters

1. Add parameters to control whether negatives and false_positives should be excluded:

    - `exclude_negatives: false`
    - `false_positives: false`

1. Add new optional param `max_placements` to rule `linelist`.
1. Remove `--show-private-mutations` from `debug_args` of rule `sc2rf`.
1. Add optional param `--sc2rf-dir` to `sc2rf` to enable execution outside of `sc2rf` dir.
1. Add params `--output-csv` and `--output-ansi` to the wrapper `scripts/sc2rf.sh`.
1. Remove params `nextclade_ref` and `custom_ref` from rule `nextclade`.
1. Change `--breakpoints 0-10` in `sc2rf`.

## Continuous Integration

1. Re-rename tutorial action to pipeline, and add different jobs for different profiles:

    - Tutorial
    - Controls (Positive)
    - Controls (Negative)
    - Controls (All)

## Output

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
