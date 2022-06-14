# Development

## Workflow

1. Error catching in `plot` and `report` when no designated sequences are present.
1. Added new script `parents.py` to summarize recombinant sequences by parent.
1. Added new plots and report section for parents summary.
1. Make `plot` and `report` more dynamic with regards to plots.
1. Exclude reference genome from alignment until `faToVcf`.
1. Confirmed that `lambda wildcards` is necessary for output and params.
1. Include rule_name in message text and indicate log file.
1. By default, include negatives (`exclude_negatives: false`) and false_positives (`exclude_false_positives: false`).
1. Use sub-functions to better control optional parameters.
1. Move rule outputs to sub-directories.
1. Make sure all rules write to a log if possible.
1. Converted all rule inputs to snakemake rule variables.
1. Create and document a `create_profile.sh` script.

## Continuous Integration

1. Re-rename tutorial action to pipeline, and add different jobs for different profiles:

    - Tutorial
    - Controls

## Output

1. Output new file `parents.tsv` to summarize recombinant sequences by parent.
1. Order the colors/legend of the stacked bar `plots` by number of sequences.
1. Include lineage and cluster id in filepaths of largest plots and tables.
1. Rename linelist output.

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

## Params

1. Add new optional param `max_placements` to rule `linelist`.
1. Remove `--show-private-mutations` from `debug_args` of rule `sc2rf`.
1. Add optional param `--sc2rf-dir` to `sc2rf` to enable execution outside of `sc2rf` dir.
1. Add params `--output-csv` and `--output-ansi` to the wrapper `scripts/sc2rf.sh`.
1. Remove params `nextclade_ref` and `custom_ref` from rule `nextclade`.

## Programs

1. Upgrade UShER to v0.5.4 (possible was in ver prior?)

## Data

1. Create new dataset `negatives`:

    - X sequences from https://nextstrain.org/ncov/open/reference
1. Rename `data/controls` to `data/positives`.
1. Consolidate `positive` and `negative` builds into `profiles/controls`.
