#!/usr/bin/env python3
import click
import pptx
from datetime import date
import os
import pandas as pd
import re


NO_DATA_CHAR = "NA"
TITLE = "SARS-CoV-2 Recombinants"
FONT_SIZE_PARAGRAPH = 20

# designated: X*
# proposed: proposed* or associated issue
# unpublished: not designated or proposed

RECOMBINANT_STATUS = {
    "designated": "X.*",
    "proposed": "proposed.*",
    "unpublished": "misc.*",
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
@click.option("--output", help="Output PPTX path", required=True)
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
    output,
):
    """Create a report of powerpoint slides"""

    # Parse build name from plot_dir path

    build = os.path.basename(os.path.dirname(plot_dir))
    outdir = os.path.dirname(output)
    if not os.path.exists(outdir):
        os.mkdir(outdir)
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

        # Largest is special, as it takes the form largest_<lineage>_<cluster_id>.*
        if label.startswith("largest_"):

            largest_lineage = label.split("_")[1]
            largest_cluster_id = label.split("_")[2].replace("-DELIM-","/")

            plot_dict["largest"] = plot_dict[label]
            plot_dict["largest"]["lineage"] = largest_lineage
            plot_dict["largest"]["cluster_id"] = largest_cluster_id

            del plot_dict[label]

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
    lineage_df = plot_dict["lineage"]["df"]
    lineages = list(lineage_df.columns)
    lineages.remove("epiweek")

    status_counts = {}
    status_df = plot_dict["status"]["df"]
    statuses = list(status_df.columns)
    statuses.remove("epiweek")

    for status in statuses:

        status_counts[status.lower()] = {
            "sequences" : 0,
            "lineages" : 0,
        }

        if status.lower() in RECOMBINANT_STATUS:
            regex = RECOMBINANT_STATUS[status.lower()]       
            for lineage in lineages:
                if re.match(regex, lineage):

                    seq_count = sum(lineage_df[lineage].dropna())
    
                    status_counts[status.lower()]["sequences"] += int(seq_count)
                    status_counts[status.lower()]["lineages"] += 1

    # Number of lineages and sequences
    num_lineages  = int(sum([status_counts[s]["lineages"] for s in status_counts]))
    num_sequences = int(sum([status_counts[s]["sequences"] for s in status_counts]))

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
        num_lineages=num_lineages
    )
    for status in RECOMBINANT_STATUS:
        if status in status_counts:
            count = status_counts[status]["lineages"]
        else:
            count = 0
        summary += "  - {lineages} lineages are {status}.\n".format(
            lineages=count, status=status
        )
    summary += "\n"
    summary += "There are {num_sequences} recombinant sequences.\n".format(
        num_sequences=num_sequences
    )
    for status in RECOMBINANT_STATUS:
        summary += "  - {sequences} sequences are {status}.\n".format(
            sequences=status_counts[status]["sequences"], status=status
        )
        
    body.text_frame.text = summary

    # Adjust font size of body    
    for paragraph in body.text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.size = pptx.util.Pt(14)

    # ---------------------------------------------------------------------
    # Geographic Summary

    plot_path = plot_dict["geography"]["plot_path"]
    geo_df = plot_dict["geography"]["df"]
    geos = list(geo_df.columns)
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

    for region in geos:
        seq_count = int(sum(geo_df[region].dropna()))
        summary += "  - {region} ({seq_count})\n".format(
            region=region, seq_count=seq_count
        )

    body.text_frame.text = summary

    # Adjust font size of body    
    for paragraph in body.text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.size = pptx.util.Pt(14)

    # ---------------------------------------------------------------------
    # Designated Summary

    plot_path = plot_dict["designated"]["plot_path"]
    designated_df = plot_dict["designated"]["df"]

    designated_lineages = list(designated_df.columns)
    designated_lineages.remove("epiweek")
    num_designated = len(designated_lineages)

    graph_slide_layout = presentation.slide_layouts[8]
    slide = presentation.slides.add_slide(graph_slide_layout)
    title = slide.shapes.title

    title.text_frame.text = "Designated"
    title.text_frame.paragraphs[0].font.bold = True

    chart_placeholder = slide.placeholders[1]
    chart_placeholder.insert_picture(plot_path)
    body = slide.placeholders[2]

    summary = "\n"
    summary += "There are {num_designated} designated lineage.\n".format(
        num_designated=num_designated
    )

    for lineage in designated_lineages:
        seq_count = int(sum(designated_df[lineage].dropna()))
        summary += "  - {lineage} ({seq_count})\n".format(
            lineage=lineage, seq_count=seq_count
        )

    body.text_frame.text = summary

    # Adjust font size of body    
    for paragraph in body.text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.size = pptx.util.Pt(14)

    # ---------------------------------------------------------------------
    # Largest Summary

    plot_path = plot_dict["largest"]["plot_path"]
    largest_df = plot_dict["largest"]["df"]
    
    largest_geos = list(largest_df.columns)
    largest_geos.remove("epiweek")
    num_geos = len(largest_geos)    

    largest_lineage = plot_dict["largest"]["lineage"]
    largest_lineage_size = 0
    largest_cluster_id = plot_dict["largest"]["cluster_id"]

    for lineage in lineages:
        seq_count = int(sum(lineage_df[lineage].dropna()))
        if seq_count > largest_lineage_size:
            largest_lineage_size = seq_count

    graph_slide_layout = presentation.slide_layouts[8]
    slide = presentation.slides.add_slide(graph_slide_layout)
    title = slide.shapes.title

    title.text_frame.text = "Largest"
    title.text_frame.paragraphs[0].font.bold = True

    chart_placeholder = slide.placeholders[1]
    chart_placeholder.insert_picture(plot_path)
    body = slide.placeholders[2]

    summary = "\n"
    summary += "The largest lineage is {lineage} (N={size}).\n".format(
        lineage=largest_lineage,
        size=largest_lineage_size,
        )

    summary += "The cluster ID for this lineage is {id}.\n".format(
        id=largest_cluster_id
    )
    summary += "{lineage} is observed in {num_geo} {geo}.\n".format(
        lineage=largest_lineage, num_geo=num_geos, geo=geo
    )  

    for region in largest_geos:
        seq_count = int(sum(largest_df[region].dropna()))
        summary += "  - {region} ({seq_count})\n".format(
            region=region, seq_count=seq_count
        )

    body.text_frame.text = summary

    # Adjust font size of body    
    for paragraph in body.text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.size = pptx.util.Pt(14)


    # ---------------------------------------------------------------------
    # Parents Summary

    plot_path = plot_dict["parents"]["plot_path"]
    parents_df = plot_dict["parents"]["df"]
    
    parents = list(parents_df.columns)
    parents.remove("epiweek")
    num_parents = len(parents)  

    graph_slide_layout = presentation.slide_layouts[8]
    slide = presentation.slides.add_slide(graph_slide_layout)
    title = slide.shapes.title

    title.text_frame.text = "Parents"
    title.text_frame.paragraphs[0].font.bold = True

    chart_placeholder = slide.placeholders[1]
    chart_placeholder.insert_picture(plot_path)
    body = slide.placeholders[2]

    summary = "\n"
    summary += "There are {num_parents} parental combinations.\n".format(
        num_parents=num_parents
    )


    for parent in parents:
        seq_count = int(sum(parents_df[parent].dropna()))
        summary += "  - {parent} ({seq_count})\n".format(
            parent=parent, seq_count=seq_count
        )

    body.text_frame.text = summary

    # Adjust font size of body    
    for paragraph in body.text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.size = pptx.util.Pt(14)

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
    presentation.save(output)


if __name__ == "__main__":
    main()
