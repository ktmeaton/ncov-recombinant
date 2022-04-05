#!/usr/bin/env python3

import pandas as pd
import click

NO_DATA_CHAR = "NA"


@click.command()
@click.option("--qc", help="QC output from nextclade.", required=True)
@click.option("--min-muts", help="Minimum number of mutations", default=2)
def main(
    qc,
    min_muts,
):
    """Detect recombinant seqences from nextclade."""

    # -----------------------------------------------------------------------------
    # Import QC Dataframe

    qc_df = pd.read_csv(qc, sep="\t", low_memory=False)
    qc_df.fillna(NO_DATA_CHAR, inplace=True)
    qc_df.rename(
        {
            "seqName": "strain",
        },
        axis="columns",
        inplace=True,
    )
    # qc_df = qc_df[0:100]

    # -----------------------------------------------------------------------------
    # Process QC

    mut_type = "privateNucMutations.labeledSubstitutions"

    strain_recomb = []

    for rec in qc_df.iterrows():

        strain = rec[1]["strain"]

        # Identify based on next clade
        clade = rec[1]["clade"]
        if clade == "recombinant":
            strain_recomb.append(strain)
            continue

        # Identify based on private mutation count

        clade_mut_count = {}

        muts = rec[1][mut_type]
        muts_split = muts.split(",")

        for mut in muts_split:
            if mut == NO_DATA_CHAR:
                continue
            mut_clades = mut.split("|")[1].split("&")
            for clade in mut_clades:
                # Update the count dict
                if clade not in clade_mut_count:
                    clade_mut_count[clade] = 0
                clade_mut_count[clade] += 1

        for clade in clade_mut_count:
            if clade_mut_count[clade] >= min_muts:
                strain_recomb.append(strain)
                break

    # -----------------------------------------------------------------------------
    # Write Recombinant Candidates

    for strain in strain_recomb:
        print(strain)


if __name__ == "__main__":
    main()
