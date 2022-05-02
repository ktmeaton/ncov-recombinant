#!/usr/bin/env python3
import click
import os
import pandas as pd
import copy
import re

# Hard-coded constants

NO_DATA_CHAR = "NA"

# Concise names for report.md
CLADES_RENAME = {
    "Alpha/B.1.1.7/20I": "Alpha",
    "Delta/21I": "Delta (21I)",
    "Delta/21J": "Delta (21J)",
    "Omicron/BA.1/21K": "BA.1",
    "Omicron/BA.2/21L": "BA.2",
}
PANGO_ISSUES_URL = "https://github.com/cov-lineages/pango-designation/issues/"

# designated: X*
# proposed: proposed* or associated issue
# unpublished: not designated or proposed

RECOMBINANT_STATUS = ["designated", "proposed", "unpublished"]

PIPELINE = "ncov-recombinant"
CLASSIFIER = "UShER"

# Select and rename columns from summary
LINELIST_COLS = {
    "strain": "strain",
    "usher_pango_lineage_map": "lineage_usher",
    "sc2rf_lineage": "lineage_sc2rf",
    "Nextclade_pango": "lineage_nextclade",
    "sc2rf_clades_filter": "parents",
    "sc2rf_breakpoints_regions_filter": "breakpoints",
    "usher_subtree": "subtree",
    "sc2rf_clades_regions_filter": "regions",
    "date": "date",
    "country": "country",
    "ncov-recombinant_version": "pipeline",
    "usher_version": "classifier",
    "usher_dataset": "classifier_dataset",
}

# Select and rename columns from linelist
RECOMBINANTS_COLS = [
    "status",  # excluded from report.md
    "lineage",
    "issue",
    "parents",
    "breakpoints",
    "subtree",
    "sequences",
    "sequences_int",  # excluded from report.md
    "earliest_date",
    "latest_date",
    "year",  # excluded from report.md
]


@click.command()
@click.option("--summary", help="Summary (tsv).", required=True)
@click.option(
    "--years", help="Reporting years (csv)", required=True, default="2022,2021"
)
@click.option(
    "--issues",
    help="Reporting years (csv)",
    required=True,
    default="resources/issues.tsv",
)
@click.option("--prev-linelist", help="Previous linelist", required=False)
@click.option("--changelog", help="Markdown changelog", required=False)
@click.option(
    "--extra-cols",
    help="Extra columns (CSV) to extract from the summary",
    required=False,
)
def main(
    summary,
    years,
    issues,
    prev_linelist,
    changelog,
    extra_cols,
):
    """Create a linelist and recombinant report"""

    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------

    # Misc variables
    years_list = [int(y) for y in years.split(",")]
    outdir = os.path.dirname(summary)

    # Import Summary Dataframe
    summary_df = pd.read_csv(summary, sep="\t")
    summary_df.fillna(NO_DATA_CHAR, inplace=True)

    # Import Issues Summary Dataframe
    issues_df = pd.read_csv(issues, sep="\t")

    # Extract columns from summary
    if extra_cols:
        for col in extra_cols.split(","):
            LINELIST_COLS[col] = col

    cols_list = list(LINELIST_COLS.keys())

    # -------------------------------------------------------------------------
    # Program Versions

    ver_cols = [col for col in summary_df if "ver" in col or "dataset" in col]
    ver_cols.sort()
    ver_vals = list(summary_df[ver_cols].iloc[0].values)
    ver_dict = {
        "program": [c.replace("_version", "") for c in ver_cols],
        "version": ver_vals,
    }
    ver_df = pd.DataFrame(ver_dict)

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

        # sc2rf can have multiple lineages, because different lineages
        # can have the same breakpoint
        lineages_sc2rf = rec[1]["lineage_sc2rf"].split(",")
        lineage_usher = rec[1]["lineage_usher"]

        # Use UShER
        lineage = lineage_usher

        # Try to get find a related pango-designation by lineage name
        # This will work for designated (X*) or proposed UShER lineages
        if lineage in list(issues_df["lineage"]):
            match = issues_df[issues_df["lineage"] == lineage]
            issue = match["issue"].values[0]

        # Alternatively, try to find related pango-designation issues by breakpoint
        # Multiple matches are possible here
        # I would need to manually add the parent regions to issues to improve that look up
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
        elif issue != NO_DATA_CHAR:
            status = "proposed"
        linelist_df.at[rec[0], "status"] = str(status)

    # Edit pipeline versions
    pipeline_ver = linelist_df["pipeline"].values[0]
    linelist_df.loc[linelist_df.index, "pipeline"] = "{}-{}".format(
        PIPELINE, pipeline_ver
    )
    classifer_ver = linelist_df["classifier"].values[0]
    linelist_df.loc[linelist_df.index, "classifier"] = "{}-{}".format(
        CLASSIFIER, classifer_ver
    )

    # -------------------------------------------------------------------------
    # Identify new samples

    if prev_linelist:

        # Read in the old linelist
        prev_linelist_df = pd.read_csv(prev_linelist, sep="\t")

        # Use first column as the ID column to match up records
        prev_id_col = prev_linelist_df.columns[0]
        id_col = linelist_df.columns[0]

        prev_samples = list(prev_linelist_df[prev_id_col])
        current_samples = list(linelist_df[id_col])

        # Add "new" column
        new_samples = []
        for s in current_samples:
            if s not in prev_samples:
                new_samples.append("yes")
            else:
                new_samples.append("no")
        linelist_df["new"] = new_samples

    # Drop Unnecessary columns
    linelist_df.drop(columns=["lineage_sc2rf", "lineage_nextclade"], inplace=True)
    linelist_df.rename(columns={"lineage_usher": "lineage"}, inplace=True)

    # -------------------------------------------------------------------------
    # Save to File

    outpath = os.path.join(outdir, "linelist.tsv")
    linelist_df.to_csv(outpath, sep="\t", index=False)

    # -------------------------------------------------------------------------
    # Create the recombinants table (recombinants.tsv)
    # -------------------------------------------------------------------------

    # Add datetime fields to the base dataframe (linelist)
    linelist_df["datetime"] = pd.to_datetime(linelist_df["date"], format="%Y-%m-%d")
    linelist_df["year"] = [d.year for d in linelist_df["datetime"]]

    # Define a recombinant by the intersection of:
    #   - Breakpoints
    #   - subtree # (Phylogenetic placement)

    # Different recombinant types can have the same breakpoint
    # but different placement: ex. XE and XH

    seen = []
    recombinants_data = {col: [] for col in RECOMBINANTS_COLS}

    for lineage, bp, subtree in zip(
        linelist_df["lineage"], linelist_df["breakpoints"], linelist_df["subtree"]
    ):

        # Mark the first time we see this recombinant type
        lin_bp_subtree = "{},{},{}".format(lineage, bp, subtree)
        if lin_bp_subtree in seen:
            continue
        else:
            seen.append(lin_bp_subtree)

        bp_subtree_df = linelist_df[
            (linelist_df["breakpoints"] == bp)
            & (linelist_df["subtree"] == subtree)
            & (linelist_df["lineage"] == lineage)
        ]

        status = bp_subtree_df["status"].values[0]
        parents = bp_subtree_df["parents"].values[0]
        sequences_int = len(bp_subtree_df)
        earliest_date = min(bp_subtree_df["datetime"])
        latest_date = max(bp_subtree_df["datetime"])
        issue = bp_subtree_df["issue"].values[0]
        year = bp_subtree_df["year"].values[0]
        growth = "0"

        sequences = "{} ({})".format(sequences_int, growth)

        # Calculate sequences growth from previous linelist
        growth = 0
        if prev_linelist:

            prev_lineage_col = None
            for col in prev_linelist_df.columns:
                if "lineage" in col:
                    prev_lineage_col = col
                    break

            # Try to match on both breakpoint and lineage
            match = prev_linelist_df[
                (prev_linelist_df["breakpoints"] == bp)
                & (prev_linelist_df[prev_lineage_col] == lineage)
            ]

            sequences_prev = len(match)
            growth = sequences - sequences_prev
            if growth <= 0:
                growth = str(growth)
            else:
                growth = "+{}".format(growth)

        # Update data
        recombinants_data["status"].append(status)
        recombinants_data["breakpoints"].append(bp)
        recombinants_data["parents"].append(parents)
        recombinants_data["sequences"].append(sequences)
        recombinants_data["sequences_int"].append(sequences_int)
        recombinants_data["earliest_date"].append(earliest_date)
        recombinants_data["latest_date"].append(latest_date)
        recombinants_data["lineage"].append(lineage)
        recombinants_data["issue"].append(issue)
        recombinants_data["subtree"].append(subtree)
        recombinants_data["year"].append(year)

    recombinants_df = pd.DataFrame(recombinants_data)
    recombinants_df.sort_values(by="sequences_int", ascending=False, inplace=True)
    recombinants_df.drop("sequences_int", axis="columns", inplace=True)

    outpath = os.path.join(outdir, "recombinants.tsv")
    recombinants_df.to_csv(outpath, index=False, sep="\t")

    # ---------------------------------------------------------------------------
    # Create the markdown report
    # ---------------------------------------------------------------------------

    report_content = ""

    # YAML Frontmatter
    frontmatter = "---\n"
    frontmatter += "title: SARS-CoV-2 Recombinants\n"
    frontmatter += "---\n"
    report_content += frontmatter + "\n"

    # Custom css
    custom_css = ""
    custom_css += "<style> th { font-size: 12px } td { font-size: 10px } </style>\n"
    report_content += custom_css + "\n"

    # Preface
    preface = ""
    preface += "---\n\n"
    preface += (
        "- `subtrees` can be uploaded to <https://auspice.us/> for visualization.\n"
    )
    preface += "- `breakpoints-sc2rf` can be visualized in VS Code with [ANSI Colors](https://marketplace.visualstudio.com/items?itemName=iliazeus.vscode-ansi)."
    report_content += preface + "\n\n"

    # -------------------------------------------------------------------------
    # Breakdown By Year

    year_table_note = ""
    year_table_note += "\*The number in parentheses indicates the growth compared to the previous report.<br>\n"

    for year in years_list:

        year_df = recombinants_df[recombinants_df["year"] == year]

        num_recombinants = len(year_df)
        num_sequences = sum([int(s.split(" ")[0]) for s in year_df["sequences"]])

        status_counts = {}
        for status in RECOMBINANT_STATUS:
            status_df = year_df[year_df["status"] == status]
            status_counts[status] = len(status_df)

        parents = []
        for p_csv in set(year_df["parents"]):
            for p in p_csv.split(","):
                if p not in parents:
                    parents.append(p)
        parents = ", ".join(parents)

        if parents != "":
            year_header = "## {year} | {parents}\n".format(year=year, parents=parents)
        else:
            year_header = "## {year}\n".format(year=year)
        report_content += year_header + "\n"

        year_desc = ""
        year_desc += (
            "- There are <u>{num_sequences} recombinant sequences</u>.\n".format(
                num_sequences=num_sequences
            )
        )
        year_desc += (
            "- There are <u>{num_recombinants} recombinant types </u>:\n".format(
                num_recombinants=num_recombinants
            )
        )

        # Add notes about count by status
        for status in RECOMBINANT_STATUS:

            year_desc += "\t- {num} type(s) are {status} (X*).\n".format(
                num=status_counts[status],
                status=status,
            )

        report_content += year_desc + "\n"

        year_df = year_df.drop("year", axis="columns")

        # Add footnote columns
        year_df = year_df.rename({"sequences": "sequences*"}, axis="columns")
        year_table = year_df.to_markdown(index=False, tablefmt="github")
        # Hack fix for dates
        year_table = year_table.replace(" 00:00:00", " " * 9)
        # Hack fix for <br> breakpoints
        year_table = re.sub("([0-9]),([0-9])", "\\1<br>\\2", year_table)
        # Hack fix for <br> parents
        year_table = re.sub("([A-Z]),([A-Z])", "\\1<br>\\2", year_table)

        report_content += year_table + "\n\n"
        report_content += year_table_note + "\n\n"

    # Rename Clades/Parents
    for clade in CLADES_RENAME:
        report_content = report_content.replace(clade, CLADES_RENAME[clade])

    # Versions
    ver_info = ""
    # Insert page break
    ver_info += (
        '<div style="page-break-after: always; visibility: hidden">\pagebreak</div>\n\n'
    )
    ver_info += "## Versions\n\n"
    ver_info += ver_df.to_markdown(index=False, tablefmt="github")
    report_content += ver_info + "\n\n"

    # Append a changelog

    if changelog:

        changelog_content = ""
        changelog_content += "## Changelog\n\n"
        with open(changelog) as infile:
            changelog_raw = infile.read()
            # Bump header levels down by 1 (extra #)
            changelog_bump = re.sub("^#", "##", changelog_raw)
            changelog_content += changelog_bump

        report_content += changelog_content + "\n\n"

    outpath = os.path.join(outdir, "report.md")
    with open(outpath, "w") as outfile:
        outfile.write(report_content)


if __name__ == "__main__":
    main()
