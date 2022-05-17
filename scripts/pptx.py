#!/usr/bin/env python3
import click

# import pptx
# import pandas as pd
# import numpy as np
# from datetime import date
# import matplotlib.pyplot as plt
# import seaborn as sns

NO_DATA_CHAR = "NA"


@click.command()
@click.option("--linelist", help="Linelist of recombinant sequences", required=True)
def main(
    linelist,
):
    """Create a powerpoint report"""
    print(linelist)


if __name__ == "__main__":
    main()
