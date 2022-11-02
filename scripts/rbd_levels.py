#!/usr/bin/env python3
import click
import pandas as pd
import os
import yaml
from functions import create_logger

NO_DATA_CHAR = "NA"


@click.command()
@click.option(
    "--rbd-definition", help="Key RBD mutation definitions (yaml).", required=True
)
@click.option("--nextclade", help="Nextclade qc table (tsv).", required=True)
@click.option("--output", help="Ouptut table of RBD level (tsv).", required=True)
@click.option("--log", help="Output log file.", required=False)
def main(
    rbd_definition,
    nextclade,
    output,
    log,
):
    """Calculate the number of key RBD mutations."""

    # create logger
    logger = create_logger(logfile=log)

    # Create output directory
    outdir = os.path.dirname(output)
    if not os.path.exists(outdir) and outdir != "." and outdir != "":
        os.makedirs(outdir)

    # -------------------------------------------------------------------------
    # RBD Mutation Definitions

    # Import file
    logger.info("Parsing RBD mutation definitions: {}".format(rbd_definition))
    with open(rbd_definition) as infile:
        rbd_dict = yaml.safe_load(infile)

    # Parse into dataframe
    rbd_data = {"gene": [], "coord": [], "ref": [], "alt": []}
    for mut in rbd_dict["rbd_mutations"]:
        rbd_data["gene"].append("S")
        rbd_data["coord"].append(int(mut[1]))
        rbd_data["ref"].append(mut[0])
        rbd_data["alt"].append(mut[2])

    rbd_df = pd.DataFrame(rbd_data)

    # -------------------------------------------------------------------------
    # Nextclade QC

    logger.info("Parsing nextclade QC: {}".format(nextclade))
    nextclade_df = pd.read_csv(nextclade, sep="\t")
    nextclade_df.fillna("NA", inplace=True)

    # -------------------------------------------------------------------------
    # RBD Calculations from Amino Acid Substitutions

    logger.info("Calculating RBD levels.")
    # Initialize the columns that will be in the output table
    output_data = {
        "strain": [],
        "rbd_level": [],
        "rbd_substitutions": [],
        "immune_escape": [],
        "ace2_binding": [],
    }

    # Initialize at 0
    # nextclade_df.at[nextclade_df.index, "rbd_level"] = [0] * len(nextclade_df)
    nextclade_df["rbd_level"] = [0] * len(nextclade_df)

    # Assign RBD level to each sample
    for rec in nextclade_df.iterrows():
        strain = rec[1]["seqName"]
        aa_subs = rec[1]["aaSubstitutions"].split(",")

        rbd_level = 0
        rbd_subs = []

        for s in aa_subs:
            gene = s.split(":")[0]
            # RBD Mutations only involve spike
            if gene != "S":
                continue
            coord = int(s.split(":")[1][1:-1])
            alt = s.split(":")[1][-1]

            # Check if the position is a RBD mutation
            if coord in list(rbd_df["coord"]):
                rbd_coord_alts = list(rbd_df[rbd_df["coord"] == coord]["alt"])[0]
                if alt in rbd_coord_alts:
                    rbd_level += 1
                    rbd_subs.append(s)

        immune_escape = NO_DATA_CHAR
        ace2_binding = NO_DATA_CHAR
        if "immune_escape" in nextclade_df.columns:
            immune_escape = rec[1]["immune_escape"]
            ace2_binding = rec[1]["ace2_binding"]

        output_data["strain"].append(strain)
        output_data["rbd_level"].append(rbd_level)
        output_data["rbd_substitutions"].append(",".join(rbd_subs))
        output_data["immune_escape"].append(immune_escape)
        output_data["ace2_binding"].append(ace2_binding)

    output_df = pd.DataFrame(output_data)

    # -------------------------------------------------------------------------
    # Export

    logger.info("Exporting table: {}".format(output))
    output_df.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    main()
