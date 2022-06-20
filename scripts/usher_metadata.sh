#!/bin/bash

# -----------------------------------------------------------------------------
# Argument Parsing

while [[ $# -gt 0 ]]; do
  case $1 in
    --base-metadata)
      base_metadata=$2
      shift # past argument
      shift # past value
      ;;
    --nextclade)
      nextclade=$2
      shift # past argument
      shift # past value
      ;;
    --sc2rf)
      sc2rf=$2
      shift # past argument
      shift # past value
      ;;
    --clades)
      clades=$2
      shift # past argument
      shift # past value
      ;;
    --placement-stats)
      placement_stats=$2
      shift # past argument
      shift # past value
      ;;
    --issue-to-lineage)
      issue_to_lineage=$2
      shift # past argument
      shift # past value
      ;;
    --low-memory)
      low_memory="true"
      shift # past argument
      ;;
    --extra-cols)
      extra_cols=$2
      shift # past argument
      shift # past value
      ;;
    --output)
      output=$2
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

default_cols="strain,date,country"
extract_cols="clade,usher_clade,Nextclade_pango,usher_pango_lineage,sc2rf_parents,sc2rf_regions,sc2rf_breakpoints,usher_num_best"
rename_cols="Nextstrain_clade,Nextstrain_clade_usher,pangolin_lineage,pango_lineage_usher,parents,parents_regions,breakpoints,usher_placements"
rename_cols_final="clade_nextclade,clade_usher,lineage_nextclade,lineage_usher,parents,parents_regions,breakpoints,usher_placements"

# Hack to fix commas if extra_cols is empty

if [[ $extra_cols ]]; then
  extra_cols=",${extra_cols},"
else
  extra_cols=","
fi

# Low memory, don't use usher metadata
if [[ "$low_memory" == "true" ]]; then

  csvtk merge -t -f "strain" ${nextclade} ${sc2rf} ${clades} ${placement_stats} \
    | csvtk cut -t -f "${default_cols}${extra_cols}${extract_cols}" \
    | csvtk rename -t -f "${extract_cols}" -n "${rename_cols}" \
    | csvtk cut -t -f "${default_cols}${extra_cols}${rename_cols}" \
    | csvtk rename -t -f "${rename_cols}" -n "${rename_cols_final}" \
    | csvtk replace -t -f "lineage_usher" -p "proposed([0-9]+)" -k ${issue_to_lineage} -r "{kv}" \
    > $output;

# Merge mode
else
  csvtk merge -t -f "strain" ${nextclade} ${sc2rf} ${clades} ${placement_stats} \
    | csvtk cut -t -f "${default_cols}${extra_cols}${extract_cols}" \
    | csvtk rename -t -f "${extract_cols}" -n "${rename_cols}" \
    | csvtk concat -t -u "?" - ${base_metadata} \
    | csvtk cut -t -f "${default_cols}${extra_cols}${rename_cols}" \
    | csvtk rename -t -f "${rename_cols}" -n "${rename_cols_final}" \
    | csvtk replace -t -f "lineage_usher" -p "proposed([0-9]+)" -k ${issue_to_lineage} -r "{kv}" \
    > $output;
fi
