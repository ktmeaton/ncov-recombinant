# Development

## Dataset

- `controls` was updated to in include 1 strain from `XBB` for a total of 22 positive controls. The 28 negative controls were unchanged from `v0.5.1`.
- `controls-gisaid` strain list was updated to include `XA` through to `XBE` for a total of 528 positive controls. This includes sublineages such as `XBB.1` and `XBB.1.2` which synchronizes with [Nextclade Dataset 2022-10-19](https://github.com/nextstrain/nextclade_data/releases/tag/2022-10-19). The 187 negatives controls were unchanged from `v0.5.1`.

## Nextclade

- [Issue #176](https://github.com/ktmeaton/ncov-recombinant/issues/176): upgrade Nextclade dataset to tag `2022-10-19` and upgrade Nextclade to `v2.7.0`.

## Lineage Tree

- [Issue #185](https://github.com/ktmeaton/ncov-recombinant/issues/185): Use nextclade dataset Auspice tree for lineage hierarchy. Previously, the phylogeny of lineages was constructed from the [cov-lineages website YAML](https://github.com/cov-lineages/lineages-website/blob/master/_data/lineages.yml). Instead, we now use the tree provided with nextclade datasets, to better synchronize the lineage model with the output.

Rather than creating the output tree in `resources/lineages.nwk`, the lineage tree will output to `results/BUILD/lineage_tree/tree.nwk`. This is because different builts might use different nextclade datasets, and so are build-specific results.

## sc2rf

- [Issue #179](https://github.com/ktmeaton/ncov-recombinant/issues/179): Fix bug where `sc2rf/recombinants.ansi.txt` is truncated.
- [Issue #180](https://github.com/ktmeaton/ncov-recombinant/issues/180): Fix recombinant sublineages (ex. XAY.1) missing their derived mutations in the `cov-spectrum_query`. Previously, the `cov-spectrum_query` mutations were only based on the parental alleles (before recombination). This led to sublinaeges (ex. `XAY.1`, `XAY.2`) all having the exact same query. Now, the `cov-spectrum_query` will include _all_ substitutions shared between all sequences in the `cluster_id`.
- [Issue #187](https://github.com/ktmeaton/ncov-recombinant/issues/187): Document bug that occurs if duplicate sequences are present, and the initial validation was skipped by not running `scripts/create_profile.sh`.

## Linelist

- [Issue #183](https://github.com/ktmeaton/ncov-recombinant/issues/183): Recombinant sublineages. When nextclade calls a lineage (ex. `XAY.1`) which is a sublineage of a sc2rf lineage (`XAY`), we prioritize the nextclade assignment.

## Plot

- [Issue #57](https://github.com/ktmeaton/ncov-recombinant/issues/57): Include substitutions within breakpoint intervals for breakpoint plots. This is a product of [Issue #180](https://github.com/ktmeaton/ncov-recombinant/issues/180) which provides access to _all_ substitutions.
- [Issue #112](https://github.com/ktmeaton/ncov-recombinant/issues/112): Fix bug where breakpoints plot image was out of bounds.
- [Issue #188](https://github.com/ktmeaton/ncov-recombinant/issues/188): Remove the breakpoints distribution axis (ex. `breakpoints_clade.png`) in favor of putting the legend at the top. This significant reduces plotting issues (ex. [Issue #112](https://github.com/ktmeaton/ncov-recombinant/issues/112)).

## Validate

### Designated Lineages

- [Issue #85](https://github.com/ktmeaton/ncov-recombinant/issues/85): `XAY`, updated controls
- [Issue #178](https://github.com/ktmeaton/ncov-recombinant/issues/178): `XAY.1`
- [Issue #172](https://github.com/ktmeaton/ncov-recombinant/issues/172): `XBB.1`
- [Issue #175](https://github.com/ktmeaton/ncov-recombinant/issues/175): `XBB.1.1`
- [Issue #184](https://github.com/ktmeaton/ncov-recombinant/issues/184): `XBB.1.2`
- [Issue #173](https://github.com/ktmeaton/ncov-recombinant/issues/173): `XBB.2`
- [Issue #174](https://github.com/ktmeaton/ncov-recombinant/issues/174): `XBB.3`
- [Issue #181](https://github.com/ktmeaton/ncov-recombinant/issues/181): `XBC.1`
- [Issue #182](https://github.com/ktmeaton/ncov-recombinant/issues/182): `XBC.2`
- [Issue #171](https://github.com/ktmeaton/ncov-recombinant/issues/171): `XBD`
- [Issue #177](https://github.com/ktmeaton/ncov-recombinant/issues/177): `XBE`
