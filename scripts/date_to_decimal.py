#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
import sys


def decimal_date(date):
    """
    Convert datetime (%Y-%m-%d) to decimal date.
    Credit: Matthias Fripp
    Source: https://stackoverflow.com/a/36949905
    """
    # if type(date) != str:
    #    return "?"

    try:
        date = datetime.strptime(date, "%Y-%m-%d")
    except (ValueError, TypeError) as error:
        # nan vals will be flagged as a TypeError
        if type(error) == TypeError:
            return "?"
        try:
            date = datetime.strptime(date, "%Y-%m")
        except ValueError:
            try:
                date = datetime.strptime(date, "%Y")
            except ValueError:
                return "?"

        decimal_date = float(date.year)
        return decimal_date

    date_ord = date.toordinal()
    year_start = datetime(date.year, 1, 1).toordinal()
    year_end = datetime(date.year + 1, 1, 1).toordinal()
    year_length = year_end - year_start
    year_fraction = float(date_ord - year_start) / year_length
    decimal_date = date.year + year_fraction
    return decimal_date


if __name__ == "__main__":
    df_path = sys.argv[1]
    df_out_path = sys.argv[2]
    df = pd.read_csv(df_path, sep="\t", low_memory=False, encoding="unicode_escape")

    if "date" in df.columns:
        df["num_date"] = [decimal_date(d) for d in df["date"]]

    df.to_csv(df_out_path, sep="\t", index=False)
