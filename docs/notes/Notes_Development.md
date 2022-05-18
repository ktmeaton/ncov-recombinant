# Development

## Params

1. New param `weeks` for new rule `plot`.
1. Removed `prev_linelist` param.

## Workflow

1. New rule `plot`.
1. Changed growth calculation from a comparison to the previous week to a score of sequences per day.

## Programs

1. Move `sc2rf_recombinants.py` to `postprocess.py` in ktmeaton fork of `sc2rf`.
1. Add false positives filtering to `sc2rf_recombinants` based on parents and breakpoints.

## Docs

1. Add section `Configuration` to `README.md`.

## To Do

### Priority

1. Split `report` rule into `linelist` and `recombinants`.

1. Should deletions be used to define recombinants and breakpoints?

    - Currently, no, it changes published breakpoints.

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
