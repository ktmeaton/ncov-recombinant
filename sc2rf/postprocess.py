#!/usr/bin/env python3

import pandas as pd
import click
import os
import logging
import requests
import sys
import time
from Bio import Phylo

NO_DATA_CHAR = "NA"

LAPIS_LINEAGE_COL = "pangoLineage"
LAPIS_OPEN_BASE = (
    "https://lapis.cov-spectrum.org/open/v1/sample/aggregated"
    + "?fields={lineage_col}".format(lineage_col=LAPIS_LINEAGE_COL)
    + "&nucMutations={mutations}"
)

LAPIS_GISAID_BASE = (
    "https://lapis.cov-spectrum.org/gisaid/v1/sample/aggregated"
    + "?accessKey={access_key}"
    + "&fields={lineage_col}".format(lineage_col=LAPIS_LINEAGE_COL)
    + "&nucMutations={mutations}"
)

LINEAGE_PROP_THRESHOLD = 0.01
LAPIS_SLEEP_TIME = 0
# Consider a breakpoint match if within 50 base pairs
BREAKPOINT_APPROX_BP = 50

DATAFRAME_COLS = [
    "sc2rf_status",
    "sc2rf_details",
    "sc2rf_lineage",
    "sc2rf_clades_filter",
    "sc2rf_regions_filter",
    "sc2rf_regions_length",
    "sc2rf_breakpoints_filter",
    "sc2rf_num_breakpoints_filter",
    "sc2rf_breakpoints_motif",
    "sc2rf_unique_subs_filter",
    "sc2rf_alleles_filter",
    "sc2rf_intermission_allele_ratio",
    "cov-spectrum_parents",
    "cov-spectrum_parents_confidence",
    "cov-spectrum_parents_subs",
    "sc2rf_parents_conflict",
]


def create_logger(logfile=None):
    # create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    if logfile:
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def reverse_iter_collapse(
    regions,
    min_len,
    max_breakpoint_len,
    start_coord,
    end_coord,
    clade,
):
    """Collapse adjacent regions from the same parent into one region."""

    coord_list = list(regions.keys())
    coord_list.reverse()

    for coord in coord_list:
        prev_start_coord = coord
        prev_end_coord = regions[prev_start_coord]["end"]
        prev_region_len = (prev_end_coord - prev_start_coord) + 1
        prev_clade = regions[coord]["clade"]
        breakpoint_len = start_coord - prev_end_coord

        # If the previous region was too short AND from a different clade
        # Delete that previous region, it's an intermission
        if prev_region_len < min_len and clade != prev_clade:
            del regions[prev_start_coord]

        # If the previous breakpoint was too long AND from a different clade
        # Don't add the current region
        elif (
            start_coord != prev_start_coord
            and clade != prev_clade
            and (max_breakpoint_len != -1 and breakpoint_len > max_breakpoint_len)
        ):
            break

        # Collapse the current region into the previous one
        elif clade == prev_clade:
            regions[prev_start_coord]["end"] = end_coord
            break

        # Otherwise, clades differ and this is the start of a new region
        else:
            regions[start_coord] = {"clade": clade, "end": end_coord}
            break

    # Check if the reveres iter collapse wound up deleting all the regions
    if len(regions) == 0:
        regions[start_coord] = {"clade": clade, "end": end_coord}


@click.command()
@click.option(
    "--csv",
    help="CSV output from sc2rf, multiple files separate by commas.",
    required=True,
)
@click.option(
    "--ansi",
    help="ANSI output from sc2rf, multiple files separate by commas.",
    required=False,
)
@click.option("--motifs", help="TSV of breakpoint motifs", required=False)
@click.option(
    "--prefix",
    help="Prefix for output files.",
    required=False,
    default="sc2rf.recombinants",
)
@click.option(
    "--min-len",
    help="Minimum region length (-1 to disable filter).",
    required=False,
    default=-1,
)
@click.option(
    "--min-consec-allele",
    help="Minimum number of consecutive alleles in a region (-1 to disable filter).",
    required=False,
    default=-1,
)
@click.option(
    "--max-breakpoint-len",
    help="Maximum breakpoint length (-1 to disable filter).",
    required=False,
    default=-1,
)
@click.option(
    "--max-parents",
    help="Maximum number of parents (-1 to disable filter).",
    required=False,
    default=-1,
)
@click.option("--outdir", help="Output directory", required=False, default=".")
@click.option(
    "--aligned",
    help="Extract recombinants from this alignment (Note: requires seqkit)",
    required=False,
)
@click.option(
    "--nextclade",
    help="Nextclade TSV output from the sars-cov-2.",
    required=False,
)
@click.option(
    "--nextclade-no-recomb",
    help="Nextclade TSV output from the sars-cov-2-no-recomb dataset.",
    required=False,
)
@click.option(
    "--nextclade-auto-pass",
    help="CSV list of lineage assignments that will be called positive",
    required=False,
)
@click.option(
    "--max-breakpoints",
    help="The maximum number of breakpoints (-1 to disable breakpoint filtering)",
    required=False,
    default=-1,
)
@click.option(
    "--lapis",
    help="Enable the LAPIS API to identify parental lineages from covSPECTRUM.",
    is_flag=True,
    required=False,
    default=False,
)
@click.option(
    "--gisaid-access-key",
    help="The accessKey to query GISAID data with LAPIS",
    required=False,
)
@click.option(
    "--issues",
    help="Issues TSV metadata from pango-designation",
    required=False,
)
@click.option(
    "--lineage-tree",
    help="Newick tree of pangolin lineage hierarchies",
    required=False,
)
@click.option(
    "--metadata",
    help="Sample metadata TSV, used to include negative samples in the final output.",
    required=False,
)
@click.option("--log", help="Path to a log file", required=False)
@click.option(
    "--dup-method",
    help=(
        "Method for resolving duplicate results:\n"
        + "\nfirst: Use first positive results found.\n"
        + "\nlast: Use last positive results found.\n"
        + "\nmin_bp: Use fewest breakpoints."
        + "\nmin_uncertainty: Use small breakpoint intervals."
    ),
    type=click.Choice(
        ["first", "last", "min_bp", "min_uncertainty"],
        case_sensitive=False,
    ),
    required=False,
    default="lineage",
)
def main(
    csv,
    ansi,
    prefix,
    min_len,
    min_consec_allele,
    max_breakpoint_len,
    outdir,
    aligned,
    nextclade,
    nextclade_auto_pass,
    nextclade_no_recomb,
    max_parents,
    issues,
    max_breakpoints,
    motifs,
    log,
    lineage_tree,
    metadata,
    dup_method,
    lapis,
    gisaid_access_key,
):
    """Detect recombinant seqences from sc2rf. Dependencies: pandas, click"""

    # Check for directory
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # create logger
    logger = create_logger(logfile=log)

    # -----------------------------------------------------------------------------
    # Import Optional Data Files

    # (Optional) issues.tsv of pango-designation issues
    #            lineage assignment by parent+breakpoint matching
    if issues:

        logger.info("Parsing issues: {}".format(issues))

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

    # (Optional) motifs dataframe
    if motifs:
        logger.info("Parsing motifs: {}".format(motifs))
        motifs_df = pd.read_csv(motifs, sep="\t")

    # (Optional) nextclade tsv dataframe
    if nextclade:
        logger.info("Parsing nextclade: {}".format(nextclade))
        nextclade_df = pd.read_csv(nextclade, sep="\t")
        nextclade_df["seqName"] = [str(s) for s in nextclade_df["seqName"]]
        nextclade_df.set_index("seqName", inplace=True)
        nextclade_df.fillna(NO_DATA_CHAR, inplace=True)

        if nextclade_auto_pass:
            nextclade_auto_pass_lineages = nextclade_auto_pass.split(",")
            # Identify samples to autopass
            auto_pass_df = nextclade_df[
                (nextclade_df["Nextclade_pango"] != NO_DATA_CHAR)
                & (nextclade_df["Nextclade_pango"].isin(nextclade_auto_pass_lineages))
            ]

    # (Optional) nextclade tsv dataframe no-recomb dataset
    if nextclade_no_recomb:
        logger.info(
            "Parsing nextclade no-recomb output: {}".format(nextclade_no_recomb)
        )
        nextclade_no_recomb_df = pd.read_csv(nextclade_no_recomb, sep="\t")
        nextclade_no_recomb_df["seqName"] = [
            str(s) for s in nextclade_no_recomb_df["seqName"]
        ]
        nextclade_no_recomb_df.set_index("seqName", inplace=True)
        nextclade_no_recomb_df.fillna(NO_DATA_CHAR, inplace=True)

    # (Optional) metadata tsv dataframe to find negatives missing from sc2rf
    if metadata:
        logger.info("Parsing metadata tsv: {}".format(metadata))
        metadata_df = pd.read_csv(metadata, sep="\t")
        metadata_df["strain"] = [str(s) for s in metadata_df["strain"]]
        metadata_df.fillna(NO_DATA_CHAR, inplace=True)

    # (Optional) phylogenetic tree of pangolineage lineages
    if lineage_tree:
        logger.info("Parsing lineage tree: {}".format(lineage_tree))
        tree = Phylo.read(lineage_tree, "newick")

    # -----------------------------------------------------------------------------
    # Import Dataframes of Potential Positive Recombinants

    # note: Add the end of this section, only positives and false positives will
    #       be in the dataframe.

    # sc2rf csv output (required)
    df = pd.DataFrame()
    csv_split = csv.split(",")
    # Store a dict of duplicate strains
    duplicate_strains = {}

    for csv_file in csv_split:
        logger.info("Parsing csv: {}".format(csv_file))

        try:
            temp_df = pd.read_csv(csv_file, sep=",")
        except pd.errors.EmptyDataError:
            logger.warning("No records in csv: {}".format(csv_file))
            temp_df = pd.DataFrame()

        # Add column to indicate which csv file results come from (debugging)
        temp_df.insert(
            loc=len(temp_df.columns),
            column="csv_file",
            value=os.path.basename(csv_file),
        )

        # Convert to str type
        temp_df["sample"] = [str(s) for s in temp_df["sample"]]
        temp_df.set_index("sample", inplace=True)

        # Add column to hold original strain name before marking duplicates
        temp_df.insert(
            loc=len(temp_df.columns),
            column="strain",
            value=temp_df.index,
        )

        # If the df has no records, this is the first csv
        if len(df) == 0:
            df = temp_df
        else:
            # Keep all dups for now, only retain best results at end
            for strain in temp_df.index:
                if strain in list(df["strain"]):
                    if strain not in duplicate_strains:
                        duplicate_strains[strain] = 1

                    # add suffix "_dup<i>", remove at the end of scripts
                    dup_1 = strain + "_dup{}".format(duplicate_strains[strain])
                    df.rename(index={strain: dup_1}, inplace=True)

                    duplicate_strains[strain] += 1

                    dup_2 = strain + "_dup{}".format(duplicate_strains[strain])
                    temp_df.rename(index={strain: dup_2}, inplace=True)

            # Combine primary and secondary data frames
            df = pd.concat([df, temp_df])

    df.fillna("", inplace=True)

    # -------------------------------------------------------------------------
    # Initialize new stat columns to NA

    # note: Add the end of this section, only positives and false positives will
    #       be in the sc2rf_details_dict

    for col in DATAFRAME_COLS:
        df[col] = [NO_DATA_CHAR] * len(df)

    # Initialize a dictionary of sc2rf details and false positives
    # key: strain, value: list of reasons
    false_positives_dict = {}
    sc2rf_details_dict = {strain: [] for strain in df.index}

    # -------------------------------------------------------------------------
    # Add in the Negatives (if metadata was specified)
    # Avoiding the Bio module, I just need names not sequences

    if metadata:

        logger.info("Reporting non-recombinants in metadata as negatives")
        for strain in list(metadata_df["strain"]):
            # Ignore this strain if it's already in dataframe (it's a recombinant)
            if strain in list(df["strain"]):
                continue
            # Otherwise add it, with no data as default
            df.loc[strain] = NO_DATA_CHAR
            df.at[strain, "strain"] = strain
            df.at[strain, "sc2rf_status"] = "negative"
            sc2rf_details_dict[strain] = []

    # ---------------------------------------------------------------------
    # Auto-pass lineages from nextclade assignment, that were also detected by sc2rf

    if nextclade and nextclade_auto_pass:

        logger.info(
            "Auto-passing lineages: {}".format(",".join(nextclade_auto_pass_lineages))
        )

        for rec in auto_pass_df.iterrows():

            # Note the strain is the true strain, not _dup suffix
            strain = rec[0]

            lineage = auto_pass_df.loc[strain]["Nextclade_pango"]
            details = "nextclade-auto-pass {}".format(lineage)

            # Case 1 : In df with NO DUPS, set the status to positive, update details
            if strain in list(df.index):

                sc2rf_details_dict[strain].append(details)
                df.at[strain, "sc2rf_status"] = "positive"
                df.at[strain, "sc2rf_details"] = ";".join(sc2rf_details_dict[strain])

            # Case 2: In df WITH DUPS, set the dups status to positive, update details
            elif strain in list(df["strain"]):

                dup_strains = list(df[df["strain"] == strain].index)
                for dup in dup_strains:

                    sc2rf_details_dict[dup].append(details)
                    df.at[dup, "sc2rf_status"] = "positive"
                    df.at[dup, "sc2rf_details"] = ";".join(sc2rf_details_dict[dup])

            # Case 3: If it's not in the dataframe add it
            else:
                sc2rf_details_dict[strain] = [details]

                # new row
                row_dict = {col: [NO_DATA_CHAR] for col in df.columns}
                row_dict["strain"] = strain
                row_dict["sc2rf_status"] = "positive"
                row_dict["sc2rf_details"] = ";".join(sc2rf_details_dict[strain])

                row_df = pd.DataFrame(row_dict).set_index("strain")
                df = pd.concat([df, row_df], ignore_index=False)

    # -------------------------------------------------------------------------
    # Begin Post-Processing
    logger.info("Post-processing table")

    # Iterate through all positive and negative recombinantions
    for rec in df.iterrows():

        # Skip over negative recombinants
        if rec[1]["sc2rf_status"] == "negative":
            continue

        strain = rec[0]

        # Check if this strain was auto-passed
        strain_auto_pass = False
        for detail in sc2rf_details_dict[strain]:
            if "auto-pass" in detail:
                strain_auto_pass = True

        regions_str = rec[1]["regions"]
        regions_split = regions_str.split(",")

        alleles_str = rec[1]["alleles"]
        alleles_split = alleles_str.split(",")

        unique_subs_str = rec[1]["unique_subs"]
        unique_subs_split = unique_subs_str.split(",")

        # Keys are going to be the start coord of the region
        regions_filter = {}
        unique_subs_filter = []
        alleles_filter = []
        breakpoints_filter = []

        # Store alleles for filtering
        intermission_alleles = []
        alleles_by_parent = {}

        prev_clade = None
        prev_start_coord = 0
        prev_end_coord = 0

        # ---------------------------------------------------------------------
        # FIRST PASS

        # If the region is NA, this is an auto-passed recombinant
        # and sc2rf couldn't find any breakpoints, skip the rest of processing
        # and continue on to next strain

        if regions_split == [NO_DATA_CHAR]:
            continue

        for region in regions_split:

            coords = region.split("|")[0]
            clade = region.split("|")[1]
            start_coord = int(coords.split(":")[0])
            end_coord = int(coords.split(":")[1])
            region_len = (end_coord - start_coord) + 1
            coord_list = list(regions_filter)
            coord_list.reverse()

            # Just ignore singletons, no calculation necessary
            if region_len == 1:
                continue

            # Is this the first region?
            if not prev_clade:
                regions_filter[start_coord] = {"clade": clade, "end": end_coord}
                prev_clade = clade
                prev_start_coord = start_coord

            # Moving 3' to 5', collapse adjacent regions from the same parent
            # Modifies regions in place
            reverse_iter_collapse(
                regions=regions_filter,
                min_len=min_len,
                max_breakpoint_len=max_breakpoint_len,
                start_coord=start_coord,
                end_coord=end_coord,
                clade=clade,
            )

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

        # -----------------------------------------------------------------
        # SECOND PASS: UNIQUE SUBSTITUTIONS

        regions_filter_collapse = {}

        for start_coord in list(regions_filter):
            clade = regions_filter[start_coord]["clade"]
            end_coord = regions_filter[start_coord]["end"]

            region_contains_unique_sub = False

            for sub in unique_subs_split:

                sub_coord = int(sub.split("|")[0])
                sub_parent = sub.split("|")[1]

                if (
                    sub_coord >= start_coord
                    and sub_coord <= end_coord
                    and sub_parent == clade
                ):
                    region_contains_unique_sub = True
                    unique_subs_filter.append(sub)

            # If it contains a unique sub, check if we should
            # collapse into previous parental region
            if region_contains_unique_sub:
                reverse_iter_collapse(
                    regions=regions_filter_collapse,
                    min_len=min_len,
                    max_breakpoint_len=max_breakpoint_len,
                    start_coord=start_coord,
                    end_coord=end_coord,
                    clade=clade,
                )

        regions_filter = regions_filter_collapse

        # -----------------------------------------------------------------
        # THIRD PASS: CONSECUTIVE ALLELES

        regions_filter_collapse = {}

        for start_coord in list(regions_filter):
            clade = regions_filter[start_coord]["clade"]
            end_coord = regions_filter[start_coord]["end"]

            num_consec_allele = 0

            for allele in alleles_split:

                allele_coord = int(allele.split("|")[0])
                allele_parent = allele.split("|")[1]

                if (
                    allele_coord >= start_coord
                    and allele_coord <= end_coord
                    and allele_parent == clade
                ):
                    num_consec_allele += 1
                    alleles_filter.append(allele)

            # If there are sufficient consecutive alleles, check if we should
            # collapse into previous parental region
            if num_consec_allele >= min_consec_allele:
                reverse_iter_collapse(
                    regions=regions_filter_collapse,
                    min_len=min_len,
                    max_breakpoint_len=max_breakpoint_len,
                    start_coord=start_coord,
                    end_coord=end_coord,
                    clade=clade,
                )

        regions_filter = regions_filter_collapse

        # -----------------------------------------------------------------
        # Check if all the regions were collapsed
        if len(regions_filter) < 2:
            sc2rf_details_dict[strain].append("single parent")
            # if this is an auto-pass lineage, don't add to false positives
            if not strain_auto_pass:
                false_positives_dict[strain] = ""

        # -----------------------------------------------------------------
        # FOURTH PASS: BREAKPOINT DETECTION

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
        # 2022-06-17: Why? Under what conditions does the filtered breakpoints increase?
        # Except! If the breakpoints were initially 0
        # num_breakpoints = df["breakpoints"][strain]
        num_breakpoints_filter = len(breakpoints_filter)

        # Check for too many breakpoints
        if max_breakpoints != -1:
            if num_breakpoints_filter > max_breakpoints:
                details = "{} breakpoints > {} max breakpoints".format(
                    num_breakpoints_filter,
                    max_breakpoints,
                )
                sc2rf_details_dict[strain].append(details)
                # if this is an auto-pass lineage, don't add to false positives
                if not strain_auto_pass:
                    false_positives_dict[strain] = ""

        # Identify the new filtered clades
        clades_filter = [regions_filter[s]["clade"] for s in regions_filter]
        # clades_filter_csv = ",".join(clades_filter)
        num_parents = len(set(clades_filter))
        if max_parents != -1:
            if num_parents > max_parents:
                details = "{} parents > {}".format(num_parents, max_parents)
                sc2rf_details_dict[strain].append(details)
                # if this is an auto-pass lineage, don't add to false positives
                if not strain_auto_pass:
                    false_positives_dict[strain] = ""

        # ---------------------------------------------------------------------
        # Intermission/Minor Parent Allele Ratio
        # ie. alleles that conflict with the parental region
        #   be lenient if there were more parents initially reported by sc2rf (ex. >2)
        #   because this wil lead to large numbers of unresolved intermissions

        original_parents = rec[1]["examples"]
        num_original_parents = len(original_parents.split(","))

        if num_original_parents > num_parents:
            intermission_allele_ratio = "NA"
        else:
            for start_coord in regions_filter:
                end_coord = regions_filter[start_coord]["end"]
                clade = regions_filter[start_coord]["clade"]

                for allele in alleles_split:

                    allele_coord = int(allele.split("|")[0])
                    allele_clade = allele.split("|")[1]
                    allele_nuc = allele.split("|")[2]

                    # Skip if this allele is not found in the current region
                    if allele_coord < start_coord or allele_coord > end_coord:
                        continue

                    # Skip missing data
                    if allele_nuc == "N":
                        continue

                    # Check if this allele's origins conflicts with the parental region
                    if allele_clade != clade:
                        intermission_alleles.append(allele)
                    else:
                        if clade not in alleles_by_parent:
                            alleles_by_parent[clade] = []
                        alleles_by_parent[clade].append(allele)

            # Add in alleles that were not assigned to any region
            for allele in alleles_split:
                allele_nuc = allele.split("|")[2]
                # Skip missing data
                if allele_nuc == "N":
                    continue

                allele_coord = int(allele.split("|")[0])
                allele_in_region = False
                for start_coord in regions_filter:
                    end_coord = regions_filter[start_coord]["end"]
                    if allele_coord >= start_coord and allele_coord <= end_coord:
                        allele_in_region = True

                # Alleles not assigned to any region are counted as intermissions
                if not allele_in_region:
                    intermission_alleles.append(allele)

            # Identify the "minor" parent (least number of alleles)
            # minor_parent = None
            minor_num_alleles = len(alleles_split)

            for parent in alleles_by_parent:
                num_alleles = len(alleles_by_parent[parent])
                if num_alleles <= minor_num_alleles:
                    # minor_parent = parent
                    minor_num_alleles = num_alleles

            intermission_allele_ratio = len(intermission_alleles) / minor_num_alleles

            # When the ratio is above 1, that means there are more intermission than
            # minor parent alleles. But don't override the false_positive status
            # if this strain was already flagged as a false_positive previously
            if intermission_allele_ratio >= 1:
                sc2rf_details_dict[strain].append("intermission_allele_ratio >= 1")
                # if this is an auto-pass lineage, don't add to false positives
                if not strain_auto_pass:
                    false_positives_dict[strain] = ""

        # --------------------------------------------------------------------------
        # Extract the lengths of each region
        regions_length = [str(regions_filter[s]["end"] - s) for s in regions_filter]

        # Construct the new filtered regions
        regions_filter = [
            "{}:{}|{}".format(s, regions_filter[s]["end"], regions_filter[s]["clade"])
            for s in regions_filter
        ]

        # --------------------------------------------------------------------------
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
                            start_diff <= BREAKPOINT_APPROX_BP
                            and end_diff <= BREAKPOINT_APPROX_BP
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
            df.at[strain, "sc2rf_lineage"] = sc2rf_lineage

        # check for breakpoint motifs, to override lineage call
        # all breakpoints must include a motif!
        # ---------------------------------------------------------------------
        if motifs:
            breakpoints_motifs = []
            for bp in breakpoints_filter:
                bp_motif = False
                bp_start = int(bp.split(":")[0])
                bp_end = int(bp.split(":")[1])

                # Add buffers
                bp_start = bp_start - BREAKPOINT_APPROX_BP
                bp_end = bp_end + BREAKPOINT_APPROX_BP

                for motif_rec in motifs_df.iterrows():
                    motif_start = motif_rec[1]["start"]
                    motif_end = motif_rec[1]["end"]

                    # Is motif contained within the breakpoint
                    # Allow fuzzy matching
                    if motif_start >= bp_start and motif_end <= bp_end:
                        # print("\t\t", motif_start, motif_end)
                        bp_motif = True

                breakpoints_motifs.append(bp_motif)

            # If there's a lone "False" value, it gets re-coded to an
            # empty string on export. To prevent that, force it to be
            # the NO_DATA_CHAR (ex. 'NA')
            if len(breakpoints_motifs) == 0:
                breakpoints_motifs_str = [NO_DATA_CHAR]
            else:
                breakpoints_motifs_str = [str(m) for m in breakpoints_motifs]

            df.at[strain, "sc2rf_breakpoints_motif"] = ",".join(breakpoints_motifs_str)

            # Override the linaege call if one breakpoint had no motif
            if False in breakpoints_motifs:
                sc2rf_details_dict[strain].append("missing breakpoint motif")
                # if this is an auto-pass lineage, don't add to false positives
                if not strain_auto_pass:
                    false_positives_dict[strain] = ""

        df.at[strain, "sc2rf_clades_filter"] = ",".join(clades_filter)
        df.at[strain, "sc2rf_regions_filter"] = ",".join(regions_filter)
        df.at[strain, "sc2rf_regions_length"] = ",".join(regions_length)
        df.at[strain, "sc2rf_breakpoints_filter"] = ",".join(breakpoints_filter)
        df.at[strain, "sc2rf_num_breakpoints_filter"] = num_breakpoints_filter
        df.at[strain, "sc2rf_unique_subs_filter"] = ",".join(unique_subs_filter)
        df.at[strain, "sc2rf_alleles_filter"] = ",".join(alleles_filter)
        df.at[strain, "sc2rf_intermission_allele_ratio"] = intermission_allele_ratio

        if strain not in false_positives_dict:
            df.at[strain, "sc2rf_status"] = "positive"
            # A sample can be positive with no breakpoints, if auto-pass
            if len(breakpoints_filter) != 0:
                sc2rf_details_dict[strain] = ["recombination detected"]
            # For auto-pass negatives, update the csv_file
            else:
                df.at[strain, "csv_file"] = NO_DATA_CHAR
        else:
            df.at[strain, "sc2rf_status"] = "false_positive"

        df.at[strain, "sc2rf_details"] = ";".join(sc2rf_details_dict[strain])

    # ---------------------------------------------------------------------
    # Resolve strains with duplicate results

    logger.info("Reconciling duplicate results with method: {}".format(dup_method))
    for strain in duplicate_strains:

        # Check if this strain was auto-passed
        strain_auto_pass = True if strain in auto_pass_df.index else False
        strain_df = df[df["strain"] == strain]
        strain_bp = list(set(strain_df["sc2rf_breakpoints_filter"]))

        num_dups = duplicate_strains[strain]
        # Which duplicates should we keep (1), which should we remove (many)
        keep_dups = []
        remove_dups = []

        for i in range(1, num_dups + 1):
            dup_strain = strain + "_dup{}".format(i)
            dup_status = df["sc2rf_status"][dup_strain]

            if dup_status == "positive":
                keep_dups.append(dup_strain)
            else:
                remove_dups.append(dup_strain)

        # Case 1. No keep dups were found, retain first removal dup, remove all else
        if len(keep_dups) == 0:
            keep_strain = remove_dups[0]
            keep_dups.append(keep_strain)
            remove_dups.remove(keep_strain)

        # Case 2. Multiple keeps found, but it's an auto-pass and they're all negative
        # Just take the first csv
        elif strain_auto_pass and strain_bp == [""]:
            remove_dups += keep_dups[1:]
            keep_dups = [keep_dups[0]]

        # Case 3. Multiple keeps found, use dup_method
        elif len(keep_dups) > 1:

            # First try to match to a published lineage
            # Key = dup_strain, value = csv of lineages
            lineage_strains = {}

            for dup_strain in keep_dups:
                dup_lineage = df["sc2rf_lineage"][dup_strain]

                if dup_lineage != NO_DATA_CHAR:
                    lineage_strains[dup_strain] = dup_lineage

            lineage_strains_matches = list(set(lineage_strains.values()))

            # Check if a match was found, but not more than 1 candidate lineage
            if len(lineage_strains) > 0 and len(lineage_strains_matches) < 2:
                keep_strain = list(lineage_strains)[0]
                # Remove all strains except the min one
                remove_dups = keep_dups + remove_dups
                remove_dups.remove(keep_strain)
                keep_dups = [keep_strain]

            # Otherwise, use a duplicate resolving method
            elif dup_method == "first":
                remove_dups += keep_dups[1:]
                keep_dups = [keep_dups[0]]

            elif dup_method == "last":
                remove_dups += keep_dups[0:-1]
                keep_dups = [keep_dups[-1]]

            elif dup_method == "min_bp":
                min_bp = None
                min_bp_strain = None
                for dup_strain in keep_dups:
                    num_bp = df["sc2rf_num_breakpoints_filter"][dup_strain]
                    if not min_bp:
                        min_bp = num_bp
                        min_bp_strain = dup_strain
                    elif num_bp < min_bp:
                        min_bp = num_bp
                        min_bp_strain = dup_strain
                # Remove all strains except the min one
                remove_dups = keep_dups + remove_dups
                remove_dups.remove(min_bp_strain)
                keep_dups = [min_bp_strain]

            elif dup_method == "min_uncertainty":

                min_uncertainty = None
                min_uncertainty_strain = None

                for dup_strain in keep_dups:

                    # '8394:12879,13758:22000'
                    bp = df["sc2rf_breakpoints_filter"][dup_strain]
                    # ['8394:12879','13758:22000']
                    # Skip if this is an auto-pass lineage with no breakpoints
                    if bp == "":
                        continue
                    bp = bp.split(",")
                    # [4485, 8242]
                    bp = [int(c.split(":")[1]) - int(c.split(":")[0]) for c in bp]
                    bp_uncertainty = sum(bp)

                    # Set to the first strain by default
                    if not min_uncertainty:
                        min_uncertainty_strain = dup_strain
                        min_uncertainty = bp_uncertainty
                    elif bp_uncertainty < min_uncertainty:
                        min_uncertainty_strain = dup_strain
                        min_uncertainty = bp_uncertainty

                # Remove all strains except the min one
                remove_dups = keep_dups + remove_dups
                remove_dups.remove(min_uncertainty_strain)
                keep_dups = [min_uncertainty_strain]

        # If this is an auto-pass negative, indicate no csvfile was used
        if strain_bp == [""]:
            keep_csv_file = NO_DATA_CHAR
        else:
            keep_csv_file = df["csv_file"][keep_dups[0]]
        logger.info(
            "Reconciling duplicate results for {}, retaining output from: {}".format(
                strain, keep_csv_file
            )
        )
        # Rename the accepted duplicate
        df.rename(index={keep_dups[0]: strain}, inplace=True)
        # Drop the rejected duplicates
        df.drop(labels=remove_dups, inplace=True)

    # ---------------------------------------------------------------------
    # Fix up duplicate strain names in false_positives

    false_positives_filter = {}
    for strain in false_positives_dict:

        strain_orig = strain.split("_dup")[0]
        status = df["sc2rf_status"][strain_orig]
        # If the original strain isn't positive
        # All duplicates were false positives and should be removed
        if status != "positive":
            false_positives_filter[strain_orig] = false_positives_dict[strain]
            sc2rf_details_dict[strain_orig] = sc2rf_details_dict[strain]

    false_positives_dict = false_positives_filter

    # ---------------------------------------------------------------------
    # Identify parent lineages by querying cov-spectrum mutations

    # We can only do this if:
    # 1. A nextclade no-recomb tsv file was specified with mutations
    # 2. Multiple regions were detected (not collapsed down to one parent region)
    # 3. The lapis API was enabled (--lapis)

    if nextclade_no_recomb and lapis:

        logger.info(
            "Identifying parent lineages based on nextclade no-recomb substitutions"
        )

        # Check if we're using open data or GISAID
        if gisaid_access_key:
            lapis_url_base = LAPIS_GISAID_BASE.format(
                access_key=gisaid_access_key, mutations="{mutations}"
            )
        else:
            lapis_url_base = LAPIS_OPEN_BASE

        positive_df = df[df["sc2rf_status"] == "positive"]
        total_positives = len(positive_df)
        progress_i = 0

        # keys = query, value = json
        query_subs_dict = {}

        for rec in positive_df.iterrows():

            strain = rec[0]
            strain_bp = rec[1]["sc2rf_breakpoints_filter"]

            # If this was an auto-pass negative strain, no regions for us to query
            if strain_bp == NO_DATA_CHAR:
                continue

            parent_clades = rec[1]["sc2rf_clades_filter"].split(",")

            progress_i += 1
            logger.info("{} / {}: {}".format(progress_i, total_positives, strain))

            regions_filter = positive_df["sc2rf_regions_filter"][strain].split(",")

            parent_lineages = []
            parent_lineages_confidence = []
            parent_lineages_subs = []

            substitutions = nextclade_no_recomb_df["substitutions"][strain].split(",")
            unlabeled_privates = nextclade_no_recomb_df[
                "privateNucMutations.unlabeledSubstitutions"
            ][strain].split(",")

            # Remove NA char
            if NO_DATA_CHAR in substitutions:
                substitutions.remove(NO_DATA_CHAR)
            if NO_DATA_CHAR in unlabeled_privates:
                unlabeled_privates.remove(NO_DATA_CHAR)

            # Exclude privates from mutations to query
            for private in unlabeled_privates:
                # Might not be in there if it's an indel
                if private in substitutions:
                    substitutions.remove(private)

            # Split mutations by region
            for region, parent_clade in zip(regions_filter, parent_clades):

                # If the parental clade is a recombinant, we'll allow the covlineages
                # to be recombinants
                parent_clade_is_recombinant = False
                for label in parent_clade.split("/"):
                    if label.startswith("X"):
                        parent_clade_is_recombinant = True

                region_coords = region.split("|")[0]
                region_start = int(region_coords.split(":")[0])
                region_end = int(region_coords.split(":")[1])
                region_subs = []

                for sub in substitutions:
                    sub_coord = int(sub[1:-1])
                    if sub_coord >= region_start and sub_coord <= region_end:
                        region_subs.append(sub)

                region_subs_csv = ",".join(region_subs)

                # Check if we already fetched this subs combo
                if region_subs_csv in query_subs_dict:
                    logger.info("\tUsing cache for region {}".format(region_coords))
                    lineage_data = query_subs_dict[region_subs_csv]
                # Otherwise, query cov-spectrum for these subs
                else:
                    query_subs_dict[region_subs_csv] = ""
                    url = lapis_url_base.format(mutations=region_subs_csv)
                    logger.info(
                        "Querying cov-spectrum for region {}".format(region_coords)
                    )
                    r = requests.get(url)
                    # Sleep after fetching
                    time.sleep(LAPIS_SLEEP_TIME)
                    result = r.json()
                    lineage_data = result["data"]
                    query_subs_dict[region_subs_csv] = lineage_data

                # Have keys be counts
                lineage_dict = {}

                for rec in lineage_data:
                    lineage = rec[LAPIS_LINEAGE_COL]

                    # Ignore None lineages
                    if not lineage:
                        continue

                    # If parent clade is not a recombinant, don't include
                    # recombinant lineages in final dict and count
                    if lineage.startswith("X") and not parent_clade_is_recombinant:
                        continue

                    count = rec["count"]
                    lineage_dict[count] = lineage

                # Sort in order
                lineage_dict = {
                    k: lineage_dict[k] for k in sorted(lineage_dict, reverse=True)
                }

                # If no matches were found, report NA for lineage
                if len(lineage_dict) == 0:
                    max_lineage = NO_DATA_CHAR
                    max_prop = NO_DATA_CHAR
                else:
                    # Temporarily set to fake data
                    total_count = sum(lineage_dict.keys())
                    max_count = max(lineage_dict.keys())
                    max_prop = max_count / total_count
                    max_lineage = lineage_dict[max_count]

                    # Don't want to report recombinants as parents
                    # UNLESS, the parental clade is a recombinant (ex. XBB)
                    while (
                        max_lineage is None
                        or max_lineage.startswith("X")
                        or max_lineage == "Unassigned"
                    ):

                        # Allow the max_lineage to be recombinant if clade is also
                        if max_lineage.startswith("X") and parent_clade_is_recombinant:
                            break
                        lineage_dict = {
                            count: lineage
                            for count, lineage in lineage_dict.items()
                            if lineage != max_lineage
                        }
                        # If there are no other options, set to NA
                        if len(lineage_dict) == 0:
                            max_lineage = NO_DATA_CHAR
                            break
                        # Otherwise try again!
                        else:
                            # For now, deliberately don't update total_count
                            max_count = max(lineage_dict.keys())
                            max_prop = max_count / total_count
                            max_lineage = lineage_dict[max_count]

                    # If we ended with an empty dictionary,
                    # there were not usable lineages
                    if len(lineage_dict) == 0:
                        max_lineage = NO_DATA_CHAR
                        max_prop = NO_DATA_CHAR

                    # Combine counts of sublineages into the max lineage total
                    # This requires the pangolin lineage tree!
                    if lineage_tree:
                        max_lineage_tree = [c for c in tree.find_clades(max_lineage)]
                        # Make sure we found this lineage in the tree
                        if len(max_lineage_tree) == 1:
                            max_lineage_tree = max_lineage_tree[0]
                            max_lineage_children = [
                                c.name for c in max_lineage_tree.find_clades()
                            ]

                            # Search for counts in the lapis data that
                            # descend from the max lineage
                            for count, lineage in lineage_dict.items():
                                if (
                                    lineage in max_lineage_children
                                    and lineage != max_lineage
                                ):
                                    max_count += count
                                    max_prop = max_count / total_count

                            # Add a "*" suffix to the max lineage, to indicate
                            # this includes descendant counts
                            max_lineage = max_lineage + "*"

                parent_lineages_sub_str = "{}|{}".format(region_subs_csv, max_lineage)

                parent_lineages.append(max_lineage)
                parent_lineages_confidence.append(max_prop)
                parent_lineages_subs.append(parent_lineages_sub_str)

            # Update the dataframe columns
            df.at[strain, "cov-spectrum_parents"] = ",".join(parent_lineages)
            df.at[strain, "cov-spectrum_parents_confidence"] = ",".join(
                str(round(c, 3)) if type(c) == float else NO_DATA_CHAR
                for c in parent_lineages_confidence
            )
            df.at[strain, "cov-spectrum_parents_subs"] = ";".join(parent_lineages_subs)

    # ---------------------------------------------------------------------
    # Identify parent conflict

    if nextclade_no_recomb and lapis and lineage_tree:

        logger.info("Identifying parental conflict between lineage and clade.")

        positive_df = df[df["sc2rf_status"] == "positive"]

        for rec in positive_df.iterrows():

            strain = rec[0]
            parent_clades = rec[1]["sc2rf_clades_filter"].split(",")
            parent_lineages = rec[1]["cov-spectrum_parents"].split(",")
            conflict = False
            lineage_is_descendant = False
            lineage_is_ancestor = False

            # Clade format can be:
            #   Lineage (BA.2.3.20)
            #   WHO_LABEL/Nextstrain clade (Delta/21J)
            #   WHO_LABEL/Lineage/Nextstrain clade (Omicron/BA.1/21K)
            #   WHO_LABEL/Lineage/Nextstrain clade (Omicron/XBB/22F)
            #   Lineage/Nextstrain clade (B.1.177/20E)

            for i, labels in enumerate(parent_clades):
                parent = NO_DATA_CHAR
                labels_split = labels.split("/")
                for label in labels_split:
                    # Need to find the lineage which contains "."
                    if "." in label:
                        parent = label
                    # Or a recombinant, which doesn't have a "."
                    elif label.startswith("X"):
                        parent = label
                parent_clades[i] = parent

            for c, l in zip(parent_clades, parent_lineages):

                # We can't compare to NA
                if c == NO_DATA_CHAR or l == NO_DATA_CHAR:
                    continue
                # Remove the asterisk indicating all descendants
                l = l.replace("*", "")
                # If they are the same, there is no conflict, continue
                if c == l:
                    continue

                # Check if parents_lineage is descendant of parents_clade
                c_nodes = [c for c in tree.find_clades(c)]

                # If the clade is not in the tree, without further evidence
                # don't report a conflict. Candidate for more testing
                if len(c_nodes) == 0:
                    continue
                else:
                    c_node = c_nodes[0]
                l_node = [c for c in c_node.find_clades(l)]
                if len(l_node) != 1:
                    lineage_is_descendant = True

                # Check if parents_lineage is ancestor of parents_clade
                l_nodes = [c for c in tree.find_clades(l)]
                # If the lineage is not in the tree, without further evidence
                # don't report a conflict. Candidate for more testing
                if len(l_nodes) == 0:
                    continue
                else:
                    l_node = l_nodes[0]
                c_node = [c for c in l_node.find_clades(c)]
                if len(c_node) != 1:
                    lineage_is_ancestor = True

                if not lineage_is_descendant and not lineage_is_ancestor:
                    conflict = True

            df.at[strain, "sc2rf_parents_conflict"] = conflict

    # ---------------------------------------------------------------------
    # Write exclude strains (false positives)

    outpath_exclude = os.path.join(outdir, prefix + ".exclude.tsv")
    logger.info("Writing strains to exclude: {}".format(outpath_exclude))
    if len(false_positives_dict) > 0:
        with open(outpath_exclude, "w") as outfile:
            for strain in false_positives_dict:
                details = ";".join(sc2rf_details_dict[strain])
                outfile.write(strain + "\t" + details + "\n")
    else:
        cmd = "touch {outpath}".format(outpath=outpath_exclude)
        os.system(cmd)

    # -------------------------------------------------------------------------
    # write output table

    # Drop old columns, if there were only negative samples, these columns don't exist
    logger.info("Formatting output columns.")
    if set(df["sc2rf_status"]) != set(["negative"]):
        df.drop(
            [
                "examples",
                "intermissions",
                "breakpoints",
                "regions",
                "unique_subs",
                "alleles",
            ],
            axis="columns",
            inplace=True,
        )

    # Move the strain column to the beginning
    df.drop(columns="strain", inplace=True)
    df.insert(loc=0, column="strain", value=df.index)
    df.rename(
        {
            "sc2rf_clades_filter": "sc2rf_parents",
            "sc2rf_regions_filter": "sc2rf_regions",
            "sc2rf_breakpoints_filter": "sc2rf_breakpoints",
            "sc2rf_num_breakpoints_filter": "sc2rf_num_breakpoints",
            "sc2rf_unique_subs_filter": "sc2rf_unique_subs",
            "sc2rf_alleles_filter": "sc2rf_alleles",
        },
        axis="columns",
        inplace=True,
    )
    # Sort by status
    df.sort_values(by=["sc2rf_status", "sc2rf_lineage"], inplace=True, ascending=False)
    outpath_rec = os.path.join(outdir, prefix + ".tsv")

    logger.info("Writing the output table: {}".format(outpath_rec))
    df.to_csv(outpath_rec, sep="\t", index=False)

    # -------------------------------------------------------------------------
    # write output strains
    outpath_strains = os.path.join(outdir, prefix + ".txt")
    strains_df = df[
        (df["sc2rf_status"] != "negative") & (df["sc2rf_status"] != "false_positive")
    ]
    strains = list(strains_df.index)
    strains_txt = "\n".join(strains)
    with open(outpath_strains, "w") as outfile:
        outfile.write(strains_txt)

    # -------------------------------------------------------------------------
    # filter the ansi output
    if ansi:

        ansi_split = ansi.split(",")
        outpath_ansi = os.path.join(outdir, prefix + ".ansi.txt")

        for i, ansi_file in enumerate(ansi_split):
            logger.info("Parsing ansi: {}".format(ansi_file))
            if len(false_positives_dict) > 0:
                cmd = (
                    "cut -f 1 "
                    + "{exclude} | grep -v -f - {inpath} {operator} {outpath}".format(
                        exclude=outpath_exclude,
                        inpath=ansi_file,
                        operator=">" if i == 0 else ">>",
                        outpath=outpath_ansi,
                    )
                )
            else:
                cmd = "cat {inpath} {operator} {outpath}".format(
                    inpath=ansi_file,
                    operator=">" if i == 0 else ">>",
                    outpath=outpath_ansi,
                )
            logger.info("Writing filtered ansi: {}".format(outpath_ansi))
            # logger.info(cmd)
            os.system(cmd)

    # -------------------------------------------------------------------------
    # write alignment
    if aligned:
        outpath_fasta = os.path.join(outdir, prefix + ".fasta")
        logger.info("Writing filtered alignment: {}".format(outpath_fasta))

        cmd = "seqkit grep -f {outpath_strains} {aligned} > {outpath_fasta};".format(
            outpath_strains=outpath_strains,
            aligned=aligned,
            outpath_fasta=outpath_fasta,
        )
        os.system(cmd)


if __name__ == "__main__":
    main()
