#!/usr/bin/env python3

import pandas as pd
import click
import os

NO_DATA_CHAR = "NA"


@click.command()
@click.option("--tsv", help="TSV output from sc2rf.", required=True)
@click.option("--min-len", help="Minimum region length.", required=True, default=10)
@click.option(
    "--max-parents", help="Maximum number of parents.", required=True, default=10
)
@click.option("--outdir", help="Output directory", required=True)
@click.option("--aligned", help="Alignment", required=True)
@click.option("--custom-ref", help="Reference strain name", required=True)
@click.option("--exclude-clades", help="Clades to exclude (csv)", required=True)
def main(
    tsv,
    min_len,
    outdir,
    aligned,
    custom_ref,
    max_parents,
    exclude_clades,
):
    """Detect recombinant seqences from sc2rf."""

    # -----------------------------------------------------------------------------
    # Import Dataframe
    df = pd.read_csv(tsv, sep="\t", index_col=0)
    df.fillna("", inplace=True)
    df["sc2rf_clades_filter"] = [NO_DATA_CHAR] * len(df)
    df["sc2rf_clades_regions_filter"] = [NO_DATA_CHAR] * len(df)
    df["sc2rf_breakpoints_regions_filter"] = [NO_DATA_CHAR] * len(df)

    exclude_clades = exclude_clades.split(",")

    drop_strains = {}

    for rec in df.iterrows():
        regions_str = rec[1]["sc2rf_clades_regions"]
        regions_split = regions_str.split(",")

        # Keys are start coord
        regions_filter = {}
        breakpoints_filter = []

        prev_clade = None
        prev_start_coord = None
        prev_end_coord = None

        for region in regions_split:
            coords = region.split("|")[0]
            clade = region.split("|")[1]
            start_coord = int(coords.split(":")[0])
            end_coord = int(coords.split(":")[1])
            region_len = (end_coord - start_coord) + 1

            if region_len >= min_len:

                # Is this a continuation of the previous region?
                if prev_clade and clade == prev_clade:
                    regions_filter[prev_start_coord]["end"] = end_coord
                else:
                    regions_filter[start_coord] = {"clade": clade, "end": end_coord}

                    # add breakpoint
                    if prev_clade:
                        breakpoint_start = prev_end_coord + 1
                        breakpoint_end = start_coord - 1
                        breakpoint = "{}:{}".format(breakpoint_start, breakpoint_end)
                        breakpoints_filter.append(breakpoint)

                    # store prev record
                    prev_clade = clade
                    prev_start_coord = start_coord
                    prev_end_coord = end_coord

        # Check if all the regions were collapsed
        if len(regions_filter) < 2:
            drop_strains[rec[0]] = "all regions collapsed"

        # check if the number of breakpoints changed
        # the filtered breakpoints should only ever be equal or less
        num_breakpoints = df["sc2rf_breakpoints"][rec[0]]
        num_breakpoints_filter = len(breakpoints_filter)

        if num_breakpoints_filter > num_breakpoints:
            drop_strains[rec[0]] = "{} filtered breakpoints > {}".format(
                num_breakpoints_filter, num_breakpoints
            )

        # Identify the new filtered clades
        clades_filter = [regions_filter[s]["clade"] for s in regions_filter]
        num_parents = len(set(clades_filter))
        if num_parents > max_parents:
            drop_strains[rec[0]] = "{} parents > {}".format(num_parents, max_parents)

        # Check if any clades are in exclude clades

        x_clade_found = False
        for clade in clades_filter:
            for x_clade in exclude_clades:
                if x_clade in clade:
                    drop_strains[rec[0]] = "{} is in exclude_clades".format(clade)
                    x_clade_found = True
                    break

            if x_clade_found:
                break

        # Extract the lengths of each region
        regions_length = [str(regions_filter[s]["end"] - s) for s in regions_filter]

        # Construct the new filtered regions
        regions_filter = [
            "{}:{}|{}".format(s, regions_filter[s]["end"], regions_filter[s]["clade"])
            for s in regions_filter
        ]

        df.at[rec[0], "sc2rf_clades_filter"] = ",".join(clades_filter)
        df.at[rec[0], "sc2rf_clades_regions_filter"] = ",".join(regions_filter)
        df.at[rec[0], "sc2rf_clades_regions_length"] = ",".join(regions_length)
        df.at[rec[0], "sc2rf_breakpoints_regions_filter"] = ",".join(breakpoints_filter)

    # write exclude strains
    outpath_exclude = os.path.join(outdir, "sc2rf.recombinants.exclude.tsv")
    if len(drop_strains) > 0:
        with open(outpath_exclude, "w") as outfile:
            for strain, reason in drop_strains.items():
                outfile.write(strain + "\t" + reason + "\n")
    else:
        cmd = "touch {outpath}".format(outpath=outpath_exclude)
        os.system(cmd)

    # drop strains
    drop_strains = set(drop_strains.keys())
    df.drop(drop_strains, inplace=True)

    # write output table
    outpath_rec = os.path.join(outdir, "sc2rf.recombinants.tsv")
    df.to_csv(outpath_rec, sep="\t")

    # write output strains
    outpath_strains = os.path.join(outdir, "sc2rf.recombinants.txt")
    strains = "\n".join(list(df.index))
    with open(outpath_strains, "w") as outfile:
        outfile.write(strains + "\n")

    # filter the ansi output
    inpath_ansi = os.path.join(outdir, "sc2rf.ansi.txt")
    outpath_ansi = os.path.join(outdir, "sc2rf.recombinants.ansi.txt")
    if len(drop_strains) > 0:
        cmd = "cut -f 1 {exclude} | grep -v -f - {inpath} > {outpath}".format(
            exclude=outpath_exclude,
            inpath=inpath_ansi,
            outpath=outpath_ansi,
        )
    else:
        cmd = "cp -f {inpath} {outpath}".format(
            inpath=inpath_ansi,
            outpath=outpath_ansi,
        )
    os.system(cmd)

    # write alignment
    outpath_fasta = os.path.join(outdir, "sc2rf.recombinants.fasta")

    # first extract the reference genome
    cmd = "seqkit grep -p '{custom_ref}' {aligned} > {outpath_fasta};".format(
        custom_ref=custom_ref,
        aligned=aligned,
        outpath_fasta=outpath_fasta,
    )
    os.system(cmd)
    # Next all the recombinant strains
    cmd = "seqkit grep -f {outpath_strains} {aligned} >> {outpath_fasta};".format(
        outpath_strains=outpath_strains,
        aligned=aligned,
        outpath_fasta=outpath_fasta,
    )
    os.system(cmd)


if __name__ == "__main__":
    main()
