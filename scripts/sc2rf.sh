#!/bin/bash

# -----------------------------------------------------------------------------
# Argument Parsing

sc2rf_args=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --alignment)
      alignment=$2
      shift # past argument
      shift # past value
      ;;
    --primers)
      primers=$2
      shift # past argument
      shift # past value
      ;;
    --primers-name)
      primers_name=$2
      shift # past argument
      shift # past value
      ;;
    --output-ansi)
      output_ansi=$2
      shift # past argument
      shift # past value
      ;;
    --output-csv)
      output_csv=$2
      shift # past argument
      shift # past value
      ;;
    --log)
      log=$2
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      arg=$1
      value=$2
      sc2rf_args+=("$arg")
      shift # past argument
      if [[ ${value:0:1} != "-" ]]; then
        sc2rf_args+=("$value")
        shift # past value
      fi
      ;;
    *)
      # This is a risky way to parse the clades for sc2rf
      value=$1
      sc2rf_args+=("$value")
      shift # past value
      ;;
  esac
done

# Prep the Output Directory
outdir=$(dirname $output_csv)
mkdir -p $outdir

# Location of sc2rf executable
sc2rf="sc2rf/sc2rf.py"

# Add optional params to sc2rf_args
primers_name=${primers_name:-primers}
sc2rf_args+=("--csvfile $output_csv")

# Add primers
if [[ "${primers}" ]]; then
  cp $primers sc2rf/${primers_name}.bed
  sc2rf_args+=("--primers ${primers_name}.bed")
fi

# rebuild examples
#log_rebuild=${log%.*}_rebuild
#python3 sc2rf.py --rebuild-examples 1> ${log_rebuild}.log 2> ${log_rebuild}.err

echo "python3 $sc2rf ${alignment} ${sc2rf_args[@]}" > ${output_ansi}
python3 $sc2rf ${alignment} ${sc2rf_args[@]} 1>> ${output_ansi} 2> ${log};

# Clean up primers
if [[ "${primers}" ]]; then
  rm -f sc2rf/${primers_name}.bed
fi
