#!/bin/bash

# -----------------------------------------------------------------------------
# Argument Parsing

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      dry_run="-n"
      shift # past argument
      ;;
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
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

dry_run="${dry_run:-}"
profile="${profile:-profiles/hpc}"
conda_env="${conda:-ncov-recombinant}"
target="${target:-all}"
partition="${partition:-MyPartition}"
cpus="${cpus:-1}"
mem="${mem:-4GB}"

today=$(date +"%Y-%m-%d")
log_dir="logs/slurm"

# -----------------------------------------------------------------------------
# Run the Workflow

mkdir -p $log_dir

cmd="
sbatch
  --parsable
  -p ${partition}
  -c ${cpus}
  --mem=${mem}
  -J ${conda_env}
  -o ${log_dir}/%x_${today}_%j.log
  --wrap=\"source activate $conda_env && snakemake --profile $profile $dry_run $target\"
"

echo $cmd
eval $cmd
