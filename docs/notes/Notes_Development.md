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

## To Do

### Priority

1. Experiment with the `motifs` param for `sc2rf_recombinants`.
1. Troubleshoot `sc2rf` update to `bd2a4009` which drops all deltacrons.

    - The last stable commit was `5ac8d04`.

### Misc

1. Remove the `resources` in config.yaml.
1. Investigate the reasons that X* lineages are excluded by `sc2rf`.
1. Add citations to report.
1. Update UShER to 0.5.3.
1. Plot recombinant breakpoints differently.
1. Edit Auspice json to change default colorings,filters,and panels (also sort).
1. Automate unit test update.
1. Not implemented recombinant lineages:

    - XA | Alpha recombinant (poor lineage accuracy)
    - XB | Conflicting designation [issue](https://github.com/summercms/covid19-pango-designation/commit/26b7359e34a0b2f122215332b6495fea97ff3fe7)
    - XC | Alpha recombinant (poor lineage accuracy)
    - XK | No public genomes
    - XT | No public genomes, South Africa
    - XU | No public genomes, India, Japan, Australia
