#!/bin/bash

# -----------------------------------------------------------------------------
# Argument Parsing

while [[ $# -gt 0 ]]; do
  case $1 in
    --gisaid-dir)
      GISAID_DIR=$2
      shift # past argument
      shift # past value
      ;;
    --partition)
      PARTITION=$2
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

if [[ ! $GISAID_DIR ]]; then
  echo "Error: --gisaid-dir was not specified."
  exit 1
elif [[ ! PARTITION ]]; then
  echo "Error: --partition was not specified."
  exit 1
fi

# Convert xlsx metadata to tsv
csvtk xlsx2csv data/controls/metadata.xlsx | csvtk csv2tab > data/controls/metadata.tsv;
csvtk cut -t -f "strain" data/controls/metadata.tsv | tail -n+2 > data/controls/strains.txt;

# Extract sequences
cmd="
sbatch -p $PARTITION -J controls-sequences --wrap=\"
    source activate ncov-recombinant &&
    seqkit grep -f data/controls/strains.txt ${GISAID_DIR}/gisaid_sequences.fasta \
        > data/controls/sequences.fasta; \"
"
echo $cmd
eval $cmd
