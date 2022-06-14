#!/bin/bash

# -----------------------------------------------------------------------------
# Argument Parsing

num_args="$#"

while [[ $# -gt 0 ]]; do
  case $1 in
    --profile)
      profile=$2
      shift # past argument
      shift # past value
      ;;
    --conda-env)
      conda_env=$2
      shift # past argument
      shift # past value
      ;;
    --target)
      target=$2
      shift # past argument
      shift # past value
      ;;
    --partition)
      partition=$2
      shift # past argument
      shift # past value
      ;;
    --cpus)
      cpus=$2
      shift # past argument
      shift # past value
      ;;
    --mem)
      mem=$2
      shift # past argument
      shift # past value
      ;;
    -h|--help)
      help="true"
      shift # past argument
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
  usage: bash slurm.sh [-h] [--profile PROFILE] [--conda-env CONDA_ENV] [--target TARGET] [--partition PARTITION] [--cpus CPUS] [--mem MEM]\n\n

  \tDispatch a Snakemake pipeline using SLURM.\n\n

  \tRequired arguments:\n
  \t\t--profile PROFILE     \t\t   Snakemake profile to execute (ex. profiles/tutorial-hpc)\n\n

  \tOptional arguments:\n
  \t\t--partition PARTITION     \t\t  Partition to submit jobs to with SLURM.\n
  \t\t--conda-env CONDA_ENV     \t\t Conda environment to use. (default: ncov-recombinant)\n
  \t\t--target TARGET           \t\t Snakemake target(s) to execute (default: all)\n
  \t\t--cpus CPUS               \t\t\t CPUS to use for the  main pipeline. (default: 1)\n
  \t\t--mem MEM                 \t\t\t Memory to use for the  ain pipeline. (default: 4GB)\n
  \t\t-h, --help                \t\t\t Show this help message and exit.
  "
  echo -e $usage
  exit 0
fi

if [[ -z $profile ]]; then
  echo "ERROR: A profile must be specified with --profile <PROFILE>"
  exit 1
fi

# Default arguments
conda_env="${conda_env:-ncov-recombinant}"
target="${target:-all}"
cpus="${cpus:-1}"
mem="${mem:-4GB}"

today=$(date +"%Y-%m-%d")
log_dir="logs/ncov-recombinant"

if [[ $partition ]]; then
  partition="--partition $partition"
fi

# -----------------------------------------------------------------------------
# Run the Workflow

mkdir -p $log_dir

cmd="
sbatch
  --parsable
  ${partition}
  -c ${cpus}
  --mem=${mem}
  -J ${conda_env}
  -o ${log_dir}/%x_${today}_%j.log
  --wrap=\"source activate $conda_env && snakemake --profile $profile $target\"
"

echo $cmd
eval $cmd
