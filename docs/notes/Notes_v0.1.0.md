# v0.1.0

1. Add Stage 1: Nextclade.
1. Add Stage 2: sc2rf.
1. Add Stage 3: UShER.
1. Add Stage 4: Summary.
1. Add Continuous Integration workflows: `lint`, `test`, `pipeline`, and `release`.
1. New representative controls dataset:

    - Exclude XA because this is an Alpha recombinant (poor lineage accuracy).
    - Exclude XB because of [current issue](https://github.com/summercms/covid19-pango-designation/commit/26b7359e34a0b2f122215332b6495fea97ff3fe7)
    - Exclude XC because this is an Alpha recombinant (poor lineage accuracy).
    - Exclude XD because there are no public genomes.
    - Exclude XK because there are no public genomes.
