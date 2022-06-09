#!/usr/bin/env python3
import click
import pptx
from datetime import date
import os
import pandas as pd
import epiweeks
from datetime import datetime, timedelta
import copy


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
@click.option("--plot-dir", help="Plotting directory", required=True)
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
    plot_dir,
    template,
    geo,
    changelog,
):
    """Create a report of powerpoint slides"""

    # Parse build name from plot_dir path

    build = os.path.basename(os.path.dirname(plot_dir))
    outdir = os.path.dirname(plot_dir)
    subtitle = "{}\n{}".format(build.title(), date.today())

    # Import dataframes
    plot_suffix = ".png"
    df_suffix = ".tsv"
    labels = [f.replace(plot_suffix, "") for f in os.listdir(plot_dir) if f.endswith(plot_suffix)]
    plot_dict = {}
    for label in labels:
        plot_dict[label] = {}
        plot_dict[label]["plot_path"] = os.path.join(plot_dir, label + plot_suffix)
        plot_dict[label]["df_path"] = os.path.join(plot_dir, label + df_suffix)
        plot_dict[label]["df"] = pd.read_csv(plot_dict[label]["df_path"], sep="\t")
        plot_dict[label]["df"].index = plot_dict[label]["df"]["epiweek"]


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

    plot_path = plot_dict["lineage"]["plot_path"]
    df = plot_dict["lineage"]["df"]
    lineages = list(df.columns)
    lineages.remove("epiweek")

    num_lineages = len(lineages)
    num_sequences = 0
    for lineage in lineages:
        count = sum(df[lineage].dropna())
        num_sequences += count

    status_counts = {}
    df = plot_dict["status"]["df"]

    for col in df.columns:
        if col == "epiweek": continue
        status = col
        seq_count = sum(df[status].dropna())
        # START HERE! How to count status lineages?   
        lineage_count = 0
        status_counts[status.lower()] = {
            "lineages": int(lineage_count),
            "sequences": int(seq_count),
        }

    graph_slide_layout = presentation.slide_layouts[8]
    slide = presentation.slides.add_slide(graph_slide_layout)
    title = slide.shapes.title
    title.text_frame.text = "Status"
    title.text_frame.paragraphs[0].font.bold = True

    chart_placeholder = slide.placeholders[1]
    chart_placeholder.insert_picture(plot_path)
    body = slide.placeholders[2]

    summary = "\n"
    summary += "There are {num_lineages} recombinant lineages.\n".format(
        num_lineages=int(num_lineages)
    )
    for status in RECOMBINANT_STATUS:
        summary += "  - {lineages} lineages are {status}.\n".format(
            lineages=status_counts[status]["lineages"], status=status
        )
    summary += "\n"
    summary += "There are {num_sequences} recombinant sequences.\n".format(
        num_sequences=int(num_sequences)
    )
    for status in RECOMBINANT_STATUS:
        summary += "  - {sequences} sequences are {status}.\n".format(
            sequences=status_counts[status]["sequences"], status=status
        )

    body.text_frame.text = summary

    # ---------------------------------------------------------------------
    # Geographic Summary

    plot_path = plot_dict["geography"]["plot_path"]
    df = plot_dict["geography"]["df"]
    geos = list(df.columns)
    geos.remove("epiweek")
    num_geos = len(geos)

    graph_slide_layout = presentation.slide_layouts[8]
    slide = presentation.slides.add_slide(graph_slide_layout)
    title = slide.shapes.title

    title.text_frame.text = "Geography"
    title.text_frame.paragraphs[0].font.bold = True

    chart_placeholder = slide.placeholders[1]
    chart_placeholder.insert_picture(plot_path)
    body = slide.placeholders[2]

    summary = "\n"
    summary += "Recombinants are observed in {num_geos} {geo}.\n".format(
        num_geos=num_geos, geo=geo
    )

    # for rec in df.iterrows():
    #     region = rec[1][geo]
    #     sequences = rec[1]["sequences"]
    #     summary += "  - {region} ({sequences})\n".format(
    #         region=region, sequences=sequences
    #     )

    body.text = summary

    # # ---------------------------------------------------------------------
    # # Designated Summary

    # if os.path.exists(designated_plot):
    #     graph_slide_layout = presentation.slide_layouts[8]
    #     slide = presentation.slides.add_slide(graph_slide_layout)
    #     title = slide.shapes.title

    #     title.text_frame.text = "Designated"
    #     title.text_frame.paragraphs[0].font.bold = True

    #     chart_placeholder = slide.placeholders[1]
    #     chart_placeholder.insert_picture(designated_plot)
    #     body = slide.placeholders[2]

    #     summary = "\n"
    #     summary += "There are {num} designated lineages.\n".format(
    #         num=len(designated_df)
    #     )

    #     for rec in designated_df.iterrows():
    #         lineage = rec[1]["lineage"]
    #         sequences = rec[1]["sequences"]
    #         summary += "  - {lineage} ({sequences})\n".format(
    #             lineage=lineage, sequences=sequences
    #         )

    #     body.text = summary

    # # ---------------------------------------------------------------------
    # # Largest Summary

    # graph_slide_layout = presentation.slide_layouts[8]
    # slide = presentation.slides.add_slide(graph_slide_layout)
    # title = slide.shapes.title

    # title.text_frame.text = "Largest"
    # title.text_frame.paragraphs[0].font.bold = True

    # chart_placeholder = slide.placeholders[1]
    # chart_placeholder.insert_picture(largest_plot)
    # body = slide.placeholders[2]

    # summary = "\n"
    # summary += "The largest lineage is {lineage}.\n".format(lineage=largest_lineage)
    # summary += "The cluster ID for this lineage is {id}.\n".format(
    #     id=largest_cluster_id
    # )
    # summary += "{lineage} is observed in {num_geo} {geo}.\n".format(
    #     lineage=largest_lineage, num_geo=len(largest_df), geo=geo
    # )

    # for rec in largest_df.iterrows():
    #     region = rec[1][geo]
    #     sequences = rec[1]["sequences"]
    #     summary += "  - {region} ({sequences})\n".format(
    #         region=region, sequences=sequences
    #     )

    # body.text = summary

    # # ---------------------------------------------------------------------
    # # Parents Summary

    # if os.path.exists(parents_plot):

    #     graph_slide_layout = presentation.slide_layouts[8]
    #     slide = presentation.slides.add_slide(graph_slide_layout)
    #     title = slide.shapes.title

    #     title.text_frame.text = "Parents"
    #     title.text_frame.paragraphs[0].font.bold = True

    #     chart_placeholder = slide.placeholders[1]
    #     chart_placeholder.insert_picture(parents_plot)
    #     body = slide.placeholders[2]

    #     summary = "\n"
    #     summary += "There are {num} parental combinations.\n".format(
    #         num=len(parents_df)
    #     )

    #     for rec in parents_df.iterrows():
    #         parents = rec[1]["parents"]
    #         sequences = rec[1]["sequences"]
    #         summary += "  - {parents} ({sequences})\n".format(
    #             parents=parents, sequences=sequences
    #         )

    #     # Adjust font size of body
    #     body.text_frame.text = summary
    #     for paragraph in body.text_frame.paragraphs:
    #         for run in paragraph.runs:
    #             run.font.size = pptx.util.Pt(14)

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
