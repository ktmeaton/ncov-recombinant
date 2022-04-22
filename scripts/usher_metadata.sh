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
    --extra-cols)
      extra_cols=$2
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

base_metadata="data/${base_input}/metadata.tsv"
nextclade="results/${build}/nextclade.metadata.tsv"
sc2rf="results/${build}/sc2rf.recombinants.tsv"
usher_clades="results/${build}/usher.clades.tsv"
usher_placement="results/${build}/usher.placement_stats.tsv"
issue_to_lineage="resources/issue_to_lineage.tsv"

default_cols="strain"
extract_cols="clade,usher_clade,Nextclade_pango,usher_pango_lineage,dataset,sc2rf_clades_filter,sc2rf_clades_regions_filter,sc2rf_breakpoints_regions_filter,usher_num_best"
rename_cols="Nextstrain_clade,Nextstrain_clade_usher,pangolin_lineage,pango_lineage_usher,dataset,parents,parents_regions,breakpoints,usher_placements"
rename_cols_final="clade_nextclade,clade_usher,lineage_nextclade,lineage_usher,dataset,parents,parents_regions,breakpoints,usher_placements"

csvtk merge -t -f "strain" ${nextclade} ${sc2rf} ${usher_clades} ${usher_placement} \
  | csvtk cut -t -f "${default_cols},${extra_cols},${extract_cols}" \
  | csvtk rename -t -f "${extract_cols}" -n "${rename_cols}" \
  | csvtk concat -t -u "?" - ${base_metadata} \
  | csvtk cut -t -f "${default_cols},${extra_cols},${rename_cols}" \
  | csvtk rename -t -f "${rename_cols}" -n "${rename_cols_final}" \
  | csvtk replace -t -f "lineage_usher" -p "proposed([0-9]+)" -k ${issue_to_lineage} -r "{kv}"
