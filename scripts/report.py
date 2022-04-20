#!/usr/bin/env python3
import click
import os
import pandas as pd

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
@click.option("--cols", help="Columns to rename (csv)", required=True)
@click.option("--cols-rename", help="Renamed columns (csv)", required=True)
@click.option(
    "--years", help="Reporting years (csv)", required=True, default="2022,2021"
)
@click.option(
    "--lineage-to-issue",
    help="Lineage to issue (tsv)",
    required=True,
    default="data/controls/lineage_to_issue.tsv",
)
@click.option(
    "--breakpoint-to-issue",
    help="Breakpoint to issue tsv",
    required=True,
    default="data/controls/breakpoint_to_issue.tsv",
)
@click.option("--prev-report", help="Previous report", required=False)
def main(
    summary,
    cols,
    cols_rename,
    years,
    lineage_to_issue,
    breakpoint_to_issue,
    prev_report,
):
    """Create a linelist and recombinant report"""

    # Misc variables
    years_list = [int(y) for y in years.split(",")]
    outdir = os.path.dirname(summary)

    # Import Dataframes
    summary_df = pd.read_csv(summary, sep="\t")

    lineage_issue_df = pd.read_csv(lineage_to_issue, sep="\t", header=None)
    lineage_issue_df.columns = ["lineage", "issue"]

    breakpoint_issue_df = pd.read_csv(breakpoint_to_issue, sep="\t", header=None)
    breakpoint_issue_df.columns = ["breakpoint", "issue"]

    # Select and rename columns from summary
    cols_list = cols.split(",")
    cols_rename_list = cols_rename.split(",")
    rename_dict = {c: r for c, r in zip(cols_list, cols_rename_list)}
    report_df = summary_df[cols_list]
    report_df.rename(columns=rename_dict, inplace=True)
    outpath = os.path.join(outdir, "linelist.tsv")
    report_df.to_csv(outpath, sep="\t", index=False)

    # Check if previous report was specified
    if prev_report:

        # Identify new samples
        prev_report_df = pd.read_csv(prev_report, sep="\t")
        sample_col = prev_report_df.columns[0]
        prev_samples = list(prev_report_df[sample_col])
        current_samples = list(report_df[sample_col])
        new_samples = []
        for s in current_samples:
            if s not in prev_samples:
                new_samples.append("yes")
            else:
                new_samples.append("no")
        report_df["new"] = new_samples

        # Identify prev sequences for each breakpoint (for growth)
        prev_report_df = prev_report_df.pivot_table(
            index="breakpoints", values="date", aggfunc="count"
        ).reset_index()
        prev_report_df.columns = ["breakpoints", "sequences"]

    # Convert date to datetime
    report_df["datetime"] = pd.to_datetime(report_df["date"], format="%Y-%m-%d")
    report_df["year"] = [d.year for d in report_df["datetime"]]

    # Get program versions
    ver_cols = [col for col in summary_df if "ver" in col or "dataset" in col]
    ver_cols.sort()
    ver_vals = list(summary_df[ver_cols].iloc[0].values)
    ver_dict = {
        "program": [c.replace("_version", "") for c in ver_cols],
        "version": ver_vals,
    }
    ver_df = pd.DataFrame(ver_dict)

    header_cols = [
        "parents",
        "breakpoints",
        "sequences",
        "sequences_int",
        "earliest_date",
        "latest_date",
        "lineage:issue",
        "subtree",
        "year",
    ]

    rec_df = pd.DataFrame(columns=header_cols)
    outpath = os.path.join(outdir, "recombinants.tsv")

    data = {col: [] for col in header_cols}

    for bp in set(report_df["breakpoints"]):

        bp_df = report_df[report_df["breakpoints"] == bp]
        parents = list(bp_df["parents"])[0]
        sequences = len(bp_df)
        earliest_date = min(bp_df["datetime"])
        latest_date = max(bp_df["datetime"])
        subtree = list(bp_df["subtree"])[0]
        lineage = list(bp_df["lineage_usher"])[0]
        issue = NO_DATA_CHAR
        year = earliest_date.year

        # Try to find the issue based on lineages (designated)
        if lineage in list(lineage_issue_df["lineage"]):
            match = lineage_issue_df[lineage_issue_df["lineage"] == lineage]
            issue_num = str(match["issue"].values[0])
            issue_url = os.path.join(PANGO_ISSUES_URL, issue_num)
            issue = "[{}]({})".format(issue_num, issue_url)

        # Try to find the issue based on breakpoints (pending)
        elif bp in list(breakpoint_issue_df["breakpoint"]):
            match = breakpoint_issue_df[breakpoint_issue_df["breakpoint"] == bp]
            issue_num = str(match["issue"].values[0])
            issue_url = os.path.join(PANGO_ISSUES_URL, issue_num)
            issue = "[{}]({})".format(issue_num, issue_url)

        lineage_issue = "{}:{}".format(lineage, issue)

        for clade, rename in CLADES_RENAME.items():
            parents = parents.replace(clade, rename)
        parents = parents.replace(",", ", ")

        # Calculate growth from previous report
        growth = 0
        if prev_report and bp in list(prev_report_df["breakpoints"]):
            match = prev_report_df[prev_report_df["breakpoints"] == bp]
            sequences_prev = match["sequences"].values[0]
            growth = sequences - sequences_prev
            if growth <= 0:
                growth = str(growth)
            else:
                growth = "+{}".format(growth)

        sequences_int = sequences
        sequences = "{} ({})".format(sequences, growth)

        # Update data
        data["breakpoints"].append(bp)
        data["parents"].append(parents)
        data["sequences"].append(sequences)
        data["sequences_int"].append(sequences_int)
        data["earliest_date"].append(earliest_date)
        data["latest_date"].append(latest_date)
        data["lineage:issue"].append(lineage_issue)
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

        year_header = "## {year} | {parents}\n".format(year=year, parents=parents)
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

        dates = [d.strftime("%Y-%m-%d") for d in year_df["earliest_date"]]
        year_df["earliest_date"] = dates
        dates = [d.strftime("%Y-%m-%d") for d in year_df["latest_date"]]
        year_df["latest_date"] = dates

        year_df.drop("year", axis="columns", inplace=True)
        year_table = year_df.to_markdown(index=False, tablefmt="github")
        report_content += year_table + "\n\n"

    # Versions
    ver_info = ""
    # Insert page break
    ver_info += (
        '<div style="page-break-after: always; visibility: hidden">\pagebreak</div>\n\n'
    )
    ver_info += "## Versions\n\n"
    ver_info += ver_df.to_markdown(index=False, tablefmt="github")
    report_content += ver_info + "\n\n"

    outpath = os.path.join(outdir, "report.md")
    with open(outpath, "w") as outfile:
        outfile.write(report_content)


if __name__ == "__main__":
    main()
