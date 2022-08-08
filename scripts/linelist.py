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
    "ncov-recombinant_version": "ncov-recombinant_version",
    "nextclade_version": "nextclade_version",
    "sc2rf_version": "sc2rf_version",
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
@click.option("--log", help="Logfile", required=False)
def main(
    input,
    issues,
    extra_cols,
    outdir,
    log,
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

    # -------------------------------------------------------------------------
    # Create the linelist (linelist.tsv)
    # -------------------------------------------------------------------------

    linelist_df = copy.deepcopy(summary_df[cols_list])
    linelist_df.rename(columns=LINELIST_COLS, inplace=True)

    # -------------------------------------------------------------------------
    # Lineage Consensus
    # Use lineage calls by sc2rf and nextclade to classify recombinants status

    logger.info("Comparing lineage assignments across tools")

    # Initialize columns
    linelist_df.insert(1, "status", [NO_DATA_CHAR] * len(linelist_df))
    linelist_df.insert(2, "lineage", [NO_DATA_CHAR] * len(linelist_df))
    linelist_df.insert(3, "issue", [NO_DATA_CHAR] * len(linelist_df))
    linelist_df["cov-spectrum_query"] = [NO_DATA_CHAR] * len(linelist_df)

    for rec in linelist_df.iterrows():
        strain = rec[1]["strain"]
        issue = NO_DATA_CHAR
        is_recombinant = False
        lineage = NO_DATA_CHAR

        # Nextclade can only have one lineage assignment, typically this
        # will be the "majority" parent
        lineage_nextclade = rec[1]["lineage_nextclade"]

        # sc2rf can have multiple lineages, because different lineages
        # can have the same breakpoint
        lineages_sc2rf = rec[1]["lineage_sc2rf"].split(",")
        status_sc2rf = rec[1]["status_sc2rf"]
        breakpoints = rec[1]["breakpoints"]

        # Check if sc2rf confirmed its a recombinant
        if status_sc2rf == "positive":
            is_recombinant = True

        # If sc2rf couldn't find a definitive match, use nextclade
        if lineages_sc2rf[0] == NO_DATA_CHAR or len(lineages_sc2rf) > 1:
            lineage = lineage_nextclade

        # Otherwise use the sc2rf lineage match
        else:
            lineage = lineages_sc2rf[0]

        # Try to get find a related pango-designation by lineage name
        # This will work for designated (X*) lineages
        if lineage in list(issues_df["lineage"]):
            match = issues_df[issues_df["lineage"] == lineage]
            issue = match["issue"].values[0]
            linelist_df.at[rec[0], "issue"] = str(issue)

        # Alternatively, try to find related pango-designation issues by breakpoint
        # This will work for proposed* lineages.
        else:
            issues = []
            for lin in lineages_sc2rf:
                # ex. proposed517 is issue 517
                if lin.startswith("proposed"):
                    issue = lin.replace("proposed", "")
                    issues.append(issue)

            if len(issues) > 1:
                issue = ",".join(issues)

        # Special Cases: XN, XP
        # As of v0.4.0, XN and XP will be detected by sc2rf, but then labeled
        # as a false positive, since all parental regions are collapsed
        parents_clade = rec[1]["parents_clade"]
        if (lineage == "XN" or lineage == "XP") and parents_clade != NO_DATA_CHAR:
            status_sc2rf = "positive"
            is_recombinant = True

        # Fine-tune positive status
        status = status_sc2rf
        if is_recombinant:
            if lineage.startswith("X"):
                status = "designated"
            elif lineage.startswith("proposed") or issue != NO_DATA_CHAR:
                status = "proposed"
            else:
                status = "unpublished"

        # Update the database values
        linelist_df.at[rec[0], "lineage"] = lineage
        linelist_df.at[rec[0], "status"] = str(status)
        linelist_df.at[rec[0], "issue"] = str(issue)

    # -------------------------------------------------------------------------
    # Lineage Grouping
    # Group sequences into lineages that have a unique combination of
    #   1. Lineage
    #   2. Parent clades (sc2rf)
    #   3. Parent lineages (sc2rf, lapis cov-spectrum)
    #   4. Breakpoints (sc2rf)

    logger.info("Defining recombinant lineages")

    # Create a dictionary of recombinant lineages seen
    rec_seen = {}
    seen_i = 0

    for rec in linelist_df.iterrows():
        strain = rec[1]["strain"]

        status = rec[1]["status"]

        if status == "negative" or status == "false_positive":
            continue

        # 1. Lineage assignment (nextclade or sc2rf)
        lineage = rec[1]["lineage"]

        # 2. Parents by clade (ex. 21K,21L)
        parents_clade = rec[1]["parents_clade"]

        # 3. Parents by lineage (ex. BA.1.1,BA.2.3)
        parents_lineage = rec[1]["parents_lineage"]

        # 4. Breakpoints
        breakpoints = rec[1]["breakpoints"]

        # Format: "C234T,A54354G|Omicron/BA.1/21K;A423T|Omicron/BA.2/21L"
        parents_subs_raw = rec[1]["parents_subs"].split(";")
        # Format: ["C234T,A54354G|Omicron/BA.1/21K", "A423T|Omicron/BA.2/21L"]
        parents_subs_csv = [sub.split("|")[0] for sub in parents_subs_raw]
        # Format: ["C234T,A54354G", "A423T"]
        parents_subs_str = ",".join(parents_subs_csv)
        # Format: "C234T,A54354G,A423T"
        parents_subs_list = parents_subs_str.split(",")
        # Format: ["C234T","A54354G","A423T"]

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
                if sub not in lineage_parents_subs:
                    rec_seen[match]["cov-spectrum_query"].remove(sub)

        # This is the first appearance
        else:
            rec_seen[seen_i] = {
                "lineage": lineage,
                "breakpoints": breakpoints,
                "parents_clade": parents_clade,
                "parents_lineage": parents_lineage,
                "strains": [strain],
                "cov-spectrum_query": parents_subs_list,
            }
            seen_i += 1

    for i in rec_seen:
        if rec_seen[i]["breakpoints"] == NO_DATA_CHAR:
            continue

    # -------------------------------------------------------------------------
    # Lineage ID
    # Assign an id to each lineage based on the first sequence collected

    logger.info("Assigning cluster IDs to recombinant lineages")

    linelist_df["cluster_id"] = [NO_DATA_CHAR] * len(linelist_df)

    for i in rec_seen:
        earliest_datetime = datetime.today()
        earliest_strain = None

        rec_strains = rec_seen[i]["strains"]
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
            linelist_df.loc[strain_i, "cov-spectrum_query"] = subs_query

    # -------------------------------------------------------------------------
    # Assign status and curated lineage

    logger.info("Assigning a curated recombinant lineage")

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

        # If designated, override with actual lineage
        elif status == "designated":
            linelist_df.at[rec[0], "recombinant_lineage_curated"] = lineage

        # If proposed and the lineage is actually proposed*, override
        elif status == "proposed" and lineage.startswith("proposed"):
            linelist_df.at[rec[0], "recombinant_lineage_curated"] = lineage

    # -------------------------------------------------------------------------
    # Pipeline Versions
    logger.info("Recording pipeline versions")

    pipeline_ver = linelist_df["ncov-recombinant_version"].values[0]
    linelist_df.loc[linelist_df.index, "pipeline_version"] = "{pipeline}".format(
        pipeline="ncov-recombinant:{}".format(pipeline_ver)
    )
    nextclade_ver = linelist_df["nextclade_version"].values[0]
    sc2rf_ver = linelist_df["nextclade_version"].values[0]
    linelist_df.loc[
        linelist_df.index, "recombinant_classifier"
    ] = "{nextclade}-{sc2rf}".format(
        nextclade="nextclade:{}".format(nextclade_ver),
        sc2rf="nextclade:{}".format(sc2rf_ver),
    )

    # -------------------------------------------------------------------------
    # Save to File

    logger.info("Sorting output tables.")

    # Drop Unnecessary columns
    linelist_df.drop(
        columns=[
            "status_sc2rf",
            "clade_nextclade",
            "privateNucMutations.reversionSubstitutions",
            "privateNucMutations.labeledSubstitutions",
            "privateNucMutations.reversionSubstitutions",
        ],
        inplace=True,
    )

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
