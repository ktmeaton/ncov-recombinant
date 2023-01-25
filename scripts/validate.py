#!/usr/bin/env python3
import click
import pandas as pd
import os

NO_DATA_CHAR = "NA"
VALIDATE_COLS = ["status", "lineage", "parents_clade", "breakpoints"]


@click.command()
@click.option("--expected", help="Expected linelist (TSV)", required=True)
@click.option("--observed", help="Observed linelist (TSV)", required=True)
@click.option("--outdir", help="Output directory", required=True)
def main(
    expected,
    observed,
    outdir,
):
    """Validate output"""

    # Check for output directory
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Import Dataframes
    expected_df = pd.read_csv(expected, sep="\t")
    observed_df = pd.read_csv(observed, sep="\t")

    expected_df.fillna(NO_DATA_CHAR, inplace=True)
    observed_df.fillna(NO_DATA_CHAR, inplace=True)

    output_data = {
        "strain": [],
        "status": [],
        "fail_cols": [],
        "expected": [],
        "observed": [],
    }

    # Validate observed values
    for rec in observed_df.iterrows():
        strain = rec[1]["strain"]
        fail_cols = []
        expected_vals = []
        observed_vals = []

        # Check if this in the validation table
        if strain not in expected_df["strain"].values:
            status = "No Expected Values"
        else:

            # Check if all observed values match the expected values
            match = True

            for col in VALIDATE_COLS:
                exp_val = expected_df[expected_df["strain"] == strain][col].values[0]
                obs_val = observed_df[observed_df["strain"] == strain][col].values[0]

                if exp_val != obs_val:
                    match = False
                    fail_cols.append(col)
                    expected_vals.append(exp_val)
                    observed_vals.append(obs_val)

            # Check if any columns failed matching
            if match:
                status = "Pass"
            else:
                status = "Fail"

        output_data["strain"].append(strain)
        output_data["status"].append(status)
        output_data["fail_cols"].append(";".join(fail_cols))
        output_data["expected"].append(";".join(expected_vals))
        output_data["observed"].append(";".join(observed_vals))

    # Table of validation
    output_df = pd.DataFrame(output_data)
    outpath = os.path.join(outdir, "validation.tsv")
    output_df.to_csv(outpath, sep="\t", index=False)

    # Overall build validation status
    build_status = "Pass"
    # Option 1. Fail if one sample failed
    if "Fail" in output_data["status"]:
        build_status = "Fail"
    # Option 2. Pass if values are all "Pass" or "No Expected Values"
    elif "Pass" in output_data["status"]:
        build_status = "Pass"
    # Option 2. No Expected Values
    elif len(output_df) == 0:
        build_status = "No Expected Values"

    outpath = os.path.join(outdir, "status.txt")
    with open(outpath, "w") as outfile:
        outfile.write(build_status + "\n")


if __name__ == "__main__":
    main()
