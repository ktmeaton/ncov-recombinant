#!/usr/bin/env python3
import click
import os
import pandas as pd
import copy
from datetime import datetime
import numpy as np
from functions import create_logger

# Hard-coded constants

NO_DATA_CHAR = "NA"

PIPELINE = "ncov-recombinant"

# Select and rename columns from summary
LINELIST_COLS = {
    "strain": "strain",
    "sc2rf_lineage": "lineage_sc2rf",
    "sc2rf_status": "status_sc2rf",
    "Nextclade_pango": "lineage_nextclade",
    "Nextclade_clade": "clade_nextclade",
    "sc2rf_parents": "parents_clade",
    "cov-spectrum_parents": "parents_lineage",
    "cov-spectrum_parents_confidence": "parents_lineage_confidence",
    "cov-spectrum_parents_subs": "parents_subs",
    "sc2rf_breakpoints": "breakpoints",
    "sc2rf_regions": "regions",
    "date": "date",
    "country": "country",
    "privateNucMutations.reversionSubstitutions": "subs_reversion",
    "privateNucMutations.unlabeledSubstitutions": "subs_unlabeled",
    "privateNucMutations.labeledSubstitutions": "subs_labeled",
    "ncov-recombinant_version": "ncov-recombinant_version",
    "nextclade_version": "nextclade_version",
    "nextclade_dataset": "nextclade_dataset",
}


@click.command()
@click.option("--input", help="Summary (tsv).", required=True)
@click.option(
    "--issues",
    help="pango-designation issues table",
    required=True,
    default="resources/issues.tsv",
)
@click.option(
    "--extra-cols",
    help="Extra columns (csv) to extract from the summary",
    required=False,
)
@click.option(
    "--outdir",
    help="Output directory for linelists",
    required=True,
)
@click.option(
    "--min-lineage-size",
    help="For lineage sizes larger than this, investigate -like status.",
    default=10,
    required=False,
)
@click.option(
    "--min-private-muts",
    help="If more than this number of private mutations, investigate -like status.",
    required=False,
    default=3,
)
@click.option("--log", help="Logfile", required=False)
def main(
    input,
    issues,
    extra_cols,
    outdir,
    log,
    min_lineage_size,
    min_private_muts,
):
    """Create a linelist and recombinant report"""

    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------

    # create logger
    logger = create_logger(logfile=log)

    # Misc variables
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # Import Summary Dataframe
    logger.info("Parsing table: {}".format(input))
    summary_df = pd.read_csv(input, sep="\t")
    summary_df.fillna(NO_DATA_CHAR, inplace=True)

    # Import Issues Summary Dataframe
    logger.info("Parsing issues: {}".format(issues))
    issues_df = pd.read_csv(issues, sep="\t")
    issues_df.fillna(NO_DATA_CHAR, inplace=True)

    # Extract columns from summary
    if extra_cols:
        for col in extra_cols.split(","):
            LINELIST_COLS[col] = col

    cols_list = list(LINELIST_COLS.keys())

    # Setup the linelist dataframe
    linelist_df = copy.deepcopy(summary_df[cols_list])
    linelist_df.rename(columns=LINELIST_COLS, inplace=True)

    # Initialize columns
    linelist_df.insert(1, "status", [NO_DATA_CHAR] * len(linelist_df))
    linelist_df.insert(2, "lineage", [NO_DATA_CHAR] * len(linelist_df))
    linelist_df.insert(3, "issue", [NO_DATA_CHAR] * len(linelist_df))
    linelist_df["privates"] = [NO_DATA_CHAR] * len(linelist_df)
    linelist_df["cov-spectrum_query"] = [NO_DATA_CHAR] * len(linelist_df)

    # -------------------------------------------------------------------------
    # Lineage Consensus
    # -------------------------------------------------------------------------

    # Use lineage calls by sc2rf and nextclade to classify recombinants status

    logger.info("Comparing lineage assignments across tools")

    for rec in linelist_df.iterrows():
        strain = rec[1]["strain"]
        status = rec[1]["status_sc2rf"]
        breakpoints = rec[1]["breakpoints"]

        issue = NO_DATA_CHAR
        is_recombinant = False
        lineage = NO_DATA_CHAR

        # ---------------------------------------------------------------------
        # Lineage Assignments (Designated)

        # Nextclade can only have one lineage assignment
        lineage_nextclade = rec[1]["lineage_nextclade"]

        # sc2rf can be multiple lineages, same breakpoint, multiple possible lineages
        lineages_sc2rf = rec[1]["lineage_sc2rf"].split(",")
        status = rec[1]["status_sc2rf"]

        # Check if sc2rf confirmed its a recombinant
        if status == "positive":
            is_recombinant = True

        # By default use nextclade
        lineage = lineage_nextclade
        classifier = "nextclade"

        # unless sc2rf found a definitive match, that is not a "proposed"
        if (
            lineages_sc2rf[0] != NO_DATA_CHAR
            and len(lineages_sc2rf) == 1
            and not lineages_sc2rf[0].startswith("proposed")
        ):
            lineage = lineages_sc2rf[0]
            classifier = "sc2rf"

        # Special Cases: XN, XP
        # As of v0.4.0, sometimes XN and XP will be detected by sc2rf, but then labeled
        # as a false positive, since all parental regions are collapsed
        parents_clade = rec[1]["parents_clade"]
        if (lineage == "XN" or lineage == "XP") and parents_clade != NO_DATA_CHAR:
            status = "positive"
            is_recombinant = True

            # If we actually found breakpoints but not sc2rf lineage, this is a "-like"
            if breakpoints != NO_DATA_CHAR and lineages_sc2rf[0] == NO_DATA_CHAR:
                lineage = lineage + "-like"

        # Special Cases: XAS
        # As of v0.4.2, XAS cannot be detected by sc2rf
        elif parents_clade == NO_DATA_CHAR and (lineage == "XAS"):
            status = "positive"
            is_recombinant = True

        # if nextclade thinks it's a recombinant but sc2rf doesn't
        elif lineage.startswith("X") and breakpoints == NO_DATA_CHAR:
            status = "false_positive"

        # if nextclade and sc2rf disagree, flag it as X*-like
        elif (
            len(lineages_sc2rf) >= 1
            and lineage.startswith("X")
            and lineage not in lineages_sc2rf
        ):
            lineage = lineage + "-like"

        # ---------------------------------------------------------------------
        # Issue

        # Identify the possible pango-designation issue this is related to
        issues = []

        for lin in set(lineages_sc2rf + [lineage_nextclade]):
            # There are two weird examples in sc2rf lineages
            # which are proposed808-1 and proposed808-2
            # because two lineages got the same issue post
            # Transform proposed808-1 to proposed808
            if lin.startswith("proposed") and "-" in lin:
                lin = lin.split("-")[0]

            if lin in list(issues_df["lineage"]):
                match = issues_df[issues_df["lineage"] == lin]
                issue = match["issue"].values[0]
                issues.append(issue)

        if len(issues) >= 1:
            issue = ",".join([str(iss) for iss in issues])
        else:
            issue = NO_DATA_CHAR

        # ---------------------------------------------------------------------
        # Private Substitutions

        privates = []

        # The private subs are only informative if we're using the nextclade lineage
        if classifier == "nextclade":
            reversions = rec[1]["subs_reversion"].split(",")
            labeled = rec[1]["subs_labeled"].split(",")
            unlabeled = rec[1]["subs_unlabeled"].split(",")

            privates_dict = {}

            for sub in reversions + labeled + unlabeled:
                if sub == NO_DATA_CHAR:
                    continue
                # Labeled subs have special formatting
                if "|" in sub:
                    sub = sub.split("|")[0]
                coord = int(sub[1:-1])
                privates_dict[coord] = sub

            # Convert back to sorted list
            for coord in sorted(privates_dict):
                sub = privates_dict[coord]
                privates.append(sub)

        # ---------------------------------------------------------------------
        # Status

        # Fine-tune the status of a positive recombinant
        if is_recombinant:
            if lineage.startswith("X") and not lineage.endswith("like"):
                status = "designated"
            elif issue != NO_DATA_CHAR:
                status = "proposed"
            else:
                status = "unpublished"

        # ---------------------------------------------------------------------
        # Update Dataframe

        linelist_df.at[rec[0], "lineage"] = lineage
        linelist_df.at[rec[0], "status"] = str(status)
        linelist_df.at[rec[0], "issue"] = str(issue)
        linelist_df.at[rec[0], "privates"] = privates

    # -------------------------------------------------------------------------
    # Lineage Assignment (Undesignated)
    # -------------------------------------------------------------------------

    # Group sequences into potential lineages that have a unique combination of
    #   1. Lineage
    #   2. Parent clades (sc2rf)
    #   3. Parent lineages (sc2rf, lapis cov-spectrum)
    #   4. Breakpoints (sc2rf)
    #   5. Private substitutions (nextclade)

    logger.info("Grouping sequences into lineages.")

    # Create a dictionary of recombinant lineages seen
    rec_seen = {}
    seen_i = 0

    for rec in linelist_df.iterrows():

        strain = rec[1]["strain"]
        status = rec[1]["status"]

        if status == "negative" or status == "false_positive":
            continue

        # 1. Lineage assignment (nextclade or sc2rf)
        # 2. Parents by clade (ex. 21K,21L)
        # 3. Parents by lineage (ex. BA.1.1,BA.2.3)
        # 4. Breakpoints
        lineage = rec[1]["lineage"]
        parents_clade = rec[1]["parents_clade"]
        parents_lineage = rec[1]["parents_lineage"]
        breakpoints = rec[1]["breakpoints"]
        privates = rec[1]["privates"]

        # Format substitutions into a tidy list
        # "C234T,A54354G|Omicron/BA.1/21K;A423T|Omicron/BA.2/21L"
        parents_subs_raw = rec[1]["parents_subs"].split(";")
        # ["C234T,A54354G|Omicron/BA.1/21K", "A423T|Omicron/BA.2/21L"]
        parents_subs_csv = [sub.split("|")[0] for sub in parents_subs_raw]
        # ["C234T,A54354G", "A423T"]
        parents_subs_str = ",".join(parents_subs_csv)
        # "C234T,A54354G,A423T"
        parents_subs_list = parents_subs_str.split(",")
        # ["C234T","A54354G","A423T"]

        match = None

        for i in rec_seen:
            rec_lin = rec_seen[i]
            # lineage, parents, breakpoints, and subs have to match
            if (
                rec_lin["lineage"] == lineage
                and rec_lin["parents_clade"] == parents_clade
                and rec_lin["parents_lineage"] == parents_lineage
                and rec_lin["breakpoints"] == breakpoints
            ):
                match = i
                break

        # If we found a match, increment our dict
        if match is not None:
            # Add the strain to this lineage
            rec_seen[match]["strains"].append(strain)

            # Adjust the cov-spectrum subs /parents subs to include the new strain
            lineage_parents_subs = rec_seen[match]["cov-spectrum_query"]
            for sub in lineage_parents_subs:
                if sub not in parents_subs_list:
                    rec_seen[match]["cov-spectrum_query"].remove(sub)

            # Adjust the private subs to include the new strain
            lineage_private_subs = rec_seen[match]["privates"]
            for sub in lineage_private_subs:
                if sub not in privates:
                    rec_seen[match]["privates"].remove(sub)

        # This is the first appearance
        else:
            rec_seen[seen_i] = {
                "lineage": lineage,
                "breakpoints": breakpoints,
                "parents_clade": parents_clade,
                "parents_lineage": parents_lineage,
                "strains": [strain],
                "cov-spectrum_query": parents_subs_list,
                "privates": privates,
            }
            seen_i += 1

    # -------------------------------------------------------------------------
    # Cluster ID
    # Assign an id to each lineage based on the first sequence collected

    logger.info("Assigning cluster IDs to lineages.")

    linelist_df["cluster_id"] = [NO_DATA_CHAR] * len(linelist_df)
    linelist_df["cluster_privates"] = [NO_DATA_CHAR] * len(linelist_df)

    for i in rec_seen:
        earliest_datetime = datetime.today()
        earliest_strain = None

        rec_strains = rec_seen[i]["strains"]
        rec_privates = rec_seen[i]["privates"]
        rec_df = linelist_df[linelist_df["strain"].isin(rec_strains)]

        earliest_datetime = min(rec_df["date"])
        earliest_strain = rec_df[rec_df["date"] == earliest_datetime]["strain"].values[
            0
        ]
        subs_query = rec_seen[i]["cov-spectrum_query"]
        if subs_query != NO_DATA_CHAR:
            subs_query = ",".join(subs_query)

        # indices are preserved from the original linelist_df
        for strain in rec_strains:
            strain_i = rec_df[rec_df["strain"] == strain].index[0]
            linelist_df.loc[strain_i, "cluster_id"] = earliest_strain
            linelist_df.loc[strain_i, "cluster_privates"] = rec_privates
            linelist_df.loc[strain_i, "cov-spectrum_query"] = subs_query

    # -------------------------------------------------------------------------
    # Mimics

    logger.info("Checking for mimics with too many private mutations.")
    # Check for designated lineages that have too many private mutations
    # This may indicate this is a novel lineage
    for i in rec_seen:
        lineage = rec_seen[i]["lineage"]
        rec_strains = rec_seen[i]["strains"]
        lineage_size = len(rec_strains)
        num_privates = len(rec_seen[i]["privates"])

        # Mark these lineages as "X*-like"
        if (
            lineage.startswith("X")
            and not lineage.endswith("like")
            and lineage_size >= min_lineage_size
            and num_privates >= min_private_muts
        ):
            lineage = lineage + "-like"
            rec_rename = linelist_df["strain"].isin(rec_strains)
            linelist_df.loc[rec_rename, "lineage"] = lineage
            linelist_df.loc[rec_rename, "status"] = "proposed"

    # -------------------------------------------------------------------------
    # Assign status and curated lineage

    logger.info("Assigning curated recombinant lineages.")

    for rec in linelist_df.iterrows():
        lineage = rec[1]["lineage"]
        status = rec[1]["status"]
        cluster_id = rec[1]["cluster_id"]

        # By default use cluster ID for curated lineage
        linelist_df.at[rec[0], "recombinant_lineage_curated"] = cluster_id

        if status == "negative":
            linelist_df.at[rec[0], "recombinant_lineage_curated"] = "negative"

        elif status == "false_positive":
            linelist_df.at[rec[0], "recombinant_lineage_curated"] = "false_positive"

        # If designated or "-like", override with actual lineage
        elif status == "designated" or lineage.endswith("like"):
            linelist_df.at[rec[0], "recombinant_lineage_curated"] = lineage

    # -------------------------------------------------------------------------
    # Pipeline Versions
    logger.info("Recording pipeline versions.")

    pipeline_ver = linelist_df["ncov-recombinant_version"].values[0]
    linelist_df.loc[linelist_df.index, "pipeline_version"] = "{pipeline}".format(
        pipeline="ncov-recombinant:{}".format(pipeline_ver)
    )
    nextclade_ver = linelist_df["nextclade_version"].values[0]
    nextclade_dataset = linelist_df["nextclade_dataset"].values[0]
    linelist_df.loc[
        linelist_df.index, "recombinant_classifier_dataset"
    ] = "{nextclade}:{dataset}".format(
        nextclade="nextclade:{}".format(nextclade_ver),
        dataset=nextclade_dataset,
    )

    # -------------------------------------------------------------------------
    # Save to File

    logger.info("Sorting output tables.")

    # Drop Unnecessary columns
    linelist_df.drop(
        columns=[
            "status_sc2rf",
            "clade_nextclade",
            "subs_reversion",
            "subs_labeled",
            "subs_unlabeled",
        ],
        inplace=True,
    )

    # Convert privates from list to csv
    linelist_df["privates"] = [",".join(p) for p in linelist_df["privates"]]
    linelist_df["cluster_privates"] = [
        ",".join(p) for p in linelist_df["cluster_privates"]
    ]

    # Recode NA
    linelist_df.fillna(NO_DATA_CHAR, inplace=True)

    # Sort
    status_order = {
        "designated": 0,
        "proposed": 1,
        "unpublished": 2,
        "false_positive": 3,
        "negative": 4,
    }

    # Change empty cells to NaN so they'll be sorted to the end
    linelist_df = linelist_df.replace({"lineage": "", "status": ""}, np.nan)
    linelist_df.sort_values(
        [
            "status",
            "lineage",
        ],
        inplace=True,
        key=lambda x: x.map(status_order),
    )

    # All
    outpath = os.path.join(outdir, "linelist.tsv")
    logger.info("Writing output: {}".format(outpath))
    linelist_df.to_csv(outpath, sep="\t", index=False)

    # Positives
    positive_df = linelist_df[
        (linelist_df["status"] != "false_positive")
        & (linelist_df["status"] != "negative")
    ]
    outpath = os.path.join(outdir, "positives.tsv")
    logger.info("Writing output: {}".format(outpath))
    positive_df.to_csv(outpath, sep="\t", index=False)

    # False Positives
    false_positive_df = linelist_df[linelist_df["status"] == "false_positive"]
    outpath = os.path.join(outdir, "false_positives.tsv")
    logger.info("Writing output: {}".format(outpath))
    false_positive_df.to_csv(outpath, sep="\t", index=False)

    # Negatives
    negative_df = linelist_df[linelist_df["status"] == "negative"]
    outpath = os.path.join(outdir, "negatives.tsv")
    logger.info("Writing output: {}".format(outpath))
    negative_df.to_csv(outpath, sep="\t", index=False)


if __name__ == "__main__":
    main()
