## Tutorial

> **Tip**: Remember to run `conda activate ncov-recombinant` first!

1. Preview the steps that are going to be run.

    ```bash
    snakemake --profile profiles/tutorial --dryrun
    ```

1. Run the workflow.

    ```bash
    snakemake --profile profiles/tutorial
    ```

1. Explore the <a href="output.html">Output</a>.

    - Slides | `results/tutorial/report/report.pptx`
    - Tables<sup>*</sup> | `results/tutorial/report/report.xlsx`
    - Plots
        - Reporting Period (default: last 16 weeks): `results/tutorial/plots`
        - All sequences: `results/tutorial/plots_historical`
    - Breakpoints
        - By parental clade: `results/tutorial/plots_historical/breakpoints_clade.png`
        - By parental lineage: `results/tutorial/plots_historical/breakpoints_lineage.png`
    - Alleles <sup>†</sup> | `results/tutorial/sc2rf/recombinants.ansi.txt`

<sup>*</sup> Individual tables are available as TSV linelists in `results/tutorial/linelists`.  
<sup>†</sup> Visualize sc2rf mutations with `less -S` or [Visual Studio ANSI Colors](https://marketplace.visualstudio.com/items?itemName=iliazeus.vscode-ansi).  
