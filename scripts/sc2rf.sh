#!/bin/bash

# -----------------------------------------------------------------------------
# Argument Parsing

sc2rf_args=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --aligned)
      aligned=$2
      shift # past argument
      shift # past value
      ;;
    --prefix)
      prefix=$2
      shift # past argument
      shift # past value
      ;;
    --outdir)
      outdir=$2
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
  esac
done

# Correct relative paths
aligned="../${aligned}"
log="../${log}"
outdir="../${outdir}"

# Add a csvfile
csvfile="${outdir}/${prefix}.csv"
sc2rf_args+=("--csvfile $csvfile")

cd sc2rf;
echo "python3 sc2rf.py ${aligned} ${sc2rf_args[@]}" > ${outdir}/${prefix}.ansi.txt;
python3 sc2rf.py ${aligned} ${sc2rf_args[@]} 1>> ${outdir}/${prefix}.ansi.txt 2> ${log};

# Check if any recombinants were detected"
if [[ -s ${outdir}/${prefix}.csv ]]; then

  # rename tabular columns
  # + placeholder until breakpoints/intermissions regions are reported
  csvtk rename -f "sample" -n "strain" ${outdir}/${prefix}.csv \
    | csvtk rename -f "examples" -n "sc2rf_clades" \
    | csvtk rename -f "regions" -n "sc2rf_clades_regions" \
    | csvtk rename -f "intermissions" -n "sc2rf_intermissions" \
    | csvtk rename -f "breakpoints" -n "sc2rf_breakpoints" \
    | csvtk mutate2 -n "sc2rf_breakpoints_regions" -e '""' \
    | csvtk mutate2 -n "sc2rf_intermissions_regions" -e '""' \
    | csvtk csv2tab \
    > ${outdir}/${prefix}.tsv

# If not, touch an empty tabular file
else
  touch ${outdir}/${prefix}.tsv
fi
