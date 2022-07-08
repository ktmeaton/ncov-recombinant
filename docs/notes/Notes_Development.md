# Development

## Workflow

- Change parent clade nomenclature from `Omicron/21K` to `Omicron/BA.1/21K`.
- Identify false positives if the recombinant region doesn't have a unique substitution.
- Remove all subtree related rules (#52)
- Use latest protobufs rather than time-stamped (#54)
- Remove `sc2rf` debug mode.

## Programs

- Upgrade `nextclade` from `v1.11.0` to `v2.2.0`.

## Output

- Renamed `parents` column to `parents_clade`.
- Added `parents_lineage` column.
- Restrict `nextclade` output to `fasta,tsv` (alignment and QC table).
- Remove subtrees.

## Params

- Tested out `--enable-deletions` for `sc2rf` again, caused issues for `XD`, as the first breakpoint no longer contains a breakpoint motif.

## Data

- Add proposed771 (BA.5,BA.2) to positive controls.
