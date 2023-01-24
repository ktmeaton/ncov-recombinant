# Development

This is a minor release aimed towards...

## Dataset

- [Issue #210](https://github.com/ktmeaton/ncov-recombinant/issues/210): Handle numeric strain names.

## Resources

- [Issue #185](https://github.com/ktmeaton/ncov-recombinant/issues/185): Simplify creation of the pango-lineage nomenclature phylogeny to use the [lineage_notes.txt](https://github.com/cov-lineages/pango-designation/blob/master/lineage_notes.txt) file and the [pango_aliasor](https://github.com/corneliusroemer/pango_aliasor) library.

## sc2rf

- [Issue #195](https://github.com/ktmeaton/ncov-recombinant/issues/195): Add bypass to intermission allele ratio for edge cases.
- [Issue #204](https://github.com/ktmeaton/ncov-recombinant/issues/204): Add special handling for XBB sequenced with ARTIC v4.1 and dropout regions.
- [Issue #205](https://github.com/ktmeaton/ncov-recombinant/issues/205): Add new column `parents_conflict` to indicate whether the reported lineages from covSPECTRUM conflict with the reported parental clades from `sc2rf.
- [Issue #213](https://github.com/ktmeaton/ncov-recombinant/issues/213): Add `XBK` to auto-pass lineages.
- The order of the `postprocessing.py` was rearranged to have more comprehensive details for auto-pass lineages.
- Add `XAN` to auto-pass lineages.

## Plot

- [Issue #209](https://github.com/ktmeaton/ncov-recombinant/issues/209): Restrict the palette for `rbd_level` to the range of `0:12`.
- [Issue #218](https://github.com/ktmeaton/ncov-recombinant/issues/218): Fix bug concerning data fragmentation with large numbers of sequences.
- [Issue #221](https://github.com/ktmeaton/ncov-recombinant/issues/221): Remove parameter `--singletons` in favor of `--min-cluster-size` to control cluster size in plots.

## Validate

### Designated Lineages

- [Issue #217](https://github.com/ktmeaton/ncov-recombinant/issues/217): `XBB.1.5`
- [Issue #196](https://github.com/ktmeaton/ncov-recombinant/issues/196): `XBF`
- [Issue #206](https://github.com/ktmeaton/ncov-recombinant/issues/206): `XBG`
- [Issue #196](https://github.com/ktmeaton/ncov-recombinant/issues/198): `XBH`
- [Issue #199](https://github.com/ktmeaton/ncov-recombinant/issues/199): `XBJ`
- [Issue #213](https://github.com/ktmeaton/ncov-recombinant/issues/213): `XBK`
- [Issue #219](https://github.com/ktmeaton/ncov-recombinant/issues/219): `XBL`
- [Issue #215](https://github.com/ktmeaton/ncov-recombinant/issues/215): `XBM`
- [Issue #197](https://github.com/ktmeaton/ncov-recombinant/issues/197): `XBN`

### Proposed Lineages

- [Issue #203](https://github.com/ktmeaton/ncov-recombinant/issues/203): `proposed1305`
- [Issue #208](https://github.com/ktmeaton/ncov-recombinant/issues/208): `proposed1340`
- [Issue #211](https://github.com/ktmeaton/ncov-recombinant/issues/211): `proposed1393`
- [Issue #212](https://github.com/ktmeaton/ncov-recombinant/issues/212): `proposed1425`
- [Issue #214](https://github.com/ktmeaton/ncov-recombinant/issues/214): `proposed1440`
- [Issue #216](https://github.com/ktmeaton/ncov-recombinant/issues/216): `proposed1444`
- proposed1576
