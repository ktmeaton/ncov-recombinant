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

# Select and rename columns from summary
LINELIST_COLS = {
    "strain": "strain",
    "usher_pango_lineage_map": "lineage_usher",
    "sc2rf_lineage": "lineage_sc2rf",
    "Nextclade_pango": "lineage_nextclade",
    "sc2rf_clades_filter": "parents",
    "sc2rf_clades_regions_filter": "regions",
    "date": "date",
    "country": "country",
    "sc2rf_breakpoints_regions_filter": "breakpoints",
    "usher_subtree": "subtree",
}

# Select and rename columns from linelist
RECOMBINANTS_COLS = [
    "status",  # excluded from report.md
    "parents",
    "breakpoints",
    "subtree",
    "sequences",
    "sequences_int",  # excluded from report.md
    "earliest_date",
    "latest_date",
    "lineage",
    "issue",
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
    # Create the linelist (linelist.tsv)
    # -------------------------------------------------------------------------

    linelist_df = copy.deepcopy(summary_df[cols_list])
    linelist_df.rename(columns=LINELIST_COLS, inplace=True)

    # -------------------------------------------------------------------------
    # Lineage Status
    # Use lineage calls by UShER and sc2rf to classify recombinants status

    # Initialize columns
    linelist_df["issue"] = [NO_DATA_CHAR] * len(linelist_df)
    linelist_df["status"] = [NO_DATA_CHAR] * len(linelist_df)

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

    recombinants_df = pd.DataFrame(columns=RECOMBINANTS_COLS)

    # Define a recombinant by the intersection of:
    #   - Breakpoints
    #   - subtree # (Phylogenetic placement)

    # Different recombinant types can have the same breakpoint
    # but different placement: ex. XE and XH

    seen = []
    recombinants_data = {col: [] for col in RECOMBINANTS_COLS}

    for bp, subtree in zip(linelist_df["breakpoints"], linelist_df["subtree"]):

        # Mark the first time we see this recombinant type
        bp_subtree = "{},{}".format(bp, subtree)
        if bp_subtree in seen:
            continue
        else:
            seen.append(bp_subtree)

        bp_subtree_df = linelist_df[
            (linelist_df["breakpoints"] == bp) & (linelist_df["subtree"] == subtree)
        ]

        status = bp_subtree_df["issue"].values[0]
        parents = bp_subtree_df["parents"].values[0]
        sequences_int = len(bp_subtree_df)
        earliest_date = min(bp_subtree_df["datetime"])
        latest_date = max(bp_subtree_df["datetime"])
        lineage = bp_subtree_df["lineage_usher"].values[0]
        issue = bp_subtree_df["issue"].values[0]
        year = bp_subtree_df["issue"].values[0]
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

        break

    # Just tmp to make pre-commit happy
    print(years_list)
    print(re.sub("a", "b", "ab"))
    print(recombinants_df)
    # End tmp

    quit()

    # outpath = os.path.join(outdir, "recombinants.tsv")

    # # -------------------------------------------------------------------------
    # # Program Versions

    # ver_cols = [col for col in summary_df if "ver" in col or "dataset" in col]
    # ver_cols.sort()
    # ver_vals = list(summary_df[ver_cols].iloc[0].values)
    # ver_dict = {
    #     "program": [c.replace("_version", "") for c in ver_cols],
    #     "version": ver_vals,
    # }
    # ver_df = pd.DataFrame(ver_dict)

    # # -------------------------------------------------------------------------
    # # Recombinant Types

    # # Define a recombinant by the intersection of:
    # #   - Breakpoints
    # #   - subtree # (Phylogenetic placement)

    # # Different recombinant types can have the same breakpoint
    # # but different placement: ex. XE and XH

    # seen = []
    # data = {col: [] for col in header_cols}

    # for bp, lineage in zip(report_df["breakpoints"], report_df["lineage"]):
    #     # for bp, subtree in zip(report_df["breakpoints"], report_df["subtree"]):

    #     # Mark the first time we see this
    #     bp_lin = "{},{}".format(bp, lineage)
    #     if bp_lin in seen:
    #         continue
    #     else:
    #         seen.append(bp_lin)

    #     bp_lin_df = report_df[
    #         (report_df["breakpoints"] == bp) & (report_df["lineage"] == lineage)
    #     ]
    #     parents = list(bp_lin_df["parents"])[0]
    #     sequences = len(bp_lin_df)
    #     earliest_date = min(bp_lin_df["datetime"])
    #     latest_date = max(bp_lin_df["datetime"])
    #     issue = list(bp_lin_df["issue"])[0]
    #     subtree = list(bp_lin_df["subtree"])[0]
    #     year = earliest_date.year

    #     for clade, rename in CLADES_RENAME.items():
    #         parents = parents.replace(clade, rename)

    #     parents_uniq = []
    #     for p in parents.split(","):
    #         if p not in parents_uniq:
    #             parents_uniq.append(p)
    #     parents = ", ".join(parents_uniq)

    #     # Calculate growth from previous linelist
    #     growth = 0
    #     if prev_linelist:

    #         prev_lineage_col = None
    #         for col in prev_linelist_df.columns:
    #             if "lineage" in col:
    #                 prev_lineage_col = col
    #                 break

    #         # Try to match on both breakpoint and lineage
    #         match = prev_linelist_df[
    #             (prev_linelist_df["breakpoints"] == bp)
    #             & (prev_linelist_df[prev_lineage_col] == lineage)
    #         ]

    #         sequences_prev = len(match)
    #         growth = sequences - sequences_prev
    #         if growth <= 0:
    #             growth = str(growth)
    #         else:
    #             growth = "+{}".format(growth)

    #     sequences_int = sequences
    #     sequences = "{} ({})".format(sequences, growth)

    #     # issues will be a csv if there was a single breakpoint
    #     # and if sc2rf found "proposed" lineages
    #     if "," in issue:
    #         issues_urls = [
    #             "[{issue}]({url})".format(issue=i, url=PANGO_ISSUES_URL + i)
    #             for i in issue.split(",")
    #         ]
    #         issue = ",".join(issues_urls)

    #     elif issue != NO_DATA_CHAR:
    #         issue_url = PANGO_ISSUES_URL + str(issue)
    #         issue = "[{}]({})".format(issue, issue_url)

    #     # Get status
    #     if lineage.startswith("X"):
    #         status = "designated"
    #     elif lineage.startswith("proposed"):
    #         status = "proposed"
    #     else:
    #         status = "unpublished"

    #     # Update data
    #     data["status"].append(status)
    #     data["breakpoints"].append(bp)
    #     data["parents"].append(parents)
    #     data["sequences"].append(sequences)
    #     data["sequences_int"].append(sequences_int)
    #     data["earliest_date"].append(earliest_date)
    #     data["latest_date"].append(latest_date)
    #     data["lineage"].append(lineage)
    #     data["issue"].append(issue)
    #     data["subtree"].append(subtree)
    #     data["year"].append(year)

    # rec_df = pd.DataFrame(data)

    # rec_df.sort_values(by=["sequences_int"], inplace=True, ascending=False)
    # rec_df.drop("sequences_int", axis="columns", inplace=True)
    # rec_df.to_csv(outpath, sep="\t", index=False)

    # # ---------------------------------------------------------------------------
    # # Create the markdown report
    # # ---------------------------------------------------------------------------

    # report_content = ""

    # # YAML Frontmatter
    # frontmatter = "---\n"
    # frontmatter += "title: SARS-CoV-2 Recombinants\n"
    # frontmatter += "---\n"
    # report_content += frontmatter + "\n"

    # # Custom css
    # custom_css = ""
    # custom_css += "<style> th { font-size: 12px } td { font-size: 10px } </style>\n"
    # report_content += custom_css + "\n"

    # # Preface
    # preface = ""
    # preface += "---\n\n"
    # preface += (
    #     "- `subtrees` can be uploaded to <https://auspice.us/> for visualization.\n"
    # )
    # preface += "- `breakpoints-sc2rf` can be visualized in VS Code with [ANSI Colors](https://marketplace.visualstudio.com/items?itemName=iliazeus.vscode-ansi)."
    # report_content += preface + "\n\n"

    # # -------------------------------------------------------------------------
    # # Breakdown By Year
    # year_table_note = ""
    # year_table_note += "\*The number in parentheses indicates the growth compared to the previous report.<br>\n"

    # for year in years_list:

    #     year_df = rec_df[rec_df["year"] == year]

    #     # Formatting Parents
    #     parents = []
    #     year_parents = list(year_df["parents"])
    #     for p_csv in year_parents:
    #         for p in p_csv.split(", "):
    #             parents.append(p)
    #     parents = list(set(parents))
    #     parents.sort()
    #     parents = ", ".join(parents)

    #     num_recombinants = len(year_df)
    #     num_sequences = sum([int(s.split(" ")[0]) for s in year_df["sequences"]])

    #     status_counts = {status: 0 for status in RECOMBINANT_STATUS}

    #     designated = year_df[year_df["lineage"].str.startswith("X")]
    #     proposed = year_df[year_df["lineage"].str.startswith("proposed")]

    #     num_designated = len(designated)
    #     num_proposed = len(proposed)
    #     num_unpublished = num_recombinants - num_designated - num_proposed

    #     if len(parents) > 1:
    #         year_header = "## {year} | {parents}\n".format(year=year, parents=parents)
    #     else:
    #         year_header = "## {year}\n".format(year=year)
    #     report_content += year_header + "\n"

    #     year_desc = ""
    #     year_desc += (
    #         "- There are <u>{num_sequences} recombinant sequences</u>.\n".format(
    #             num_sequences=num_sequences
    #         )
    #     )
    #     year_desc += (
    #         "- There are <u>{num_recombinants} recombinant types </u>:\n".format(
    #             num_recombinants=num_recombinants
    #         )
    #     )

    #     year_desc += "\t- {num_designated} type(s) are designated (X*).\n".format(
    #         num_designated=num_designated
    #     )
    #     year_desc += "\t- {num_proposed} type(s) are proposed (proposed*).\n".format(
    #         num_proposed=num_proposed
    #     )
    #     year_desc += "\t- {num_unpublished} type(s) are unpublished.\n".format(
    #         num_unpublished=num_unpublished
    #     )

    #     report_content += year_desc + "\n"

    #     year_df = year_df.drop("year", axis="columns")

    #     # Add footnote columns
    #     year_df = year_df.rename({"sequences": "sequences*"}, axis="columns")
    #     year_table = year_df.to_markdown(index=False, tablefmt="github")
    #     # Hack fix for dates
    #     year_table = year_table.replace(" 00:00:00", " " * 9)
    #     # Hack fix for <br> breakpoints
    #     year_table = re.sub("([0-9]),([0-9])", "\\1<br>\\2", year_table)
    #     # Hack fix for <br> parents
    #     year_table = re.sub("([0-9]), ([A-Z])", "\\1<br>\\2", year_table)

    #     report_content += year_table + "\n\n"
    #     report_content += year_table_note + "\n\n"

    # # Versions
    # ver_info = ""
    # # Insert page break
    # ver_info += (
    #     '<div style="page-break-after: always; visibility: hidden">\pagebreak</div>\n\n'
    # )
    # ver_info += "## Versions\n\n"
    # ver_info += ver_df.to_markdown(index=False, tablefmt="github")
    # report_content += ver_info + "\n\n"

    # # Append a changelog

    # if changelog:

    #     changelog_content = ""
    #     changelog_content += "## Changelog\n\n"
    #     with open(changelog) as infile:
    #         changelog_raw = infile.read()
    #         # Bump header levels down by 1 (extra #)
    #         changelog_bump = re.sub("^#", "##", changelog_raw)
    #         changelog_content += changelog_bump

    #     report_content += changelog_content + "\n\n"

    # outpath = os.path.join(outdir, "report.md")
    # with open(outpath, "w") as outfile:
    #     outfile.write(report_content)


if __name__ == "__main__":
    main()
