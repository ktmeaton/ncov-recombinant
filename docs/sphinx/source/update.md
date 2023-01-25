## Update

> **Tip**: It is recommended to do a <a href="install.html">fresh install</a> in a separate directory to test a newer version.

After pulling a fresh copy of the git repository, don't forget to update your conda environment!

```bash
mamba env update -f workflow/envs/environment.yaml
```

After running the newly installed version, you can compare lineage assignment changes using the following script:

```bash
python3 scripts/compare_positives.py \
  --positives-1 old_pipeline_ver/results/controls/linelists/positives.tsv \
  --positives-2 new_pipeline_ver/results/controls/linelists/positives.tsv \
  --ver-1 "old_ver" \
  --ver-2 "new_ver" \
  --outdir compare/controls \
  --node-order alphabetical
```

A comparative report is provided for each major release:

- `v0.5.1` → `v0.6.0` : [docs/testing_summary_package/ncov-recombinant_v0.5.1_v0.6.0.html](https://ktmeaton.github.io/ncov-recombinant/docs/testing_summary_package/ncov-recombinant_v0.5.1_v0.6.0.html)
- `v0.4.2` → `v0.5.0` : [docs/testing_summary_package/ncov-recombinant_v0.4.2_v0.5.0.html](https://ktmeaton.github.io/ncov-recombinant/docs/testing_summary_package/ncov-recombinant_v0.4.2_v0.5.0.html)
