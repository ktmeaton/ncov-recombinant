# Development

The newly designated `XAS` and `XAZ` pose a challenge for recombinant detection using diagnostic alleles. The first region of `XAS` could be either `BA.5` or `BA.4` based on subsitutions, but is mostly likely `BA.4` based on deletions. Since the region contains no diagnostic alleles to discriminate `BA.5` vs. `BA.4`, breakpoints cannot be detected by `sc2rf`.

Similarly for `XAZ`, the `BA.2` segments do not contain any `BA.2` diagnostic alleles, but instead are all reversion from `BA.5` alleles. The `BA.2` parent was discovered by deep, manual investigation in the corresponding pango-designation issue. Since the `BA.2` regions contain no diagnostic for `BA.2`, breakpoints cannot be detected by `sc2rf`.

The current solution, is auto-passing...

TBD `XN` and `XP`.

- [Issue #78](https://github.com/ktmeaton/ncov-recombinant/issues/78): Add new param `max_breakpoint_len` to `sc2rf` to control false positive BA.5/BA.2 recombinants.
- [Issue #87](https://github.com/ktmeaton/ncov-recombinant/issues/87): `XAZ` nextclade assignments will auto-pass `sc2rf`.
- [Issue #91](https://github.com/ktmeaton/ncov-recombinant/issues/91): Upgrade `Nextclade` to `v2.5.0`.

- Remove parameter `lapis` from `sc2rf_recombinants`. Querying [LAPIS](https://lapis.cov-spectrum.org/) for parental lineages is no longer experimental and is now an essential component.
- Reduce postive and negative controls to one sequence per clade, to allow more diversity.
- `nextclade` and `nextclade-no-recom` for `sc2rf/postprocess.py`. The first is used to find recombinant lineages to auto-pass sc2rf. The second is used to get mutations for cov-spectrum.
- Add `--summary` as param to `report`.
