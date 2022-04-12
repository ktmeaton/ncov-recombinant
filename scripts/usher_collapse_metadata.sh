#!/bin/bash

# -----------------------------------------------------------------------------
# Argument Parsing

while [[ $# -gt 0 ]]; do
  case $1 in
    --base-input)
      base_input=$2
      shift # past argument
      shift # past value
      ;;
    --build)
      build=$2
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

subtree_dir="results/${build}/subtrees_collapse"
base_metadata="data/${base_input}/metadata.tsv"
nextclade_metadata="results/${build}/nextclade.metadata.tsv"
clades_metadata="results/${build}/usher.clades.tsv"
usher_to_pango="data/controls/usher_to_pango.tsv"

for json in $(ls ${subtree_dir}/*.json); do
    prefix=${json%.*};
    strains=${prefix}.txt

    echo $strains

    # Create the base metadata
    csvtk grep -t -f "strain" -P ${strains} ${base_metadata} \
        | csvtk rename -t -f "pangolin_lineage" -n "pango_lineage" \
        > ${prefix}.base.tsv;

    # Sample metadata
    csvtk grep -t -f "strain" -P ${strains} ${nextclade_metadata} \
      | csvtk merge -t -f "strain" ${clades_metadata} - \
      | csvtk rename -t -f "clade" -n "Nextstrain_clade" \
      | csvtk rename -t -f "Nextclade_pango" -n "pango_lineage" \
      | csvtk rename -t -f "usher_pango_lineage" -n "pango_lineage_usher" \
       > ${prefix}.input.tsv;

    csvtk concat -t  ${prefix}.base.tsv  ${prefix}.input.tsv \
      | csvtk replace -t -f "pango_lineage_usher" -p "(proposed[0-9]+)" -k ${usher_to_pango} -r "{kv}" \
      > ${prefix}.tsv;

done
