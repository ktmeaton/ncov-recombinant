# Development

## Workflow

- Change parent clade nomenclature from `Omicron/21K` to `Omicron/BA.1/21K`.
- Identify false positives if the recombinant region doesn't have a unique substitution.

## Programs

- Upgrade `nextclade` from `v1.11.0` to `v2.2.0`.

## Output

- Renamed `parents` column to `parents_clade`.
- Added `parents_lineage` column.
- Restrict `nextclade` output to `fasta,tsv` (alignment and QC table).
