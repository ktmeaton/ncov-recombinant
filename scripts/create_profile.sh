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
    --hpc)
      hpc="true"
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
  usage: bash template_build.sh [-h,--help] [--data DATA] [--hpc] \n\n

  \tCreate a template build for the ncov-recombinant Snakemake pipeline.\n\n

  \tRequired arguments:\n
  \t\t--data DATA               \t\t Path to the directory where sequences and metadata are stored (ex. data/custom)\n\n

  \tOptional arguments:\n
  \t\t--hpc                     \t\t\t Configure build for HPC execution using SLURM.\n
  \t\t-h, --help                \t\t Show this help message and exit.
  "
  echo -e $usage
  exit 0
fi

if [[ -z $data ]]; then
  echo "ERROR: A data directory must be specified with --data <DATA>"
  exit 1
fi

PROFILES_DIR="my_profiles"
NUM_REQUIRED_COLS=3
REQUIRED_COLS="strain|date|country"
FIRST_COL="strain"
DEFAULT_INPUTS="defaults/inputs.yaml"
DEFAULT_PARAMS="defaults/parameters.yaml"
DEFAULT_BUILDS="defaults/builds.yaml"
DEFAULT_CONFIG="profiles/controls/config.yaml"
DEFAULT_CONFIG_HPC="profiles/controls-hpc/config.yaml"
DEFAULT_BASE_INPUT="public-latest"

if [[ -z $hpc ]]; then
  profile="$(basename $data)"
else
  profile="$(basename $data)-hpc"
fi


mkdir -p $PROFILES_DIR


# -----------------------------------------------------------------------------
# Validate Inputs

# Metadata Check
echo -e "$(date "+%Y-%m-%d %T")\tSearching for metadata ($data/metadata.tsv)"
check=$(ls $data/metadata.tsv 2> /dev/null)
if [[ $check ]]; then
    echo -e "\t\t\tSUCCESS: metadata found"
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
    echo -e "\t\t\tFAIL: First column ($first_col) is not '$FIRST_COL'"
elif [[ ! $num_required_cols -eq $NUM_REQUIRED_COLS ]]; then
    echo -e "\t\t\tFAIL: $NUM_REQUIRED_COLS columns not found!"
    exit 1
fi

# Sequences Check
echo -e "$(date "+%Y-%m-%d %T")\tSearching for sequences ($data/sequences.fasta)"
check=$(ls $data/sequences.fasta 2> /dev/null)
if [[ $check ]]; then
    echo -e "\t\t\tSUCCESS: Sequences found"
else
    echo -e "\t\t\tFAIL: Sequences not found!"
    exit 1
fi

# Match seqs and metadata
echo -e "$(date "+%Y-%m-%d %T")\tChecking that the metadata strains match the sequence names"
grep ">" $data/sequences.fasta | sed 's/>//g' > tmp.seq_names
cut -f 1 $data/metadata.tsv | tail -n+2 > tmp.meta_names
diff_names=$(cat tmp.seq_names tmp.meta_names | sort | uniq -u)
# Reminder, var name is delib differently from input
seq_missing=$(echo $diff_names | tr " " "\n" | grep -f - tmp.meta_names)
meta_missing=$(echo $diff_names | tr " " "\n" | grep -f - tmp.seq_names)

# Cleanup tmp files
rm -f tmp.seq_names
rm -f tmp.meta_names

if [[ -z "$diff_names" ]]; then
    echo -e "\t\t\tSUCCESS: Strain column matches sequence names"
else
    echo -e "\t\t\tFAIL: Strain column does not match the sequence names!"
    echo -e "\t\t\tStrains missing from $data/sequences.fasta:"
    echo $seq_missing | tr " " "\n" | sed 's/^/\t\t\t\t/g'
    echo -e "\t\t\tStrains missing from $data/metadata.tsv:"
    echo $meta_missing | tr " " "\n" | sed 's/^/\t\t\t\t/g'
    exit 1
fi


# Create profiles directory
echo -e "$(date "+%Y-%m-%d %T")\tCreating new profile directory ($PROFILES_DIR/$profile)"
mkdir -p $PROFILES_DIR/$profile

echo -e "$(date "+%Y-%m-%d %T")\tCreating build file ($PROFILES_DIR/$profile/builds.yaml)"
echo -e "$(date "+%Y-%m-%d %T")\tAdding default input datasets from $DEFAULT_INPUTS"
cat $DEFAULT_INPUTS > $PROFILES_DIR/$profile/builds.yaml

echo -e "$(date "+%Y-%m-%d %T")\tAdding $profile input dataset ($data)"
echo -e "\n
  # custom local build
  - name: $(basename $data)
    type:
      - local
    metadata: $data/metadata.tsv
    sequences: $data/sequences.fasta
" >> $PROFILES_DIR/$profile/builds.yaml

echo -e "$(date "+%Y-%m-%d %T")\tCreating system configuration ($PROFILES_DIR/$profile/config.yaml)"
if [[ -z $hpc ]]; then
    echo -e "$(date "+%Y-%m-%d %T")\tAdding default system resources"
    cp -f $DEFAULT_CONFIG $PROFILES_DIR/$profile/config.yaml
else
    echo -e "$(date "+%Y-%m-%d %T")\tAdding default HPC system resources"
    cp -f $DEFAULT_CONFIG_HPC $PROFILES_DIR/$profile/config.yaml
fi
sed -i "s|profiles/controls/builds.yaml|$PROFILES_DIR/$profile/builds.yaml|g" $PROFILES_DIR/$profile/config.yaml

echo -e "$(date "+%Y-%m-%d %T")\tCreating build ($profile)"
cat $DEFAULT_BUILDS >> $PROFILES_DIR/$profile/builds.yaml
echo -e "
builds:
  - name: $(basename $data)
    base_input: $DEFAULT_BASE_INPUT
" >> $PROFILES_DIR/$profile/builds.yaml

echo -e "$(date "+%Y-%m-%d %T")\tDone! The $profile profile is ready to be run with:"
echo -e "
\t\t\tsnakemake --profile $PROFILES_DIR/$profile
"
