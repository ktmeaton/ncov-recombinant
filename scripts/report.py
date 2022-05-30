#!/usr/bin/env python3
import click
import pptx
from datetime import date
import os
import pandas as pd
import epiweeks


NO_DATA_CHAR = "NA"
TITLE = "SARS-CoV-2 Recombinants"
FONT_SIZE_PARAGRAPH = 20

# designated: X*
# proposed: proposed* or associated issue
# unpublished: not designated or proposed

RECOMBINANT_STATUS = {
    "designated": "X*",
    "proposed": "proposed*",
    "unpublished": "misc*",
}

# Concise names for report
CLADES_RENAME = {
    "Alpha/B.1.1.7/20I": "Alpha (20I)",
    "Delta/21I": "Delta (21I)",
    "Delta/21J": "Delta (21J)",
    "Omicron/21K": "BA.1",
    "Omicron/21L": "BA.2",
}


""" Ref for slide types:
0 ->  title and subtitle
1 ->  title and content
2 ->  section header
3 ->  two content
4 ->  Comparison
5 ->  Title only
6 ->  Blank
7 ->  Content with caption
8 ->  Pic with caption
"""


@click.command()
@click.option("--linelist", help="Recombinant sequences (TSV)", required=True)
@click.option("--recombinants", help="Recombinant lineages (TSV)", required=True)
@click.option(
    "--geo", help="Geography column to summarize", required=False, default="country"
)
@click.option(
    "--changelog", help="Markdown changelog", required=False, default="CHANGELOG.md"
)
@click.option(
    "--template",
    help="Powerpoint template",
    required=False,
    default="resources/template.pptx",
)
def main(
    linelist,
    recombinants,
    template,
    geo,
    changelog,
):
    """Create a report of powerpoint slides"""

    # Parse build name from linelist path
    build = os.path.basename(os.path.dirname(linelist))
    subtitle = "{}\n{}".format(build.title(), date.today())
    outdir = os.path.dirname(linelist)

    # Import dataframes
    linelist_df = pd.read_csv(linelist, sep="\t")
    recombinants_df = pd.read_csv(recombinants, sep="\t")

    # Import changelog (just the first header 2 section)
    with open(changelog) as infile:
        changelog_lines = infile.read().split("\n")
        changelog_date = ""
        changelog_content = []
        in_header_two = False

        for line in changelog_lines:

            # Stop at the second one
            if line.startswith("## ") and in_header_two:
                break
            elif in_header_two:
                if line.startswith("#"):
                    continue
                if not line:
                    continue
                changelog_content.append(line.replace("1. ", ""))
            elif line.startswith("## ") and not in_header_two:
                in_header_two = True
                changelog_date = line.replace("## ", "")

    # Add datetime columns
    linelist_df["datetime"] = pd.to_datetime(linelist_df["date"], format="%Y-%m-%d")
    linelist_df["year"] = [d.year for d in linelist_df["datetime"]]
    linelist_df["epiweek"] = [
        epiweeks.Week.fromdate(d, system="iso").startdate()
        for d in linelist_df["datetime"]
    ]

    largest_i = recombinants_df["sequences"].idxmax()
    largest_cluster_id = recombinants_df["cluster_id"][largest_i]
    largest_lineage = recombinants_df["lineage"][largest_i]

    # Find plots
    lineage_plot = os.path.join(outdir, "plots", "lineage.png")
    # status_plot = os.path.join(outdir, "plots", "status.png")
    geo_plot = os.path.join(outdir, "plots", "geography.png")
    designated_plot = os.path.join(outdir, "plots", "designated.png")
    largest_plot = os.path.join(outdir, "plots", "largest.png")

    # Stats
    num_lineages = len(recombinants_df)
    num_sequences = len(linelist_df)
    status_counts = {}
    for status in RECOMBINANT_STATUS:
        rec_status_df = recombinants_df[recombinants_df["status"] == status]
        seq_status_df = linelist_df[linelist_df["status"] == status]
        status_counts[status] = {
            "lineages": len(rec_status_df),
            "sequences": len(seq_status_df),
        }

    # ---------------------------------------------------------------------
    # Geography
    geo_df = pd.pivot_table(
        data=linelist_df,
        values="strain",
        index=[geo],
        aggfunc="count",
    )
    geo_df.index.name = None
    geo_df.fillna(0, inplace=True)
    geo_df[geo] = geo_df.index
    geo_df.rename(columns={"strain": "sequences"}, inplace=True)
    geo_df.sort_values(by="sequences", inplace=True, ascending=False)

    # ---------------------------------------------------------------------
    # Designated

    # Designated lineages aren't always present, so this is optional
    if os.path.exists(designated_plot):
        designated_df = pd.pivot_table(
            data=linelist_df[linelist_df["status"] == "designated"],
            values="strain",
            index=["lineage"],
            aggfunc="count",
        )
        designated_df.index.name = None
        designated_df.fillna(0, inplace=True)
        designated_df["lineage"] = designated_df.index
        designated_df.rename(columns={"strain": "sequences"}, inplace=True)
        designated_df.sort_values(by="sequences", inplace=True, ascending=False)

    # ---------------------------------------------------------------------
    # Largest

    largest_df = pd.pivot_table(
        data=linelist_df[linelist_df["cluster_id"] == largest_cluster_id],
        values="strain",
        index=[geo],
        aggfunc="count",
    )
    largest_df.index.name = None
    largest_df.fillna(0, inplace=True)
    largest_df[geo] = largest_df.index
    largest_df.rename(columns={"strain": "sequences"}, inplace=True)
    largest_df.sort_values(by="sequences", inplace=True, ascending=False)

    # ---------------------------------------------------------------------
    # Presentation
    # ---------------------------------------------------------------------
    presentation = pptx.Presentation(template)

    # ---------------------------------------------------------------------
    # Title Slide
    title_slide_layout = presentation.slide_layouts[0]
    slide = presentation.slides.add_slide(title_slide_layout)
    slide.shapes.title.text = TITLE
    slide.placeholders[1].text = subtitle

    # ---------------------------------------------------------------------
    # Lineage Summary

    graph_slide_layout = presentation.slide_layouts[8]
    slide = presentation.slides.add_slide(graph_slide_layout)
    title = slide.shapes.title
    title.text_frame.text = "Status"
    title.text_frame.paragraphs[0].font.bold = True

    chart_placeholder = slide.placeholders[1]
    chart_placeholder.insert_picture(lineage_plot)
    body = slide.placeholders[2]

    summary = "\n"
    summary += "There are {num_lineages} recombinant lineages.\n".format(
        num_lineages=num_lineages
    )
    for status in RECOMBINANT_STATUS:
        summary += "  - {lineages} lineages are {status}.\n".format(
            lineages=status_counts[status]["lineages"], status=status
        )
    summary += "\n"
    summary += "There are {num_sequences} recombinant sequences.\n".format(
        num_sequences=num_sequences
    )
    for status in RECOMBINANT_STATUS:
        summary += "  - {sequences} sequences are {status}.\n".format(
            sequences=status_counts[status]["sequences"], status=status
        )

    body.text = summary

    # ---------------------------------------------------------------------
    # Geographic Summary

    graph_slide_layout = presentation.slide_layouts[8]
    slide = presentation.slides.add_slide(graph_slide_layout)
    title = slide.shapes.title

    title.text_frame.text = "Geography"
    title.text_frame.paragraphs[0].font.bold = True

    chart_placeholder = slide.placeholders[1]
    chart_placeholder.insert_picture(geo_plot)
    body = slide.placeholders[2]

    summary = "\n"
    summary += "Recombinants are observed in {num_geo} {geo}.\n".format(
        num_geo=len(geo_df), geo=geo
    )

    for rec in geo_df.iterrows():
        region = rec[1][geo]
        sequences = rec[1]["sequences"]
        summary += "  - {region} ({sequences})\n".format(
            region=region, sequences=sequences
        )

    body.text = summary

    # ---------------------------------------------------------------------
    # Designated Summary
    if os.path.exists(designated_plot):
        graph_slide_layout = presentation.slide_layouts[8]
        slide = presentation.slides.add_slide(graph_slide_layout)
        title = slide.shapes.title

        title.text_frame.text = "Designated"
        title.text_frame.paragraphs[0].font.bold = True

        chart_placeholder = slide.placeholders[1]
        chart_placeholder.insert_picture(designated_plot)
        body = slide.placeholders[2]

        summary = "\n"
        summary += "There are {num} designated lineages.\n".format(
            num=len(designated_df)
        )

        for rec in designated_df.iterrows():
            lineage = rec[1]["lineage"]
            sequences = rec[1]["sequences"]
            summary += "  - {lineage} ({sequences})\n".format(
                lineage=lineage, sequences=sequences
            )

        body.text = summary

    # ---------------------------------------------------------------------
    # Largest Summary
    graph_slide_layout = presentation.slide_layouts[8]
    slide = presentation.slides.add_slide(graph_slide_layout)
    title = slide.shapes.title

    title.text_frame.text = "Largest"
    title.text_frame.paragraphs[0].font.bold = True

    chart_placeholder = slide.placeholders[1]
    chart_placeholder.insert_picture(largest_plot)
    body = slide.placeholders[2]

    summary = "\n"
    summary += "The largest lineage is {lineage}.\n".format(lineage=largest_lineage)
    summary += "The cluster ID for this lineage is {id}.\n".format(
        id=largest_cluster_id
    )
    summary += "{lineage} is observed in {num_geo} {geo}.\n".format(
        lineage=largest_lineage, num_geo=len(largest_df), geo=geo
    )

    for rec in largest_df.iterrows():
        region = rec[1][geo]
        sequences = rec[1]["sequences"]
        summary += "  - {region} ({sequences})\n".format(
            region=region, sequences=sequences
        )

    body.text = summary

    # ---------------------------------------------------------------------
    # Changelog
    text_slide_layout = presentation.slide_layouts[1]
    slide = presentation.slides.add_slide(text_slide_layout)
    title = slide.shapes.title

    title.text_frame.text = "Changelog ({})".format(changelog_date)
    title.text_frame.paragraphs[0].font.bold = True

    body = slide.placeholders[1]
    body.text_frame.text = "\n".join(changelog_content)

    for paragraph in body.text_frame.paragraphs:
        paragraph.font.size = pptx.util.Pt(18)

    # ---------------------------------------------------------------------
    # Saving file
    outpath = os.path.join(outdir, "report.pptx")
    presentation.save(outpath)


if __name__ == "__main__":
    main()
