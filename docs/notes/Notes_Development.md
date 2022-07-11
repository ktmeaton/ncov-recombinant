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
- Make `exclude_clades` param of `nextclade_recombinants` completely optional.
- Add `B.1.438.1` to `clades` for `proposed808`.
- Add `B.1.631` and `B.1.634` `clades` for XB.

## Data

- Add proposed771 (BA.5,BA.2) to positive controls.
- Designated recombinants currently not included in controls:

  - XA | OU143858.1, OU106081.1
  - XB | OK219662.1, OK292107.1
  - XC | No public genomes, restricted to Japan
  - XK | No public genomes
  - XT | No public genomes, restricted to South Africa
  - XU | EPI_ISL_10523603
  - XV | OX099731.1, OX097667.1 | Restricted to Denmark and Italy
  - XY | OW680552.1, ON350451.1
  - XZ | ON388919.1, ON591206.1
  - XAB | EPI_ISL_11300019
  - XAC | EPI_ISL_12683057
  - XAD | EPI_ISL_12523233
  - XAE | ON034711.1, OM999631.1
  - XAF | ON588970.1, ON674975.1
  - XAG | EPI_ISL_13068320
  - XAH | EPI_ISL_13253581
