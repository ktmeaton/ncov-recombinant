#!/bin/bash

# -----------------------------------------------------------------------------
# Argument Parsing

while [[ $# -gt 0 ]]; do

  case $1 in
    --output)
      output=$2
      shift # past argument
      shift # past value
      ;;
    --nextclade)
      nextclade=$2
      shift # past argument
      shift # past value
      ;;
    --nextclade-dataset)
      nextclade_dataset=$2
      shift # past argument
      shift # past value
      ;;
    --sc2rf)
      sc2rf=$2
      shift # past argument
      shift # past value
      ;;
    --extra-cols)
      extra_cols=$2
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# ncov-recombinant pipeline version
git_commit_hash=$(git rev-parse HEAD)
git_commit=${git_commit_hash:0:8}
git_tag=$(git tag | tail -n1)
ncov_recombinant_ver="${git_tag}:${git_commit}"

# Nextclade version
nextclade_ver=$(nextclade --version | cut -d " " -f 2)

sort_col="Nextclade_pango"
default_cols="strain,date,country"
nextclade_cols="privateNucMutations.reversionSubstitutions,privateNucMutations.unlabeledSubstitutions,privateNucMutations.labeledSubstitutions"

# Hack to fix commas if extra_cols is empty
cols="${default_cols},${nextclade_cols}"
if [[ $extra_cols ]]; then
  cols="${cols},${extra_cols}"
fi

csvtk cut -t -f "${cols},clade,Nextclade_pango" ${nextclade} \
  | csvtk rename -t -f "clade" -n "Nextclade_clade" \
  | csvtk merge -t --na "NA" -f "strain" - ${sc2rf} \
  | csvtk sort -t -k "$sort_col" \
  | csvtk mutate2 -t -n "ncov-recombinant_version" -e "\"$ncov_recombinant_ver\"" \
  | csvtk mutate2 -t -n "nextclade_version" -e "\"$nextclade_ver\"" \
  | csvtk mutate2 -t -n "nextclade_dataset" -e "\"$nextclade_dataset\"" \
  > $output
