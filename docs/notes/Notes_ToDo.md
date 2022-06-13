# To Do

Testing rule `plot` currently.

## Priority

1. Adjust all rule targets.
1. Use the build merge logic from usher.
1. Add Vani to credits (see Taxonium).
1. Re-rename tutorial action to pipeline, and add different jobs for different profiles.

    - Tutorial
    - Controls

## Misc

1. Troubleshoot the missing designated lineages in the controls report.
1. Add better filters to the Auspice JSON output (ex. `lineage_usher`).
1. Experiment with the `motifs` param for `sc2rf_recombinants`.
1. Troubleshoot `sc2rf` update to `bd2a4009` which drops all deltacrons.

    - The last stable commit was `5ac8d04`.

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
