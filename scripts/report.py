#!/usr/bin/env python3
import click
import os
import pandas as pd
import copy
import re

NO_DATA_CHAR = "NA"
CLADES_RENAME = {
    "Alpha/B.1.1.7/20I": "Alpha",
    "Delta/21I": "Delta (21I)",
    "Delta/21J": "Delta (21J)",
    "Omicron/BA.1/21K": "BA.1",
    "Omicron/BA.2/21L": "BA.2",
}
PANGO_ISSUES_URL = "https://github.com/cov-lineages/pango-designation/issues/"


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
def main(
    summary,
    years,
    issues,
    prev_linelist,
    changelog,
):
    """Create a linelist and recombinant report"""

    # Misc variables
    years_list = [int(y) for y in years.split(",")]
    outdir = os.path.dirname(summary)

    # Import Dataframes
    summary_df = pd.read_csv(summary, sep="\t")
    summary_df.fillna(NO_DATA_CHAR, inplace=True)

    issues_df = pd.read_csv(issues, sep="\t")

    # Select and rename columns from summary
    cols_dict = {
        "strain": "strain",
        "sc2rf_lineage": "lineage_sc2rf",
        "usher_pango_lineage_map": "lineage_usher",
        "Nextclade_pango": "lineage_nextclade",
        "sc2rf_clades_filter": "parents",
        "date": "date",
        "country": "country",
        "sc2rf_breakpoints_regions_filter": "breakpoints",
        "usher_subtree": "subtree",
    }
    cols_list = list(cols_dict.keys())

    report_df = copy.deepcopy(summary_df[cols_list])
    report_df.rename(columns=cols_dict, inplace=True)
    outpath = os.path.join(outdir, "linelist.tsv")
    report_df.to_csv(outpath, sep="\t", index=False)
    report_df.insert(1, "lineage", [NO_DATA_CHAR] * len(report_df))
    report_df.insert(2, "classifier", [NO_DATA_CHAR] * len(report_df))
    report_df.insert(3, "issue", [NO_DATA_CHAR] * len(report_df))

    # -------------------------------------------------------------------------
    # Lineage classification consensus

    for rec in report_df.iterrows():
        lineage = NO_DATA_CHAR
        classifier = NO_DATA_CHAR
        issue = NO_DATA_CHAR
        lineages_sc2rf = rec[1]["lineage_sc2rf"].split(",")
        lineage_usher = rec[1]["lineage_usher"]
        bp = rec[1]["breakpoints"]

        # If sc2rf was unambiguous
        if len(lineages_sc2rf) == 1 and lineages_sc2rf[0] != NO_DATA_CHAR:
            lineage = lineages_sc2rf[0]
            classifier = "sc2rf"

        # Otherwise use UShER
        else:
            lineage = lineage_usher
            classifier = "UShER"

        # Try to get issue from lineage
        if lineage in list(issues_df["lineage"]):
            match = issues_df[issues_df["lineage"] == lineage]
            issue = match["issue"].values[0]
        # Try to get issue from sc2rf lineage
        else:
            issues = []
            for lin in lineages_sc2rf:
                # ex. proposed517 is issue 517
                if "proposed" in lin:
                    issue = lin.replace("proposed", "")
                    issues.append(issue)
            if len(issues) > 1:
                issue = ",".join(issues)

        report_df.at[rec[0], "lineage"] = lineage
        report_df.at[rec[0], "classifier"] = classifier
        report_df.at[rec[0], "issue"] = str(issue)

    # Drop other lineage cols
    drop_cols = ["lineage_sc2rf", "lineage_usher", "lineage_nextclade"]
    report_df.drop(columns=drop_cols, inplace=True)

    # -------------------------------------------------------------------------
    # Previous Linelist Comparison

    if prev_linelist:

        # Identify new samples
        prev_linelist_df = pd.read_csv(prev_linelist, sep="\t")

        # Use first column as the sample ID
        linelist_sample_col = prev_linelist_df.columns[0]
        report_sample_col = report_df.columns[0]

        prev_samples = list(prev_linelist_df[linelist_sample_col])
        current_samples = list(report_df[report_sample_col])

        # Add "new" column
        new_samples = []
        for s in current_samples:
            if s not in prev_samples:
                new_samples.append("yes")
            else:
                new_samples.append("no")
        report_df["new"] = new_samples

    # Convert date to datetime
    report_df["datetime"] = pd.to_datetime(report_df["date"], format="%Y-%m-%d")
    report_df["year"] = [d.year for d in report_df["datetime"]]

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
    # Program Versions

    header_cols = [
        "parents",
        "breakpoints",
        "sequences",
        "sequences_int",
        "earliest_date",
        "latest_date",
        "lineage:issue",
        "classifier",
        "subtree",
        "year",
    ]

    # -------------------------------------------------------------------------
    # Recombinant Types

    rec_df = pd.DataFrame(columns=header_cols)
    outpath = os.path.join(outdir, "recombinants.tsv")

    # Different recombinant types can have the same breakpoint
    # ex. XE and XH

    seen = []
    data = {col: [] for col in header_cols}

    for bp, lineage in zip(report_df["breakpoints"], report_df["lineage"]):

        # Mark the first time we see this
        bp_lin = "{},{}".format(bp, lineage)
        if bp_lin in seen:
            continue
        else:
            seen.append(bp_lin)

        bp_lin_df = report_df[
            (report_df["breakpoints"] == bp) & (report_df["lineage"] == lineage)
        ]
        parents = list(bp_lin_df["parents"])[0]
        sequences = len(bp_lin_df)
        earliest_date = min(bp_lin_df["datetime"])
        latest_date = max(bp_lin_df["datetime"])
        issue = list(bp_lin_df["issue"])[0]
        classifier = list(bp_lin_df["classifier"])[0]
        subtree = list(bp_lin_df["subtree"])[0]
        year = earliest_date.year

        for clade, rename in CLADES_RENAME.items():
            parents = parents.replace(clade, rename)

        parents_uniq = []
        for p in parents.split(","):
            if p not in parents_uniq:
                parents_uniq.append(p)
        parents = ", ".join(parents_uniq)

        # Calculate growth from previous linelist
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

        sequences_int = sequences
        sequences = "{} ({})".format(sequences, growth)

        # issues will be a csv if there was a single breakpoint
        # and sc2rf found "proposed" lineages
        if "," in issue:
            issues_urls = [
                "[{issue}]({url})".format(issue=i, url=PANGO_ISSUES_URL + i)
                for i in issue.split(",")
            ]
            issue = ",".join(issues_urls)

        elif issue != NO_DATA_CHAR:
            issue_url = PANGO_ISSUES_URL + str(issue)
            issue = "[{}]({})".format(issue, issue_url)
        lineage_issue = "{}:{}".format(lineage, issue)

        # Update data
        data["breakpoints"].append(bp)
        data["parents"].append(parents)
        data["sequences"].append(sequences)
        data["sequences_int"].append(sequences_int)
        data["earliest_date"].append(earliest_date)
        data["latest_date"].append(latest_date)
        data["lineage:issue"].append(lineage_issue)
        data["classifier"].append(classifier)
        data["subtree"].append(subtree)
        data["year"].append(year)

    rec_df = pd.DataFrame(data)

    rec_df.sort_values(by=["sequences_int"], inplace=True, ascending=False)
    rec_df.drop("sequences_int", axis="columns", inplace=True)
    rec_df.to_csv(outpath, sep="\t", index=False)

    # ---------------------------------------------------------------------------
    # Create the markdown report

    report_content = ""

    # YAML Frontmatter
    frontmatter = "---\n"
    frontmatter += "title: SARS-CoV-2 Recombinants\n"
    frontmatter += "---\n"

    report_content += frontmatter + "\n"

    # Preface
    preface = ""
    preface += "---\n\n"
    preface += (
        "- `subtrees` can be uploaded to <https://auspice.us/> for visualization.\n"
    )
    preface += "- `breakpoints-sc2rf` can be visualized in VS Code with [ANSI Colors](https://marketplace.visualstudio.com/items?itemName=iliazeus.vscode-ansi)."

    report_content += preface + "\n\n"

    # By Year

    year_table_note = ""
    year_table_note += "<small>\n"
    year_table_note += "- *The number in parentheses indicates the growth compared to the previous report.\n"
    year_table_note += "- †Classification by breakpoint (sc2rf) takes priority over phylogenetic methods (UShER).\n"
    year_table_note += "</small>\n"

    for year in years_list:

        year_df = rec_df[rec_df["year"] == year]
        parents = []
        year_parents = list(year_df["parents"])
        for p_csv in year_parents:
            for p in p_csv.split(", "):
                parents.append(p)
        parents = list(set(parents))
        parents.sort()
        parents = ", ".join(parents)

        num_recombinants = len(year_df)
        num_sequences = sum([int(s.split(" ")[0]) for s in year_df["sequences"]])

        designated = year_df[year_df["lineage:issue"].str.startswith("X")]
        pending = year_df[year_df["lineage:issue"].str.startswith("misc")]

        num_designated = len(designated)
        num_pending = len(pending)
        num_unknown = num_recombinants - num_designated - num_pending

        if len(parents) > 1:
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

        year_desc += "\t- {num_designated} type(s) are designated (X*).\n".format(
            num_designated=num_designated
        )
        year_desc += "\t- {num_pending} type(s) are pending (misc*).\n".format(
            num_pending=num_pending
        )
        year_desc += (
            "\t- {num_unknown} type(s) do not match published breakpoints.\n".format(
                num_unknown=num_unknown
            )
        )

        report_content += year_desc + "\n"

        # dates = [str(d.strftime("%Y-%m-%d")) for d in year_df["earliest_date"]]
        # year_df.loc[year_df.index, "earliest_date"] = dates
        # dates = [str(d.strftime("%Y-%m-%d")) for d in year_df["latest_date"]]
        # year_df.loc[year_df.index, "latest_date"] = dates

        year_df = year_df.drop("year", axis="columns")

        # Add footnote columns
        year_df = year_df.rename({"sequences": "sequences*"}, axis="columns")
        year_df = year_df.rename(
            {"classifier": "classifier<sup>†</sup>"}, axis="columns"
        )

        year_table = year_df.to_markdown(index=False, tablefmt="github")
        # Hack fix for dates
        year_table = year_table.replace(" 00:00:00", " " * 9)
        report_content += year_table + "\n\n"
        report_content += year_table_note + "\n\n"

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
