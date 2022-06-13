# To Do

## Priority

1. Adjust all rule targets.
1. Move rule output to sub-directories
1. Use the usher_metadata from usher?
1. Use the build merge logic from usher.
1. Remove lambda wildcards from params.
1. Add Vani to credits (see Taxonium).
1. Include negatives by default.
1. Make sure all rules write to a log if possible.
1. Put the param checking in functions.
    - [x] `usher`
    - [ ] `usher_metadata`
    - [ ] `usher_subtree`
    - [ ] `summary`
    - [ ] `linelist`
    - [x] `plot`
    - [x] `report`
1. Include rule_name in message text and point to log file.
    - [x] `usher`
    - [x] `usher_stats`
    - [ ] `usher_metadata`
    - [ ] `usher_subtree_collapse`
    - [ ] `summary`
    - [ ] `linelist`
    - [x] `plot`
    - [x] `report`
1. Re-rename tutorial action to pipeline, and add different jobs for different profiles.
    - Tutorial
    - Negatives
    - Positives

## Misc

1. Rename linelist output.
    - `linelist.positives.tsv`   
    - `linelist.negatives.tsv`
    - `linelist.false_positives.tsv`
    - `linelist.lineages.tsv`
    - `linelist.parents.tsv`
1. Troubleshoot the missing designated lineages in the controls report.
1. Add better filters to the Auspice JSON output (ex. `lineage_usher`).
1. Experiment with the `motifs` param for `sc2rf_recombinants`.
1. Troubleshoot `sc2rf` update to `bd2a4009` which drops all deltacrons.

    - The last stable commit was `5ac8d04`.

1. Remove the `resources` in config.yaml.
1. Investigate the reasons that X* lineages are excluded by `sc2rf`.
1. Add citations to report.
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
    - XW | ...
    - XY | ...
