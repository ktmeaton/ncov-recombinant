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

git_commit_hash=$(git rev-parse HEAD)
git_commit_hash=${git_commit_hash:0:8}
git_branch=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')

ncov_recombinant_ver="${git_branch}@${git_commit_hash}"

csvtk cut -t -f "strain,clade,Nextclade_pango" ${nextclade} \
       | csvtk rename -t -f "clade" -n "Nextclade_clade" \
      | csvtk merge -t --na "NA" -f "strain" ${sc2rf} - \
      | csvtk rename -t -f "clades" -n "sc2rf_clades" \
      | csvtk merge -t -k --na "NA" -f "strain" - ${usher} \
      | csvtk merge -t -k --na "NA" -f "strain" - ${subtrees} \
      | csvtk sort -t -k "usher_subtree" \
      | csvtk mutate2 -t -n "ncov-recombinant" -e "\"$ncov_recombinant_ver\""
