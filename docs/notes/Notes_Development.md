# Development

## Workflow

1. Error catching in `plot` and `report` when no designated sequences are present.
1. Added new script `parents.py` to summarize recombinant sequences by parent.
1. Added new plots and report section for parents summary.
1. Make `plot` and `report` more dynamic with regards to plots.
1. Exclude reference genome from alignment until `faToVcf`.
1. Confirmed that `lambda wildcards` is necessary for output and params.

## Output

1. Output new file `parents.tsv` to summarize recombinant sequences by parent.
1. Order the colors/legend of the stacked bar `plots` by number of sequences.
1. Include lineage and cluster id in filepaths of largest plots and tables.

## Params

1. Add new optional param `max_placements` to rule `linelist`.
1. Remove `--show-private-mutations` from `debug_args` of rule `sc2rf`.
1. Add optional param `--sc2rf-dir` to `sc2rf` to enable execution outside of `sc2rf` dir.
1. Add params `--output-csv` and `--output-ansi` to the wrapper `scripts/sc2rf.sh`.

## Programs

1. Upgrade UShER to v0.5.4 (possible was in ver prior?)

## Data

1. Rename `data/controls` to `data/positives`.
1. Consolidate `positive` and `negative` builds into `profiles/controls`.