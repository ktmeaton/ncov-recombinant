#!/usr/bin/env python3

import pandas as pd
import click
import os

NO_DATA_CHAR = "NA"


@click.command()
@click.option("--csv", help="CSV output from sc2rf.", required=True)
@click.option("--ansi", help="ANSI output from sc2rf.", required=False)
@click.option("--min-len", help="Minimum region length.", required=False, default=1000)
@click.option(
    "--max-parents", help="Maximum number of parents.", required=False, default=2
)
@click.option("--outdir", help="Output directory", required=False, default=".")
@click.option(
    "--aligned",
    help="Extract recombinants from this alignment (Note: requires seqkit)",
    required=False,
)
@click.option(
    "--custom-ref",
    help="Reference strain name",
    required=False,
    default="Wuhan/Hu-1/2019",
)
@click.option(
    "--issues", help="Issues TSV metadata from pango-designation", required=False
)
@click.option("--qc", help="Nextclade QC Output TSV", required=False)
@click.option(
    "--max-breakpoints",
    help="The maximum number of breakpoints",
    required=False,
    default=2,
)
def main(
    csv,
    ansi,
    min_len,
    outdir,
    aligned,
    custom_ref,
    max_parents,
    issues,
    qc,
    max_breakpoints,
):
    """Detect recombinant seqences from sc2rf. Dependencies: pandas, click"""

    # -----------------------------------------------------------------------------
    # Import Dataframe

    # sc2rf output (required)
    df = pd.read_csv(csv, sep=",", index_col=0)
    df.fillna("", inplace=True)
    df["sc2rf_clades_filter"] = [NO_DATA_CHAR] * len(df)
    df["sc2rf_regions_filter"] = [NO_DATA_CHAR] * len(df)
    df["sc2rf_breakpoints_filter"] = [NO_DATA_CHAR] * len(df)
    df["sc2rf_num_breakpoints_filter"] = [NO_DATA_CHAR] * len(df)

    # if using issues.tsv of pango-designation issues (optional)
    # does lineage assignment by parent+breakpoint matching
    if issues:

        df["sc2rf_lineage"] = [NO_DATA_CHAR] * len(df)
        breakpoint_col = "breakpoints_curated"
        parents_col = "parents_curated"
        breakpoint_df = pd.read_csv(issues, sep="\t")
        breakpoint_df.fillna(NO_DATA_CHAR, inplace=True)
        drop_rows = breakpoint_df[breakpoint_df[breakpoint_col] == NO_DATA_CHAR].index
        breakpoint_df.drop(drop_rows, inplace=True)

        # Convert CSV to lists
        breakpoint_df[breakpoint_col] = [
            bp.split(",") for bp in breakpoint_df[breakpoint_col]
        ]
        breakpoint_df[parents_col] = [p.split(",") for p in breakpoint_df[parents_col]]

        # Consider a breakpoint match if within 50 base pairs
        breakpoint_approx_bp = 50

    # Initialize a dictionary of strains to drop with
    # key: strain, value: reason
    drop_strains = {}

    for rec in df.iterrows():

        regions_str = rec[1]["regions"]
        regions_split = regions_str.split(",")

        # Keys are going to be the start coord of the region
        regions_filter = {}
        breakpoints_filter = []

        prev_clade = None
        prev_start_coord = 0
        prev_end_coord = 0

        for region in regions_split:
            coords = region.split("|")[0]
            clade = region.split("|")[1]
            start_coord = int(coords.split(":")[0])
            end_coord = int(coords.split(":")[1])
            region_len = (end_coord - start_coord) + 1
            coord_list = list(regions_filter)
            coord_list.reverse()

            # -----------------------------------------------------------------
            # FIRST PASS

            # Just ignore singletons, no calculation necessary
            if region_len == 1:
                continue

            # Is this the first region?
            if not prev_clade:
                regions_filter[start_coord] = {"clade": clade, "end": end_coord}
                prev_start_coord = start_coord

            # -----------------------------------------------------------------
            # SECOND PASS: REVERSE ITER COLLAPSE

            for coord in coord_list:
                prev_start_coord = coord
                prev_end_coord = regions_filter[prev_start_coord]["end"]
                prev_region_len = (prev_end_coord - prev_start_coord) + 1
                prev_clade = regions_filter[coord]["clade"]

                # If the previous region was too short AND from a different clade
                # Delete that previous region, it's an intermission
                if prev_region_len < min_len and clade != prev_clade:
                    del regions_filter[prev_start_coord]

                # Collapse the current region into the previous one
                elif clade == prev_clade:
                    regions_filter[prev_start_coord]["end"] = end_coord
                    break

                # Otherwise, clades differ and this is the start of a new region
                else:
                    regions_filter[start_coord] = {"clade": clade, "end": end_coord}
                    break

            # These get updated regardless of condition
            prev_clade = clade
            prev_end_coord = end_coord

        # Check the last region for length
        if len(regions_filter) > 1:
            start_coord = list(regions_filter)[-1]
            end_coord = regions_filter[start_coord]["end"]
            region_len = end_coord - start_coord
            if region_len < min_len:
                del regions_filter[start_coord]

        # Check if all the regions were collapsed
        if len(regions_filter) < 2:
            drop_strains[rec[0]] = "all regions collapsed"

        # -----------------------------------------------------------------
        # THIRD PASS: BREAKPOINT DETECTION

        prev_start_coord = None
        for start_coord in regions_filter:

            end_coord = regions_filter[start_coord]["end"]

            # Skip the first record for breakpoints
            if prev_start_coord:
                breakpoint_start = prev_end_coord + 1
                breakpoint_end = start_coord - 1
                breakpoint = "{}:{}".format(breakpoint_start, breakpoint_end)
                breakpoints_filter.append(breakpoint)

            prev_start_coord = start_coord
            prev_end_coord = end_coord

        # check if the number of breakpoints changed
        # the filtered breakpoints should only ever be equal or less
        # Except! If the breakpoints were initially 0
        num_breakpoints = df["breakpoints"][rec[0]]
        num_breakpoints_filter = len(breakpoints_filter)

        if (num_breakpoints > 0) and (num_breakpoints_filter > num_breakpoints):
            drop_strains[
                rec[0]
            ] = "{} filtered breakpoints > {} raw breakpoints".format(
                num_breakpoints_filter, num_breakpoints
            )

        # Check for too many breakpoints
        if num_breakpoints > max_breakpoints:
            drop_strains[rec[0]] = "{} breakpoints > {} max breakpoints".format(
                num_breakpoints,
                max_breakpoints,
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

        # Identify lineage based on breakpoint and parents!
        # But only if we've suppled the issues.tsv for pango-designation
        if issues:
            sc2rf_lineage = ""
            sc2rf_lineages = {bp_s: [] for bp_s in breakpoints_filter}

            for bp_s in breakpoints_filter:
                start_s = int(bp_s.split(":")[0])
                end_s = int(bp_s.split(":")[1])

                match_found = False

                for bp_rec in breakpoint_df.iterrows():

                    # Skip over this potential lineage if parents are wrong
                    bp_parents = bp_rec[1][parents_col]
                    if bp_parents != clades_filter:
                        continue

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
                            match_found = True

                if not match_found:
                    sc2rf_lineages[bp_s].append(NO_DATA_CHAR)

            # if len(sc2rf_lineages) == num_breakpoints_filter:
            collapse_lineages = []
            for bp in sc2rf_lineages.values():
                for lineage in bp:
                    collapse_lineages.append(lineage)

            collapse_lineages = list(set(collapse_lineages))

            # When there are multiple breakpoint, a match must be the same for all!
            collapse_lineages_filter = []
            for lin in collapse_lineages:

                if lin == NO_DATA_CHAR:
                    continue
                # By default, assume they all match
                matches_all_bp = True
                for bp_s in sc2rf_lineages:
                    # If the lineage is missing, it's not in all bp
                    if lin not in sc2rf_lineages[bp_s]:
                        matches_all_bp = False
                        break

                # Check if we should drop it
                if matches_all_bp:
                    collapse_lineages_filter.append(lin)

            if len(collapse_lineages_filter) == 0:
                collapse_lineages_filter = [NO_DATA_CHAR]

            sc2rf_lineage = ",".join(collapse_lineages_filter)
            df.at[rec[0], "lineage"] = sc2rf_lineage

        df.at[rec[0], "sc2rf_clades_filter"] = ",".join(clades_filter)
        df.at[rec[0], "sc2rf_regions_filter"] = ",".join(regions_filter)
        df.at[rec[0], "sc2rf_regions_length"] = ",".join(regions_length)
        df.at[rec[0], "sc2rf_breakpoints_filter"] = ",".join(breakpoints_filter)
        df.at[rec[0], "sc2rf_num_breakpoints_filter"] = num_breakpoints

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

    # -------------------------------------------------------------------------
    # force include nextclade recombinants
    if qc:
        qc_df = pd.read_csv(qc, sep="\t", index_col=0, low_memory=False)

        for rec in qc_df.iterrows():
            strain = rec[0]
            if strain in df.index:
                continue
            if rec[1]["clade"] != "recombinant":
                continue
            df.loc[strain] = NO_DATA_CHAR

    # -------------------------------------------------------------------------
    # write output table

    # Drop old columns
    df.drop(
        ["examples", "intermissions", "breakpoints", "regions"],
        axis="columns",
        inplace=True,
    )
    df.insert(loc=0, column="strain", value=df.index)
    df.rename(
        {
            "sc2rf_clades_filter": "sc2rf_parents",
            "sc2rf_regions_filter": "sc2rf_regions",
            "sc2rf_breakpoints_filter": "sc2rf_breakpoints",
            "sc2rf_num_breakpoints_filter": "sc2rf_num_breakpoints",
        },
        axis="columns",
        inplace=True,
    )
    outpath_rec = os.path.join(outdir, "sc2rf.recombinants.tsv")
    df.to_csv(outpath_rec, sep="\t", index=False)

    # -------------------------------------------------------------------------
    # write output strains
    outpath_strains = os.path.join(outdir, "sc2rf.recombinants.txt")
    strains = list(df.index)
    strains_txt = "\n".join(strains)
    with open(outpath_strains, "w") as outfile:
        outfile.write(strains_txt + "\n")

    # -------------------------------------------------------------------------
    # filter the ansi output
    if ansi:
        outpath_ansi = os.path.join(outdir, "sc2rf.recombinants.ansi.txt")
        if len(drop_strains) > 0:
            cmd = "cut -f 1 {exclude} | grep -v -f - {inpath} > {outpath}".format(
                exclude=outpath_exclude,
                inpath=ansi,
                outpath=outpath_ansi,
            )
        else:
            cmd = "cp -f {inpath} {outpath}".format(
                inpath=ansi,
                outpath=outpath_ansi,
            )
        os.system(cmd)

    # -------------------------------------------------------------------------
    # write alignment
    if aligned:
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
