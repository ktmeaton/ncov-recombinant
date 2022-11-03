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
    --controls)
      controls="true"
      shift # past argument
      ;;
    --profile-dir)
      profile_dir=$2
      shift # past argument
      shift # past value
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
  usage: bash template_build.sh [-h,--help] [--data DATA] [--hpc] [--profile-dir]\n\n

  \tCreate a template build for the ncov-recombinant Snakemake pipeline.\n\n

  \tRequired arguments:\n
  \t\t--data DATA               \t\t Path to the directory where sequences and metadata are stored (ex. data/custom)\n\n

  \tOptional arguments:\n
  \t\t--hpc                     \t\t\t Configure build for HPC execution using SLURM.\n
  \t\t--profile-dir             \t\t\t Directory to create the profile in (default: my_profiles)\n
  \t\t--controls                \t\t\t Add the controls build\n
  \t\t-h, --help                \t\t Show this help message and exit.
  "
  echo -e $usage
  exit 0
fi

if [[ -z $data ]]; then
  echo "ERROR: A data directory must be specified with --data <DATA>"
  exit 1
fi


NUM_REQUIRED_COLS=3
REQUIRED_COLS="strain|date|country"
FIRST_COL="strain"
DEFAULT_PARAMS="defaults/parameters.yaml"
DEFAULT_BUILDS="defaults/builds.yaml"
EXCLUDE_CONTROLS_BUILDS="defaults/builds-exclude-controls.yaml"
DEFAULT_CONFIG="profiles/controls/config.yaml"
DEFAULT_CONFIG_HPC="profiles/controls-hpc/config.yaml"

profile_dir=${profile_dir:-my_profiles}
profile=$(basename $data)

if [[ $controls ]]; then
  profile="${profile}-controls"
fi

if [[ $hpc ]]; then
  profile="${profile}-hpc"
fi

mkdir -p $profile_dir

# -----------------------------------------------------------------------------
# Validate Inputs

# Metadata Check
echo -e "$(date "+%Y-%m-%d %T")\tSearching for metadata ($data/metadata.tsv)"
check=$(ls $data/metadata.tsv 2> /dev/null)
if [[ $check ]]; then
    echo -e "$(date "+%Y-%m-%d %T")\tSUCCESS: metadata found"
else
    echo -e "$(date "+%Y-%m-%d %T")\tFAIL: Metadata not found!"
    exit 1
fi

# Metadata Validate
echo -e "$(date "+%Y-%m-%d %T")\tChecking for $NUM_REQUIRED_COLS required metadata columns ($(echo $REQUIRED_COLS | tr "|" " " ))"
num_required_cols=$(head -n 1 $data/metadata.tsv | tr "\t" "\n" | grep -w -E "$REQUIRED_COLS" | wc -l)
first_col=$(head -n 1 $data/metadata.tsv | cut -f 1)


if [[ $num_required_cols -eq $NUM_REQUIRED_COLS ]]; then
    echo -e "$(date "+%Y-%m-%d %T")\tSUCCESS: $NUM_REQUIRED_COLS columns found."
elif [[ "$first_col" != "$FIRST_COL" ]]; then
    echo -e "$(date "+%Y-%m-%d %T")\tFAIL: First column ($first_col) is not '$FIRST_COL'"
elif [[ ! $num_required_cols -eq $NUM_REQUIRED_COLS ]]; then
    echo -e "$(date "+%Y-%m-%d %T")\tFAIL: $NUM_REQUIRED_COLS columns not found!"
    exit 1
fi

# Sequences Check
echo -e "$(date "+%Y-%m-%d %T")\tSearching for sequences ($data/sequences.fasta)"
check=$(ls $data/sequences.fasta 2> /dev/null)
if [[ $check ]]; then
    echo -e "$(date "+%Y-%m-%d %T")\tSUCCESS: Sequences found"
else
    echo -e "$(date "+%Y-%m-%d %T")\tFAIL: Sequences not found!"
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
    echo -e "$(date "+%Y-%m-%d %T")\tSUCCESS: Strain column matches sequence names"
else
    echo -e "$(date "+%Y-%m-%d %T")\tFAIL: Strain column does not match the sequence names!"
    echo -e "$(date "+%Y-%m-%d %T")\tStrains missing from $data/sequences.fasta:"
    echo $seq_missing | tr " " "\n" | sed 's/^/\t\t\t\t/g'
    echo -e "$(date "+%Y-%m-%d %T")\tStrains missing from $data/metadata.tsv:"
    echo $meta_missing | tr " " "\n" | sed 's/^/\t\t\t\t/g'
    exit 1
fi


# -----------------------------------------------------------------------------
# Profile

# Create profile directory
echo -e "$(date "+%Y-%m-%d %T")\tCreating new profile directory ($profile_dir/$profile)"
mkdir -p $profile_dir/$profile

# -----------------------------------------------------------------------------
# Build

# Create builds.yaml
echo -e "$(date "+%Y-%m-%d %T")\tCreating build file ($profile_dir/$profile/builds.yaml)"

# Add controls build, unless excluded
if [[ $controls == "true" ]]; then
  echo -e "$(date "+%Y-%m-%d %T")\tAdding \`controls\` as a build"
  cat $DEFAULT_BUILDS > $profile_dir/$profile/builds.yaml
else
  cat $EXCLUDE_CONTROLS_BUILDS > $profile_dir/$profile/builds.yaml
fi

#Add custom build
echo -e "$(date "+%Y-%m-%d %T")\tAdding \`$(basename $data)\` as a build"

echo -e "\n
  # ---------------------------------------------------------------------------
  # $(basename $data) build\n
  - name: $(basename $data)
    metadata: $data/metadata.tsv
    sequences: $data/sequences.fasta
" >> $profile_dir/$profile/builds.yaml

# -----------------------------------------------------------------------------
# Config

# Create config.yaml
echo -e "$(date "+%Y-%m-%d %T")\tCreating system configuration ($profile_dir/$profile/config.yaml)"
if [[ $hpc ]]; then
    echo -e "$(date "+%Y-%m-%d %T")\tAdding default HPC system resources"
    cp -f $DEFAULT_CONFIG_HPC $profile_dir/$profile/config.yaml
else
    echo -e "$(date "+%Y-%m-%d %T")\tAdding default system resources"
    cp -f $DEFAULT_CONFIG $profile_dir/$profile/config.yaml
fi
sed -i "s|profiles/controls/builds.yaml|$profile_dir/$profile/builds.yaml|g" $profile_dir/$profile/config.yaml


echo -e "$(date "+%Y-%m-%d %T")\tDone!"

echo -e "$(date "+%Y-%m-%d %T")\tSystem resources can be further configured in:"
echo -e "
\t\t\t$profile_dir/$profile/config.yaml
"

echo -e "$(date "+%Y-%m-%d %T")\tBuilds can be configured in:"
echo -e "
\t\t\t$profile_dir/$profile/builds.yaml
"

echo -e "$(date "+%Y-%m-%d %T")\tThe $profile profile is ready to be run with:"
if [[ $hpc ]]; then
  echo -e "
  \t\t\tscripts/slurm.sh --profile $profile_dir/$profile
  "
else
  echo -e "
  \t\t\tsnakemake --profile $profile_dir/$profile
  "
fi
