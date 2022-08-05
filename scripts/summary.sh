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

# sc2rf version
cd sc2rf
git_branch=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p' | sed 's/)//g' | rev | cut -d " " -f 1 | rev)
git_commit_hash=$(git rev-parse HEAD)
git_commit=${git_commit_hash:0:8}
sc2rf_ver="${git_branch}:${git_commit}"
sc2rf_muts_date=$(stat virus_properties.json | grep "Modify" | cut -d " " -f 2)
sc2rf_muts_ver="virus_properties:${sc2rf_muts_date}"
cd ..


sort_col="Nextclade_pango"
default_cols="strain,date,country"

# Hack to fix commas if extra_cols is empty
if [[ $extra_cols ]]; then
  extra_cols=",${extra_cols},"
else
  extra_cols=","
fi

csvtk cut -t -f "${default_cols}${extra_cols}clade,Nextclade_pango" ${nextclade} \
  | csvtk rename -t -f "clade" -n "Nextclade_clade" \
  | csvtk merge -t --na "NA" -f "strain" - ${sc2rf} \
  | csvtk sort -t -k "$sort_col" \
  | csvtk mutate2 -t -n "ncov-recombinant_version" -e "\"$ncov_recombinant_ver\"" \
  | csvtk mutate2 -t -n "nextclade_version" -e "\"$nextclade_ver\"" \
  | csvtk mutate2 -t -n "sc2rf_version" -e "\"$sc2rf_ver\"" \
  | csvtk mutate2 -t -n "sc2rf_mutations_version" -e "\"${sc2rf_muts_ver}\"" \
  | csvtk mutate2 -t -n "nextclade_dataset" -e "\"$nextclade_dataset\"" \
  > $output
