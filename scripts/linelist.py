#!/usr/bin/env python3
import click
import os
import pandas as pd
import copy
from datetime import datetime

# Hard-coded constants

NO_DATA_CHAR = "NA"

PIPELINE = "ncov-recombinant"
CLASSIFIER = "UShER"

# Select and rename columns from summary
LINELIST_COLS = {
    "strain": "strain",
    "usher_pango_lineage_map": "lineage_usher",
    "sc2rf_lineage": "lineage_sc2rf",
    "Nextclade_pango": "lineage_nextclade",
    "sc2rf_parents": "parents",
    "sc2rf_breakpoints": "breakpoints",
    "usher_subtree": "subtree",
    "sc2rf_regions": "regions",
    "date": "date",
    "country": "country",
    "ncov-recombinant_version": "recombinant_pipeline",
    "usher_version": "recombinant_classifier",
    "usher_dataset": "recombinant_classifier_dataset",
}


@click.command()
@click.option("--summary", help="Summary (tsv).", required=True)
@click.option(
    "--issues",
    help="Reporting years (csv)",
    required=True,
    default="resources/issues.tsv",
)
@click.option("--prev-linelist", help="Previous linelist", required=False)
@click.option(
    "--extra-cols",
    help="Extra columns (CSV) to extract from the summary",
    required=False,
)
def main(
    summary,
    issues,
    prev_linelist,
    extra_cols,
):
    """Create a linelist and recombinant report"""

    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------

    # Misc variables
    outdir = os.path.dirname(summary)

    # Import Summary Dataframe
    summary_df = pd.read_csv(summary, sep="\t")
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
        breakpoints = rec[1]["breakpoints"]
        lineage_usher = rec[1]["lineage_usher"]

        # Check if sc2rf or UShER thinks its a recombinant
        if breakpoints != NO_DATA_CHAR and lineages_sc2rf[0] != "false_positive":
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

        linelist_df.at[rec[0], "issue"] = str(issue)

        # Add status
        status = "unpublished"
        if lineage.startswith("X"):
            status = "designated"
        elif not is_recombinant:
            status = "false_positive"
        elif issue != NO_DATA_CHAR:
            status = "proposed"
        linelist_df.at[rec[0], "status"] = str(status)

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
    # Pipeline Versions
    pipeline_ver = linelist_df["recombinant_pipeline"].values[0]
    linelist_df.loc[linelist_df.index, "recombinant_pipeline"] = "{}-{}".format(
        PIPELINE, pipeline_ver
    )
    classifer_ver = linelist_df["recombinant_classifier"].values[0]
    linelist_df.loc[linelist_df.index, "recombinant_classifier"] = "{}-{}".format(
        CLASSIFIER, classifer_ver
    )
    # Edit recombinant lineage
    recombinant_lineage = []
    for lineage, status in zip(linelist_df["lineage_usher"], linelist_df["status"]):
        if status == "designated":
            recombinant_lineage.append(lineage)
        elif status == "proposed":
            recombinant_lineage.append("proposed_recombinant")
        elif status == "false_positive":
            recombinant_lineage.append("false_positive_recombinant")
        else:
            recombinant_lineage.append("unpublished_recombinant")

    linelist_df["recombinant_lineage_curated"] = recombinant_lineage

    # Drop false_positive recombinants
    linelist_df = linelist_df[linelist_df["status"] != "false_positive"]

    # -------------------------------------------------------------------------
    # Save to File

    # Drop Unnecessary columns
    linelist_df.drop(columns=["lineage_sc2rf", "lineage_nextclade"], inplace=True)
    linelist_df.rename(columns={"lineage_usher": "lineage"}, inplace=True)

    # Recode NA
    linelist_df.fillna(NO_DATA_CHAR, inplace=True)

    outpath = os.path.join(outdir, "linelist.tsv")
    linelist_df.to_csv(outpath, sep="\t", index=False)


if __name__ == "__main__":
    main()
