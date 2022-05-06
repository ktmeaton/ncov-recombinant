#!/usr/bin/env python3

import click
import pandas as pd
import json
import os


@click.command()
@click.option(
    "--lat-longs",
    help="ncov lat_longs.tsv",
    required=False,
    default="ncov/defaults/lat_longs.tsv",
)
def main(lat_longs):
    """Create a JSON of geo_resolutions from ncov lat_longs.tsv."""

    lat_longs_df = pd.read_csv(lat_longs, sep="\t", header=None)
    lat_longs_df.columns = ["resolution", "name", "latitude", "longitude"]

    resolutions = set(lat_longs_df["resolution"])

    geo_resolutions = []

    for res in resolutions:
        demes_dict = {}

        res_df = lat_longs_df[lat_longs_df["resolution"] == res]
        for rec in res_df.iterrows():
            name = rec[1]["name"]
            demes_dict[name] = {}
            demes_dict[name]["latitude"] = rec[1]["latitude"]
            demes_dict[name]["longitude"] = rec[1]["longitude"]

        # Manual edits
        if res == "country":
            demes_dict["England"] = {}
            demes_dict["England"]["latitude"] = 52.405994
            demes_dict["England"]["longitude"] = -1.671707

        res_dict = {"key": res, "demes": demes_dict}
        geo_resolutions.append(res_dict)

    # Manual edits

    geo_resolutions_json = json.dumps(geo_resolutions, indent=2)

    # Write Output
    out_path = os.path.join("resources", "geo_resolutions.json")
    with open(out_path, "w") as outfile:
        outfile.write(geo_resolutions_json)


if __name__ == "__main__":
    main()
