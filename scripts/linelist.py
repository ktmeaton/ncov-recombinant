#!/usr/bin/env python3
import click
import os
import pandas as pd
import copy
from datetime import datetime
import numpy as np

# Hard-coded constants

NO_DATA_CHAR = "NA"

PIPELINE = "ncov-recombinant"
CLASSIFIER = "UShER"

# Select and rename columns from summary
LINELIST_COLS = {
    "strain": "strain",
    "usher_pango_lineage_map": "lineage_usher",
    "sc2rf_lineage": "lineage_sc2rf",
    "sc2rf_status": "status_sc2rf",   
    "Nextclade_pango": "lineage_nextclade",
    "sc2rf_parents": "parents",
    "sc2rf_breakpoints": "breakpoints",
    "usher_num_best": "placements",
    "usher_subtree": "subtree",
    "sc2rf_regions": "regions",
    "date": "date",
    "country": "country",
    "ncov-recombinant_version": "recombinant_pipeline",
    "usher_version": "recombinant_classifier",
    "usher_dataset": "recombinant_classifier_dataset",
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
    "--max-placements",
    help="Maximum number of UShER placements before labeling false_positive",
    required=False,
    default=-1,
)
@click.option(
    "--outdir",
    help="Output directory for linelists",
    required=True,
)
def main(
    input,
    issues,
    extra_cols,
    max_placements,
    outdir,
):
    """Create a linelist and recombinant report"""

    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------

    # Misc variables
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # Import Summary Dataframe
    summary_df = pd.read_csv(input, sep="\t")
    summary_df.fillna(NO_DATA_CHAR, inplace=True)

    # Import Issues Summary Dataframe
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
    # Lineage Status
    # Use lineage calls by UShER and sc2rf to classify recombinants status

    # Initialize columns
    linelist_df.insert(1, "status", [NO_DATA_CHAR] * len(linelist_df))
    linelist_df.insert(3, "issue", [NO_DATA_CHAR] * len(linelist_df))

    for rec in linelist_df.iterrows():
        lineage = NO_DATA_CHAR
        issue = NO_DATA_CHAR
        is_recombinant = False

        # sc2rf can have multiple lineages, because different lineages
        # can have the same breakpoint
        lineages_sc2rf = rec[1]["lineage_sc2rf"].split(",")
        status_sc2rf = rec[1]["status_sc2rf"]
        breakpoints = rec[1]["breakpoints"]
        lineage_usher = rec[1]["lineage_usher"]
        usher_placements = rec[1]["placements"]

        # Check if sc2rf or UShER thinks its a recombinant
        if breakpoints != NO_DATA_CHAR and status_sc2rf[0] != "false_positive" and status_sc2rf[0] != "negative":
            is_recombinant = True

        if (
            lineage_usher.startswith("X")
            or lineage_usher.startswith("proposed")
            or lineage_usher.startswith("misc")
        ):
            is_recombinant = True

        # Use UShER as the definitive lineage caller
        lineage = lineage_usher

        # Try to get find a related pango-designation by lineage name
        # This will work for designated (X*) or proposed UShER lineages
        if lineage in list(issues_df["lineage"]):
            match = issues_df[issues_df["lineage"] == lineage]
            issue = match["issue"].values[0]

            # if there are no breakpoints, this was a nextclade recombinant
            # that auto-passed sc2rf. Use breakpoints in issues table
            if breakpoints == NO_DATA_CHAR:
                breakpoints = match["breakpoints_curated"].values[0]
                linelist_df.at[rec[0], "breakpoints"] = breakpoints
                parents = match["parents_curated"].values[0]
                linelist_df.at[rec[0], "parents"] = parents

                # TBD: regions if desired

            linelist_df.at[rec[0], "issue"] = issue

        # Alternatively, try to find related pango-designation issues by breakpoint
        # Multiple matches are possible here
        else:
            issues = []
            for lin in lineages_sc2rf:
                # ex. proposed517 is issue 517
                if lin.startswith("proposed"):
                    issue = lin.replace("proposed", "")
                    issues.append(issue)

            if len(issues) > 1:
                issue = ",".join(issues)

        # Add status
        status = "unpublished"

        # Positive recombinants
        if lineage.startswith("X"):
            status = "designated"

        elif issue != NO_DATA_CHAR:
            status = "proposed"

        # Negatives recombinants
        if status_sc2rf == "negative":
            status = "negative"

        # False Positives recombinants        
        elif max_placements != -1 and usher_placements > max_placements:
            status = "false_positive"

        elif not is_recombinant:
            status = "false_positive"


        linelist_df.at[rec[0], "status"] = str(status)
        linelist_df.at[rec[0], "issue"] = issue
      

    # -------------------------------------------------------------------------
    # Lineage Grouping
    # Group sequences into lineages by:
    #   - Lineage
    #   - Parents
    #   - Breakpoints OR Phylogenetic placement (subtree)

    # Different recombinant types can have the same breakpoint
    # but different placement: ex. XE and XH

    # Create a dictionary of recombinant lineages seen
    rec_seen = {}
    seen_i = 0

    for rec in linelist_df.iterrows():
        strain = rec[1]["strain"]
        lineage = rec[1]["lineage_usher"]
        parents = rec[1]["parents"]
        breakpoints = rec[1]["breakpoints"]
        subtree = rec[1]["subtree"]
        match = None

        for i in rec_seen:
            rec_lin = rec_seen[i]
            # lineage and parents have to match
            # one of bp or subtree has to match
            if (
                rec_lin["lineage"] == lineage
                and rec_lin["parents"] == parents
                and (
                    rec_lin["breakpoints"] == breakpoints
                    or rec_lin["subtree"] == subtree
                )
            ):
                match = i
                break

        # If we found a match, increment our dict
        if match is not None:
            rec_seen[match]["strains"].append(strain)
        else:
            rec_seen[seen_i] = {
                "lineage": lineage,
                "breakpoints": breakpoints,
                "parents": parents,
                "subtree": subtree,
                "strains": [strain],
            }
            seen_i += 1

    # -------------------------------------------------------------------------
    # Lineage ID
    # Assign an id to each lineage based on the first sequence collected
    linelist_df["cluster_id"] = [NO_DATA_CHAR] * len(linelist_df)

    for i in rec_seen:
        earliest_datetime = datetime.today()
        earliest_strain = None

        for strain in rec_seen[i]["strains"]:
            strain_date = linelist_df[linelist_df["strain"] == strain]["date"].values[0]
            strain_datetime = datetime.strptime(strain_date, "%Y-%m-%d")
            if strain_datetime <= earliest_datetime:
                earliest_datetime = strain_datetime
                earliest_strain = strain

        for strain in rec_seen[i]["strains"]:
            strain_i = linelist_df[linelist_df["strain"] == strain].index[0]
            linelist_df.at[strain_i, "cluster_id"] = earliest_strain

    # -------------------------------------------------------------------------
    # Assign status and curated lineage

    recombinant_lineage = []
    for rec in linelist_df.iterrows():
        lineage = rec[1]["lineage_usher"]
        status = rec[1]["status"]
        cluster_id = rec[1]["cluster_id"]

        # By default use cluster ID for curated lineage
        linelist_df.at[rec[0], "recombinant_lineage_curated"] = cluster_id

        if status == "negative":
            linelist_df.at[rec[0], "recombinant_lineage_curated"] = "negative"

        # If designated, override with actual lineage
        if status == "designated":
            recombinant_lineage.append(lineage)
            linelist_df.at[rec[0], "recombinant_lineage_curated"] = lineage

        elif status == "proposed":
            recombinant_lineage.append("proposed_recombinant")

        elif status == "false_positive":
            recombinant_lineage.append("false_positive_recombinant")

        else:
            recombinant_lineage.append("unpublished_recombinant")

    # -------------------------------------------------------------------------
    # Pipeline Versions
    pipeline_ver = linelist_df["recombinant_pipeline"].values[0]
    linelist_df.loc[linelist_df.index, "recombinant_pipeline"] = "{}-{}".format(
        PIPELINE, pipeline_ver
    )
    classifer_ver = linelist_df["recombinant_classifier"].values[0]
    linelist_df.loc[linelist_df.index, "recombinant_classifier"] = "{}-{}".format(
        CLASSIFIER, classifer_ver
    )

    # -------------------------------------------------------------------------
    # Save to File

    # Drop Unnecessary columns
    linelist_df.drop(columns=["lineage_sc2rf", "lineage_nextclade", "status_sc2rf"], inplace=True)
    linelist_df.rename(columns={"lineage_usher": "lineage"}, inplace=True)

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
    linelist_df.to_csv(outpath, sep="\t", index=False)     

    # Positives
    positive_df = linelist_df[
        (linelist_df["status"] != "false_positive")
        & (linelist_df["status"] != "negative")]
    outpath = os.path.join(outdir, "positives.tsv")
    positive_df.to_csv(outpath, sep="\t", index=False)    

    # False Positives
    false_positive_df = linelist_df[linelist_df["status"] == "false_positive"]
    outpath = os.path.join(outdir, "false_positives.tsv")
    false_positive_df.to_csv(outpath, sep="\t", index=False)

    # Negatives
    negative_df = linelist_df[linelist_df["status"] == "negative"]
    outpath = os.path.join(outdir, "negatives.tsv")
    negative_df.to_csv(outpath, sep="\t", index=False)


if __name__ == "__main__":
    main()
