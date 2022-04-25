#!/bin/bash

# -----------------------------------------------------------------------------
# Argument Parsing

while [[ $# -gt 0 ]]; do
  case $1 in
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
    --usher)
      usher=$2
      shift # past argument
      shift # past value
      ;;
    --subtrees)
      subtrees=$2
      shift # past argument
      shift # past value
      ;;
    --cols)
      cols=$2
      shift # past argument
      shift # past value
      ;;
    --usher-dataset)
      usher_dataset=$2
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

git_commit_hash=$(git rev-parse HEAD)
git_commit=${git_commit_hash:0:8}
git_tag=$(git tag | tail -n1)
#git_branch=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')

nextclade_ver=$(nextclade --version)
usher_ver=$(usher --version | cut -d " " -f 2 | sed 's/(\|)\|v//g')


ncov_recombinant_ver="${git_tag}:${git_commit}"

cd sc2rf
git_branch=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p' | sed 's/)//g' | rev | cut -d " " -f 1 | rev)
git_commit_hash=$(git rev-parse HEAD)
git_commit=${git_commit_hash:0:8}
sc2rf_ver="${git_branch}:${git_commit}"
cd ..

usher_dataset_name=$(basename $(dirname $usher_dataset))
usher_dataset_ver=$(cut -d " " -f 8 $usher_dataset | sed 's/(\|)\|;//g')
usher_dataset_ver="${usher_dataset_name}:${usher_dataset_ver}"

sort_col="usher_subtree"

csvtk cut -t -f "strain,${cols},clade,Nextclade_pango" ${nextclade} \
  | csvtk rename -t -f "clade" -n "Nextclade_clade" \
  | csvtk merge -t --na "NA" -f "strain" - ${sc2rf} \
  | csvtk merge -t -k --na "NA" -f "strain" - ${usher} \
  | csvtk merge -t -k --na "NA" -f "strain" - ${subtrees} \
  | csvtk sort -t -k "$sort_col" \
  | csvtk mutate2 -t -n "ncov-recombinant_version" -e "\"$ncov_recombinant_ver\"" \
  | csvtk mutate2 -t -n "nextclade_version" -e "\"$nextclade_ver\"" \
  | csvtk mutate2 -t -n "sc2rf_version" -e "\"$sc2rf_ver\"" \
  | csvtk mutate2 -t -n "usher_version" -e "\"$usher_ver\"" \
  | csvtk mutate2 -t -n "nextclade_dataset" -e "\"$nextclade_dataset\"" \
  | csvtk mutate2 -t -n "usher_dataset" -e "\"$usher_dataset_ver\""
