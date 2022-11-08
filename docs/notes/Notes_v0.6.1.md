# v0.6.1

This is a minor bugfix release aimed towards resolving network connectivity errors and catching false positives.

## sc2rf

- [Issue #195](https://github.com/ktmeaton/ncov-recombinant/issues/195): Consider alleles outside of parental regions as intermissions (conflicts) to catch false positives.
- [Issue #201](https://github.com/ktmeaton/ncov-recombinant/issues/201): Make LAPIS query of covSPECTRUM optional, to help with users with network connectivity issues. This can be set with the flag `lapis: false` in builds under the rule `sc2rf_recombinants`.
- [Issue #202](https://github.com/ktmeaton/ncov-recombinant/issues/202): Document connection errors related to LAPIS and provide options for solutions.
