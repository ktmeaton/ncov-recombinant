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

RECOMBINANT_STATUS = {
    "designated": "X*",
    "proposed": "proposed*",
    "unpublished": "misc*",
}

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
    "ncov-recombinant_version": "recombinant_pipeline",
    "usher_version": "recombinant_classifier",
    "usher_dataset": "recombinant_classifier_dataset",
}

# Select and rename columns from linelist
RECOMBINANTS_COLS = [
    "status",  # excluded from report.md
    "lineage",
    "parents",
    "breakpoints",
    "issue",
    "subtree",
    "sequences",
    "sequences_int",  # excluded from report.md
    "earliest_date",
    "latest_date",
    "year",  # excluded from report.md
]

# Resize the markdown table columns to fit this char limit
MD_COL_WIDTH = 20


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
        bp = rec[1]["breakpoints"]

        # Use UShER
        lineage = lineage_usher

        # Try to get find a related pango-designation by lineage name
        # This will work for designated (X*) or proposed UShER lineages
        if lineage in list(issues_df["lineage"]):
            match = issues_df[issues_df["lineage"] == lineage]
            issue = match["issue"].values[0]

            # if there are no breakpoints, this was a nextclade recombinant
            # that auto-passed sc2rf. Use breakpoints in issues table
            if bp == NO_DATA_CHAR:
                bp = match["breakpoints_curated"].values[0]
                linelist_df.at[rec[0], "breakpoints"] = bp
                parents = match["parents_curated"].values[0]
                linelist_df.at[rec[0], "parents"] = parents
                # TBD: regions if desired

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
        else:
            recombinant_lineage.append("unpublished_recombinant")

    linelist_df["recombinant_lineage_curated"] = recombinant_lineage

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

    # Define a recombinant by:
    #   - Breakpoints
    #   - Parents
    #   - Phylogenetic placement: lineage or subtree?

    # Different recombinant types can have the same breakpoint
    # but different placement: ex. XE and XH

    seen = []
    recombinants_data = {col: [] for col in RECOMBINANTS_COLS}

    for bp, parents, lineage in zip(
        linelist_df["breakpoints"],
        linelist_df["parents"],
        linelist_df["lineage"],
    ):

        # Mark the first time we see this recombinant type
        rec_type = "{},{},{}".format(bp, parents, lineage)
        if rec_type in seen:
            continue
        else:
            seen.append(rec_type)

        rec_type_df = linelist_df[
            (linelist_df["breakpoints"] == bp)
            & (linelist_df["parents"] == parents)
            & (linelist_df["lineage"] == lineage)
        ]

        status = rec_type_df["status"].values[0]
        parents = rec_type_df["parents"].values[0]
        sequences_int = len(rec_type_df)
        earliest_date = min(rec_type_df["datetime"])
        latest_date = max(rec_type_df["datetime"])
        issue = rec_type_df["issue"].values[0]
        year = rec_type_df["year"].values[0]
        subtree = rec_type_df["subtree"].values[0]
        growth = "0"

        # Calculate sequences growth from previous linelist
        growth = 0
        if prev_linelist:

            prev_lineage_col = "lineage_usher"
            if "lineage" in prev_linelist_df.columns:
                prev_lineage_col = "lineage"

            # Try to match on both breakpoint and lineage
            match = prev_linelist_df[
                (prev_linelist_df["breakpoints"] == bp)
                & (prev_linelist_df[prev_lineage_col] == lineage)
            ]

            sequences_prev = len(match)
            growth = sequences_int - sequences_prev
            if growth <= 0:
                growth = str(growth)
            else:
                growth = "+{}".format(growth)

        sequences = "{} ({})".format(sequences_int, growth)

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
    preface += "- See the **Definitions** section for more info.\n"
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

            year_desc += "\t- {num} type(s) are {status}.<br>\n".format(
                num=status_counts[status],
                status=status,
            )

        report_content += year_desc + "\n"

        year_df = year_df.drop("year", axis="columns")

        # Add footnote columns
        year_df = year_df.rename({"sequences": "sequences*"}, axis="columns")
        # Make issue's URLs
        # issues_list = list(year_df["issue"])
        # issues_urls = [
        #    "[{issue}]({url})".format(issue=i, url=PANGO_ISSUES_URL + i)
        #    for i in issues_list
        # ]
        # year_df.loc[year_df.index, "issue"] = issues_urls
        # Drop Status columns
        year_df.drop(columns="status", inplace=True)
        year_table = year_df.to_markdown(index=False, tablefmt="github")
        # Hack fix for dates
        year_table = year_table.replace(" 00:00:00", " " * 9)
        # Hack fix for <br> breakpoints
        year_table = re.sub("([0-9]),([0-9])", "\\1<br>\\2", year_table)
        # Hack fix for <br> parents
        # year_table = re.sub("([A-Z]),([A-Z])", "\\1<br>\\2", year_table)

        report_content += year_table + "\n\n"
        report_content += year_table_note + "\n\n"

    # Rename Clades/Parents
    for clade in CLADES_RENAME:
        report_content = report_content.replace(clade, CLADES_RENAME[clade])

    # Resize Table Columns
    num_columns = len(year_df.columns)
    line_replace = ""
    for _i in range(0, num_columns):
        line_replace += "|:" + "-" * MD_COL_WIDTH + ":"
    line_replace += "|"

    report_content = re.sub("\|-.*", line_replace, report_content)

    # -------------------------------------------------------------------------
    # Definitions

    defs = ""
    # Insert page break
    defs += (
        '<div style="page-break-after: always; visibility: hidden">\pagebreak</div>\n\n'
    )
    defs += "## Definitions\n\n"
    defs += " - **Breakpoints**: Intervals in which a breakpoint occurs according to [sc2rf](https://github.com/lenaschimmel/sc2rf).\n"
    defs += " - **Designated**: Formally designated as X\* in [pango-designation](https://github.com/cov-lineages/pango-designation).\n"
    defs += " - **Issue**: The issue number in [pango-designation issues](https://github.com/cov-lineages/pango-designation/issues).\n"
    defs += " - **Lineage**: Lineage assignment according to [UShER](https://github.com/yatisht/usher).\n"
    defs += " - **Parents**: Parental clades according to [sc2rf](https://github.com/lenaschimmel/sc2rf).\n"
    defs += " - **Proposed**: Parents and breakpoints <u>match</u> a [pango-designation issue](https://github.com/cov-lineages/pango-designation/issues).\n"
    defs += " - **Recombinant Type**: Sequences with the same `lineage`, `breakpoints`, and `parents`.\n"
    defs += " - **Subtree**: A tree of the 500 closest related sequences, extracted from UShER.\n"
    defs += " - **Unpublished**: Parents and breakpoints <u>do not match</u> a [pango-designation issues](https://github.com/cov-lineages/pango-designation/issues).\n"

    report_content += defs + "\n\n"

    # -------------------------------------------------------------------------
    # Versions
    ver_info = ""
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
