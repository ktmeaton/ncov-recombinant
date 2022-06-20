#!/usr/bin/env python3
import click
import pandas as pd
import logging
import sys
import os

NO_DATA_CHAR = "NA"


def create_logger(log):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    if log:
        fh = logging.FileHandler(log)
    else:
        fh = logging.StreamHandler(sys.stdout)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    return logger


@click.command()
@click.option("--input", help="Input report (xlsx)", required=True)
@click.option("--output", help="Output report (xlsx)", required=True)
@click.option("--cols", help="Columns (csv) to redact", required=True)
@click.option("--log", help="Logfile.", required=False)
def main(
    input,
    output,
    cols,
    log,
):
    """Redact columns from report tables."""
    outdir = os.path.dirname(output)
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # Create Logger
    logger = create_logger(log)

    # parsse columns to redact
    cols = cols.split(",")

    # Not specifiying a sheet name loads all tables
    df_dict = pd.read_excel(input, sheet_name=None)

    with pd.ExcelWriter(output) as excel_writer:

        for table in df_dict:

            table_df = df_dict[table]

            logger.info("Parsing table: {}".format(table))
            for col in cols:
                if col in table_df.columns:
                    logger.info("\tRedacting column: {}".format(col))
                    table_df.drop(columns=[col], inplace=True)

            table_df.to_excel(excel_writer, sheet_name=table)

    logger.info("Successfully created redacted report: {}".format(output))


if __name__ == "__main__":
    main()
