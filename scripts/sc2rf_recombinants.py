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
@click.option(
    "--issues", help="Issues TSV metadata from pango-designation", required=True
)
def main(
    tsv,
    min_len,
    outdir,
    aligned,
    custom_ref,
    max_parents,
    issues,
):
    """Detect recombinant seqences from sc2rf."""

    # -----------------------------------------------------------------------------
    # Import Dataframe

    # sc2rf output
    df = pd.read_csv(tsv, sep="\t", index_col=0)
    df.fillna("", inplace=True)
    df["sc2rf_clades_filter"] = [NO_DATA_CHAR] * len(df)
    df["sc2rf_clades_regions_filter"] = [NO_DATA_CHAR] * len(df)
    df["sc2rf_breakpoints_regions_filter"] = [NO_DATA_CHAR] * len(df)
    df["sc2rf_lineage"] = [NO_DATA_CHAR] * len(df)

    # breakpoint
    breakpoint_col = "breakpoints_curated"
    breakpoint_df = pd.read_csv(issues, sep="\t")
    breakpoint_df.fillna(NO_DATA_CHAR, inplace=True)
    drop_rows = breakpoint_df[breakpoint_df[breakpoint_col] == NO_DATA_CHAR].index
    breakpoint_df.drop(drop_rows, inplace=True)
    breakpoint_df[breakpoint_col] = [
        bp.split(",") for bp in breakpoint_df[breakpoint_col]
    ]

    # A breakpoint match if within 10 base pairs
    breakpoint_approx_bp = 10

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

        # Process coords in between region as breakpoints
        # print("\t",regions_filter)
        # print("\t",breakpoints_filter)

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

        # Extract the lengths of each region
        regions_length = [str(regions_filter[s]["end"] - s) for s in regions_filter]

        # Construct the new filtered regions
        regions_filter = [
            "{}:{}|{}".format(s, regions_filter[s]["end"], regions_filter[s]["clade"])
            for s in regions_filter
        ]

        # Identify lineage based on breakpoint
        sc2rf_lineage = ""
        sc2rf_lineages = {bp: [] for bp in breakpoints_filter}

        for bp_s in breakpoints_filter:
            start_s = int(bp_s.split(":")[0])
            end_s = int(bp_s.split(":")[1])

            for bp_rec in breakpoint_df.iterrows():
                for bp_i in bp_rec[1][breakpoint_col]:
                    start_i = int(bp_i.split(":")[0])
                    end_i = int(bp_i.split(":")[1])
                    start_diff = abs(start_s - start_i)
                    end_diff = abs(end_s - end_i)

                    if (
                        start_diff <= breakpoint_approx_bp
                        and end_diff <= breakpoint_approx_bp
                    ):

                        sc2rf_lineages[bp_s].append(bp_rec[1]["lineage"])

            # Collapse any duplicate lineages (ex. XF)
            sc2rf_lineages[bp_s] = list(set(sc2rf_lineages[bp_s]))

        # if len(sc2rf_lineages) == num_breakpoints_filter:
        collapse_lineages = []
        for bp in sc2rf_lineages.values():
            for lineage in bp:
                collapse_lineages.append(lineage)

        sc2rf_lineage = ",".join(list(set(collapse_lineages)))

        df.at[rec[0], "sc2rf_clades_filter"] = ",".join(clades_filter)
        df.at[rec[0], "sc2rf_clades_regions_filter"] = ",".join(regions_filter)
        df.at[rec[0], "sc2rf_clades_regions_length"] = ",".join(regions_length)
        df.at[rec[0], "sc2rf_breakpoints_regions_filter"] = ",".join(breakpoints_filter)
        df.at[rec[0], "sc2rf_breakpoints_regions_lineages"] = ",".join(
            breakpoints_filter
        )
        df.at[rec[0], "sc2rf_lineage"] = sc2rf_lineage

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
