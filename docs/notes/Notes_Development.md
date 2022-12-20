# Development

This is a minor bugfix release aimed towards...

## Dataset

- [Issue #210](https://github.com/ktmeaton/ncov-recombinant/issues/210): Handle numeric strain names.

## Resources

- [Issue #185](https://github.com/ktmeaton/ncov-recombinant/issues/185): Simplify creation of the pango-lineage nomenclature phylogeny to use the [lineage_notes.txt](https://github.com/cov-lineages/pango-designation/blob/master/lineage_notes.txt) file and the [pango_aliasor](https://github.com/corneliusroemer/pango_aliasor) library.

## sc2rf

- [Issue #204](https://github.com/ktmeaton/ncov-recombinant/issues/204): Add special handling for XBB sequenced with ARTIC v4.1 and dropout regions.
- [Issue #205](https://github.com/ktmeaton/ncov-recombinant/issues/205): Add new column `parents_conflict` to indicate whether the reported lineages from covSPECTRUM conflict with the reported parental clades from `sc2rf.
- [Issue #213](https://github.com/ktmeaton/ncov-recombinant/issues/213): Add `XBK` to auto-pass lineages.

- The order of the `postprocessing.py` was rearranged to have more comprehensive details for auto-pass lineages.
- Add `XAN` to auto-pass lineages.

## Plot

- [Issue #209](https://github.com/ktmeaton/ncov-recombinant/issues/209): Restrict the palette for `rbd_level` to the range of `0:12`.

## Validate

### Designated Lineages

- [Issue #196](https://github.com/ktmeaton/ncov-recombinant/issues/196): `XBF`
- [Issue #206](https://github.com/ktmeaton/ncov-recombinant/issues/206): `XBG`
- [Issue #196](https://github.com/ktmeaton/ncov-recombinant/issues/198): `XBH`
- [Issue #199](https://github.com/ktmeaton/ncov-recombinant/issues/199): `XBJ`
- [Issue #213](https://github.com/ktmeaton/ncov-recombinant/issues/213): `XBK`

### Proposed Lineages

- [Issue #203](https://github.com/ktmeaton/ncov-recombinant/issues/203): `proposed1305`
- [Issue #208](https://github.com/ktmeaton/ncov-recombinant/issues/208): `proposed1340`
