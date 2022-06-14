#!/bin/bash

#!/bin/bash

# -----------------------------------------------------------------------------
# Argument Parsing

num_args="$#"

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      help="true"
      shift # past argument
      ;;  
    --data)
      data=$2
      shift # past argument
      shift # past value
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# -----------------------------------------------------------------------------
# Usage

if [[ $help || $num_args -eq 0 ]]; then
  usage="
  usage: bash template_build.sh [-h,--help] [--data DATA]\n\n

  \tCreate a template build for the ncov-recombinant Snakemake pipeline.\n\n

  \tRequired arguments:\n
  \t\t--data DATA               \t\t Path to the directory where sequences and metadata are stored (ex. data/custom)\n\n

  \tOptional arguments:\n
  \t\t-h, --help                \t\t Show this help message and exit.
  "
  echo -e $usage
  exit 0
fi

if [[ -z $data ]]; then
  echo "ERROR: A data directory must be specified with --data <DATA>"
  exit 1
fi

PROFILES_DIR="profiles"
NUM_REQUIRED_COLS=3
REQUIRED_COLS="strain|date|country"
FIRST_COL="strain"

profile=$(basename $data)


# -----------------------------------------------------------------------------
# Validate Inputs

# Metadata Check
echo -e "$(date "+%Y-%m-%d %T")\tSearching for metadata ($data/metadata.tsv)"
check=$(ls $data/metadata.tsv 2> /dev/null)
if [[ $check ]]; then
    echo -e "\t\t\tSUCCESS: metadata found."
else
    echo -e "\t\t\tFAIL: Metadata not found!"
    exit 1
fi

# Metadata Validate
echo -e "$(date "+%Y-%m-%d %T")\tChecking for $NUM_REQUIRED_COLS required metadata columns ($REQUIRED_COLS)"
num_required_cols=$(head -n 1 $data/metadata.tsv | tr "\t" "\n" | grep -w -E "$REQUIRED_COLS" | wc -l)
first_col=$(head -n 1 $data/metadata.tsv | cut -f 1)


if [[ $num_required_cols -eq $NUM_REQUIRED_COLS ]]; then
    echo -e "$(date "+%Y-%m-%d %T")\tSUCCESS: $NUM_REQUIRED_COLS columns found."
elif [[ "$first_col" != "$FIRST_COL" ]]; then
    echo -e "\t\t\tFAIL: First column ($first_col) is not '$FIRST_COL'."   
elif [[ ! $num_required_cols -eq $NUM_REQUIRED_COLS ]]; then
    echo -e "\t\t\tFAIL: $NUM_REQUIRED_COLS columns not found!"
    exit 1    
fi

# Sequences Check
echo -e "$(date "+%Y-%m-%d %T")\tSearching for sequences ($data/sequences.fasta)"
check=$(ls $data/sequences.fasta 2> /dev/null)
if [[ $check ]]; then
    echo -e "\t\t\tSUCCESS: Sequences found."
else
    echo -e "\t\t\tFAIL: Sequences not found!"
    exit 1
fi

# Match seqs and metadata
echo -e "$(date "+%Y-%m-%d %T")\tChecking that the strain column matches the sequence names"
seq_names=$(grep ">" $data/sequences.fasta | sed 's/>//g' | sort)
strain_names=$(cut -f 1 $data/metadata.tsv | tail -n+2 | sort)

if [[ "$seq_names" == "$strain_names" ]]; then
    echo -e "\t\t\tFAIL: Strain column does not match the sequence names!"
    echo -e "\t\t\tSequence names:"
    echo $seq_names | sed 's/ /\n/g' | sed 's/^/\t\t\t\t/g'
    echo -e "\t\t\tStrain names:"
    echo $strain_names | sed 's/ /\n/g' | sed 's/^/\t\t\t\t/g'    
    exit 1
fi
echo $seq_names
echo $strain_names
# Create profiles directory
#echo "mkdir -p $PROFILES_DIR/$profile"
