# Development

## Params

1. New optional param `motifs` for rule `sc2rf_recombinants`.
1. New param `weeks` for new rule `plot`.
1. Removed `prev_linelist` param.

## Output

1. Switch from a pdf `report` to powerpoint slides for better automation.
1. Create summary plots.
1. Split `report` rule into `linelist` and `report`.

## Workflow

1. New rule `plot`.
1. Changed growth calculation from a comparison to the previous week to a score of sequences per day.
1. Assign a `cluster_id` according to the first sequence observed in the recombinant lineage.
1. Define a recombinant lineage as a group of sequences that share the same:
    - Lineage assignment
    - Parents
    - Breakpoints or phylogenetic placement (subtree)
1. For some sequences, the breakpoints are inaccurate and shifted slightly due to ambiguous bases. These sequences can be assigned to their corresponding cluster because they belong to the same subtree.
1. For some lineages, global prevalence has exceeded 500 sequences (which is the subtree size used). Sequences of these lineages are split into different subtrees. However, they can be assigned to the correct cluster/lineage, because they have the same breakpoints.
1. Confirmed not to use deletions define recombinants and breakpoints (differs from published)?

## Programs

1. Move `sc2rf_recombinants.py` to `postprocess.py` in ktmeaton fork of `sc2rf`.
1. Add false positives filtering to `sc2rf_recombinants` based on parents and breakpoints.

## Docs

1. Add section `Configuration` to `README.md`.
