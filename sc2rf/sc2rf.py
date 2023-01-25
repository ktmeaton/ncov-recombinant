#!/usr/bin/env python3

import csv
import enum
from typing import NamedTuple
from termcolor import colored, cprint
import json
import argparse
import os
import requests
from tqdm import tqdm
import urllib.parse
import itertools


colors = ["red", "green", "blue", "yellow", "magenta", "cyan"]

width_override = None

# I removed "ORF" from the names, because often we only see the first one or two letters of a name, and "ORF" provides no information
genes = {
    "1a": (266, 13468),
    "1b": (13468, 21555),
    "S": (21563, 25384),
    "E": (26245, 26472),
    "3a": (25393, 26220),
    "M": (26523, 27191),
    "6": (27202, 27387),
    "7a": (27394, 27759),
    "7b": (27756, 27887),
    "8": (27894, 28259),
    "N": (
        28274,
        28283,
    ),  # my algorithm does not like that ORF9b is inside N, so I split N in two halves
    "9b": (28284, 28577),
    "N": (28578, 29533),
    "": (29534, 99999),  # probably nothing, but need something to mark the end of N
}


class Interval:
    """An interval of integers, e.g., 27, 27-, -30 or 27-30"""

    def __init__(self, string):
        # TODO allow multiple separators, see https://stackoverflow.com/questions/1059559/split-strings-into-words-with-multiple-word-boundary-delimiters
        self.original_string = string
        parts = string.split("-")
        if len(parts) == 1:
            self.min = int(parts[0])
            self.max = int(parts[0])
        elif len(parts) == 2:
            self.min = int(parts[0]) if parts[0] else None
            self.max = int(parts[1]) if parts[1] else None
        else:
            raise ValueError("invalid interval: " + string)

    def matches(self, num):
        """check if num is within closed interval"""
        if self.min and num < self.min:
            return False
        if self.max and num > self.max:
            return False

        return True

    def __str__(self):
        return self.original_string


def main():
    """Command line interface"""
    global mappings
    global width_override
    global dot_character

    dot_character = "•"

    # This strange line should enable handling of
    # ANSI / VT 100 codes in windows terminal
    # See https://stackoverflow.com/a/39675059/39946
    os.system("")

    parser = argparse.ArgumentParser(
        description="Analyse SARS-CoV-2 sequences for potential, unknown recombinant variants.",
        epilog='An Interval can be a single number ("3"), a closed interval ("2-5" ) or an open one ("4-" or "-7").'
        " The limits are inclusive. Only positive numbers are supported.",
        formatter_class=ArgumentAdvancedDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input", nargs="*", help="input sequence(s) to test, as aligned .fasta file(s)"
    )
    parser.add_argument(
        "--primers",
        nargs="*",
        metavar="PRIMER",
        help="Filenames of primer set(s) to visualize. The .bed formats for ARTIC and EasySeq are recognized and supported.",
    )
    parser.add_argument(
        "--primer-intervals",
        nargs="*",
        metavar="INTERVAL",
        type=Interval,
        help="Coordinate intervals in which to visualize primers.",
    )
    parser.add_argument(
        "--parents",
        "-p",
        default="2-4",
        metavar="INTERVAL",
        type=Interval,
        help="Allowed number of potential parents of a recombinant.",
    )
    parser.add_argument(
        "--breakpoints",
        "-b",
        default="1-4",
        metavar="INTERVAL",
        type=Interval,
        help="Allowed number of breakpoints in a recombinant.",
    )
    parser.add_argument(
        "--clades",
        "-c",
        nargs="*",
        default=["20I", "20H", "20J", "21I", "21J", "BA.1", "BA.2", "BA.3"],
        help='List of variants which are considered as potential parents. Use Nextstrain clades (like "21B"), or Pango Lineages (like "B.1.617.1") or both. Also accepts "all".',
    )
    parser.add_argument(
        "--unique",
        "-u",
        default=2,
        type=int,
        metavar="NUM",
        help="Minimum of substitutions in a sample which are unique to a potential parent clade, so that the clade will be considered.",
    )
    parser.add_argument(
        "--max-intermission-length",
        "-l",
        metavar="NUM",
        default=2,
        type=int,
        help="The maximum length of an intermission in consecutive substitutions. Intermissions are stretches to be ignored when counting breakpoints.",
    )
    parser.add_argument(
        "--max-intermission-count",
        "-i",
        metavar="NUM",
        default=8,
        type=int,
        help="The maximum number of intermissions which will be ignored. Surplus intermissions count towards the number of breakpoints.",
    )
    parser.add_argument(
        "--max-name-length",
        "-n",
        metavar="NUM",
        default=30,
        type=int,
        help="Only show up to NUM characters of sample names.",
    )
    parser.add_argument(
        "--max-ambiguous",
        "-a",
        metavar="NUM",
        default=50,
        type=int,
        help="Maximum number of ambiguous nucs in a sample before it gets ignored.",
    )
    parser.add_argument(
        "--force-all-parents",
        "-f",
        action="store_true",
        help="Force to consider all clades as potential parents for all sequences. Only useful for debugging.",
    )
    parser.add_argument(
        "--select-sequences",
        "-s",
        default="0-999999",
        metavar="INTERVAL",
        type=Interval,
        help="Use only a specific range of input sequences. DOES NOT YET WORK WITH MULTIPLE INPUT FILES.",
    )
    parser.add_argument(
        "--enable-deletions",
        "-d",
        action="store_true",
        help="Include deletions in lineage comparision.",
    )
    parser.add_argument(
        "--show-private-mutations",
        action="store_true",
        help="Display mutations which are not in any of the potential parental clades.",
    )
    parser.add_argument(
        "--rebuild-examples",
        "-r",
        action="store_true",
        help="Rebuild the mutations in examples by querying cov-spectrum.org.",
    )
    parser.add_argument(
        "--mutation-threshold",
        "-t",
        metavar="NUM",
        default=0.75,
        type=float,
        help="Consider mutations with a prevalence of at least NUM as mandatory for a clade (range 0.05 - 1.0, default: %(default)s).",
    )
    parser.add_argument(
        "--add-spaces",
        metavar="NUM",
        nargs="?",
        default=0,
        const=5,
        type=int,
        help="Add spaces between every N colums, which makes it easier to keep your eye at a fixed place.",
    )
    parser.add_argument(
        "--sort-by-id",
        metavar="NUM",
        nargs="?",
        default=0,
        const=999,
        type=int,
        help="Sort the input sequences by the ID. If you provide NUM, only the first NUM characters are considered. Useful if this correlates with meaning full meta information, e.g. the sequencing lab.",
    )
    # parser.add_argument('--sort-by-first-breakpoint', action='store_true', help='Does what it says.')
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print some more information, mostly useful for debugging.",
    )
    parser.add_argument(
        "--ansi",
        action="store_true",
        help="Use only ASCII characters to be compatible with ansilove.",
    )
    parser.add_argument("--update-readme", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--hide-progress",
        action="store_true",
        help="Don't show progress bars during long task.",
    )
    parser.add_argument(
        "--csvfile",
        type=argparse.FileType("w"),
        help="Path to write results in CSV format.",
    )
    parser.add_argument(
        "--ignore-shared",
        action="store_true",
        help="Ignore substitutions that are shared between all parents.",
    )
    parser.add_argument(
        "--gisaid-access-key",
        help="covSPECTRUM accessKey for GISAID data.",
    )

    sc2rf_dir = os.path.dirname(os.path.realpath(__file__))

    global args
    args = parser.parse_args()

    mapping_path = os.path.join(sc2rf_dir, "mapping.csv")
    mappings = read_mappings(mapping_path)

    if args.ansi:
        dot_character = "."

    if args.update_readme:
        update_readme(parser)
        print("Readme was updated. Program exits.")
        return

    if args.rebuild_examples:
        rebuild_examples()
        if len(args.input) == 0:
            print(
                "Examples were rebuilt, and no input sequences were provided. Program exits."
            )
            return
    elif len(args.input) == 0:
        print(
            "Input sequences must be provided, except when rebuilding the examples. Use --help for more info. Program exits."
        )
        return

    if args.mutation_threshold < 0.05 or args.mutation_threshold > 1.0:
        print("mutation-threshold must be between 0.05 and 1.0")
        return

    global reference
    vprint("Reading reference genome, lineage definitions...")
    reference_path = os.path.join(sc2rf_dir, "reference.fasta")
    reference = read_fasta(reference_path, None)["MN908947 (Wuhan-Hu-1/2019)"]

    virus_properties_path = os.path.join(sc2rf_dir, "virus_properties.json")
    all_examples = read_examples(virus_properties_path)

    used_examples = []
    if "all" in args.clades:
        used_examples = all_examples
    else:
        # screen for a subset of examples only
        for example in all_examples:
            if (
                len(example["NextstrainClade"])
                and example["NextstrainClade"] in args.clades
            ):
                used_examples.append(example)
            elif (
                len(example["PangoLineage"]) and example["PangoLineage"] in args.clades
            ):
                used_examples.append(example)

    if args.force_all_parents and not args.parents.matches(len(used_examples)):
        print(
            "The number of allowed parents, the number of selected clades and the --force-all-parents conflict so that the results must be empty."
        )
        return

    vprint("Done.\nReading actual input.")
    all_samples = dict()
    for path in args.input:
        read_samples = read_subs_from_fasta(path)
        for key, val in read_samples.items():
            all_samples[key] = val  # deep copy
    vprint("Done.")

    global primer_sets
    primer_sets = dict()
    if args.primers:
        vprint("Reading primers.")
        for path in args.primers:
            pools = read_bed(path)
            primer_sets[path] = pools
        vprint("Done.")

    calculate_relations(used_examples)

    # lists of samples keyed by tuples of example indices
    match_sets = dict()

    vprint("Scanning input for matches against lineage definitons...")
    for sa_name, sa in my_tqdm(all_samples.items(), desc="First pass scan"):
        matching_example_indices = []
        if args.force_all_parents:
            matching_example_indices = range(0, len(used_examples))
        else:
            for i, ex in enumerate(used_examples):
                matches_count = len(sa["subs_set"] & ex["unique_subs_set"])
                # theoretically > 0 already gives us recombinants, but they are much
                # more likely to be errors or coincidences
                if matches_count >= args.unique:
                    matching_example_indices.append(i)

        matching_examples_tup = tuple(matching_example_indices)

        if args.parents.matches(len(matching_example_indices)):
            # print(f"{sa_name} is a possible recombinant of {len(matching_example_names)} lineages: {matching_example_names}")
            if match_sets.get(matching_examples_tup):
                match_sets[matching_examples_tup].append(sa)
            else:
                match_sets[matching_examples_tup] = [sa]

    vprint("Done.\nPrinting detailed analysis:\n\n")

    # Write the headers to output csv file
    writer = None
    if args.csvfile:
        fieldnames = [
            "sample",
            "examples",
            "intermissions",
            "breakpoints",
            "regions",
            "unique_subs",
            "alleles",
        ]
        if args.show_private_mutations:
            fieldnames.append("privates")
        writer = csv.DictWriter(args.csvfile, fieldnames=fieldnames)
        writer.writeheader()

    # Write the data to the output csv file
    if len(match_sets):

        for matching_example_indices, samples in match_sets.items():
            show_matches(
                [used_examples[i] for i in matching_example_indices],
                samples,
                writer=writer,
            )
    else:
        print("First pass found no potential recombinants, see ")


def my_tqdm(*margs, **kwargs):
    return tqdm(
        *margs, delay=0.1, colour="green", disable=bool(args.hide_progress), **kwargs
    )


def update_readme(parser: argparse.ArgumentParser):
    # on wide monitors, github displays up to 90 columns of preformatted text
    # but 10% of web users have screens which can only fit 65 characters
    global width_override
    width_override = 65

    help = parser.format_help()

    new_lines = []

    between_markers = False

    with open("README.md", "rt") as old_readme:
        for line in old_readme:
            if line.strip() == "<!-- BEGIN_MARKER -->":
                between_markers = True
                new_lines.append("<!-- BEGIN_MARKER -->\n")

            if line.strip() == "<!-- END_MARKER -->":
                between_markers = False
                new_lines.append("```\n")
                new_lines.append(help + "\n")
                new_lines.append("```\n")

            if not between_markers:
                new_lines.append(line)

    with open("README.md", "wt") as new_readme:
        new_readme.writelines(new_lines)


def vprint(text: str):
    if args.verbose:
        print(text)


def rebuild_examples():
    print("Rebuilding examples from cov-spectrum.org...")
    with open("virus_properties.json", newline="", mode="w") as jsonfile:

        the_list = []

        for variant_props in mappings["list"]:
            pango = variant_props["PangoLineage"]
            clade = variant_props["NextstrainClade"]
            who_label = variant_props["WhoLabel"]
            query = ""
            if variant_props["Query"]:
                query = (
                    f"?variantQuery={urllib.parse.quote_plus(variant_props['Query'])}"
                )
            elif pango and len(pango) > 0:
                query = f"?nextcladePangoLineage={pango}*"
            # WHO Labels were deprecated in cov-spectrum #546
            # elif clade and len(clade) > 0 and who_label:
            #     query = f"?nextstrainClade={clade}%20({who_label})"
            # elif clade and len(clade) > 0 and not who_label:
            #     query = f"?nextstrainClade={clade}"
            elif clade and len(clade) > 0:
                query = f"?nextstrainClade={clade}"
            else:
                print("Variant has neither pango nor clade, check out mapping.csv!")
                continue

            print(f"Fetching data for {query}")
            if args.gisaid_access_key == None:
                url = f"https://lapis.cov-spectrum.org/open/v1/sample/nuc-mutations{query}&minProportion=0.05"
            else:
                url = f"https://lapis.cov-spectrum.org/gisaid/v1/sample/nuc-mutations{query}&minProportion=0.05&accessKey={args.gisaid_access_key}"
            print(f"Url is {url}")

            r = requests.get(url)
            result = r.json()
            if len(result["errors"]):
                print("Errors occured while querying cov-spectrum.org:")
                for e in result["errors"]:
                    print("    " + e)

            variant = variant_props.copy()
            variant["mutations"] = result["data"]

            names = [who_label, pango, clade]
            names = [n for n in names if n is not None and len(n.strip()) > 0]
            variant["name"] = " / ".join(names)

            the_list.append(variant)

        props = {
            "schemaVersion": "s2r 0.0.2",
            "comment": "New file format, no longer looks like the original virus_properties.json",
            "variants": the_list,
        }

        json.dump(props, jsonfile, indent=4)
        print("Examples written to disk.")


def read_examples(path):
    with open(path, newline="") as jsonfile:
        props = json.load(jsonfile)
        assert props["schemaVersion"] == "s2r 0.0.2"
        examples = []
        for variant in props["variants"]:
            subs_dict = dict()
            for m in variant["mutations"]:
                if m["proportion"] < args.mutation_threshold:
                    continue
                sub_string = m["mutation"].strip()

                if len(sub_string) > 0:
                    sub = parse_sub(sub_string)
                    if (sub.mut != "-" or args.enable_deletions) and sub.mut != ".":
                        subs_dict[sub.coordinate] = sub
            example = {
                "name": variant["name"],
                "NextstrainClade": variant["NextstrainClade"],
                "PangoLineage": variant["PangoLineage"],
                "subs_dict": subs_dict,
                "subs_list": list(subs_dict.values()),
                "subs_set": set(subs_dict.values()),
                "missings": [],
            }

            examples.append(example)

        return examples


class Primer(NamedTuple):
    start: int
    end: int
    direction: str
    alt: bool
    name: str
    sequence: str


class Amplicon:
    left_primers: list
    right_primer: list
    number: int
    color: str
    start: int
    end: int

    def __init__(self, number: int):
        self.number = number
        self.left_primers = list()
        self.right_primers = list()
        self.color = get_color(number)
        self.start = None
        self.end = None
        self.amp_start = None
        self.amp_end = None

    def __str__(self):
        return f"Amplicon {self.number} ({self.start} to {self.end})"

    def add_primer(self, primer):
        if primer.direction == "+":
            self.left_primers.append(primer)
            if self.amp_start:
                self.amp_start = max(self.amp_start, primer.end + 1)
            else:
                self.amp_start = primer.end + 1
        else:
            self.right_primers.append(primer)
            if self.amp_end:
                self.amp_end = min(self.amp_end, primer.start - 1)
            else:
                self.amp_end = primer.start - 1

        if self.start:
            self.start = min(self.start, primer.start)
        else:
            self.start = primer.start

        if self.end:
            self.end = max(self.end, primer.end)
        else:
            self.end = primer.end

    def get_char(self, coord: int):
        if coord <= self.start or coord >= self.end:
            return " "

        for primer in self.left_primers:
            if primer.start <= coord and primer.end >= coord:
                if primer.alt:
                    return "{" if args.ansi else "‹"
                else:
                    return "<" if args.ansi else "«"

        for primer in self.right_primers:
            if primer.start <= coord and primer.end >= coord:
                if primer.alt:
                    return "}" if args.ansi else "›"
                else:
                    return ">" if args.ansi else "»"

        return "-"

    def overlaps_coord(self, coord: int, actual_amplicon: bool):
        if actual_amplicon:
            return coord >= self.amp_start and coord <= self.amp_end
        else:
            return coord >= self.start and coord <= self.end

    def overlaps_interval(self, interval: Interval):
        if interval.max and self.start > interval.max:
            return False
        if interval.min and self.end < interval.min:
            return False
        return True


def read_bed(path):
    pools = dict()
    index = 0
    current_name = None
    with open(path, newline="") as bed:
        for line in bed:
            parts = line.strip().split("\t")

            if parts[0] == parts[3]:  # EasySeq format
                name = parts[6]
                name_parts = name.split("_")
                amplicon_index = int(name_parts[1])
                amplicon = Amplicon(amplicon_index)
                left_primer = Primer(
                    start=int(parts[1]),
                    end=int(parts[2]),
                    name="left_" + str(amplicon_index),
                    alt=False,
                    direction="+",
                    sequence=None,
                )
                right_primer = Primer(
                    start=int(parts[4]),
                    end=int(parts[5]),
                    name="right_" + str(amplicon_index),
                    alt=False,
                    direction="-",
                    sequence=None,
                )
                amplicon.add_primer(left_primer)
                amplicon.add_primer(right_primer)

                pool_index = (amplicon_index + 1) % 2 + 1

                if not pools.get(pool_index):
                    pools[pool_index] = dict()

                pools[pool_index][amplicon_index] = amplicon

            else:
                # ARTIC format
                name = parts[3]
                name_parts = name.split("_")
                amplicon_index = int(name_parts[1])
                pool_index = parts[4]
                direction = parts[5]

                pool = pools.get(pool_index)
                if not pool:
                    pool = dict()
                    pools[pool_index] = pool

                amplicon = pool.get(amplicon_index)
                if not amplicon:
                    amplicon = Amplicon(amplicon_index)
                    pool[amplicon_index] = amplicon

                primer = Primer(
                    start=int(parts[1]),
                    end=int(parts[2]),
                    name=parts[3],
                    alt=len(name_parts) == 4,
                    direction=direction,
                    sequence=parts[6] if 6 < len(parts) else None,
                )

                amplicon.add_primer(primer)

    return pools


def read_fasta(path, index_range):
    """
    :param path:  str, absolute or relative path to FASTA file
    :param index_range:  Interval, select specific records from FASTA
    :return:  dict, sequences keyed by header
    """
    sequences = dict()
    index = 0
    current_name = None

    file_pos = 0
    with my_tqdm(
        total=os.stat(path).st_size, desc="Read " + path, unit_scale=True
    ) as pbar:
        with open(path, newline="") as fasta:
            current_sequence = ""
            for line in fasta:
                file_pos += len(line)
                pbar.update(file_pos - pbar.n)
                if line[0] == ">":
                    if current_name and (not index_range or index_range.matches(index)):
                        sequences[current_name] = current_sequence
                    index += 1
                    if index_range and index_range.max and index > index_range.max:
                        return sequences
                    current_sequence = ""
                    current_name = line[1:].strip()
                else:
                    current_sequence += line.strip().upper()
            sequences[current_name] = current_sequence

    return sequences


def read_subs_from_fasta(path):
    """
    Extract substitutions relative to reference genome.
    :param path:  str, path to input FASTA file
    :return:  dict, substitutions (as dict, list or set) keyed by genome name
    """
    fastas = read_fasta(path, args.select_sequences)
    sequences = dict()
    start_n = -1  # used for tracking runs of Ns or gaps
    removed_due_to_ambig = 0
    for name, fasta in my_tqdm(fastas.items(), desc="Finding mutations in " + path):
        subs_dict = dict()  # substitutions keyed by position
        missings = list()  # start/end tuples of N's or gaps
        coverage = list()  # inverse of missings, start/end tuples without N's or gaps

        # Coverage is always bases that are not "-" or "N", regardess of --enable-deletions
        no_cov_matches = ["N", "-"]

        # Missing can vary, depending on --enable-deletions
        missings_matches = ["N"]
        if not args.enable_deletions:
            missings_matches.append("-")

        if len(fasta) != len(reference):
            print(
                f"Sequence {name} not properly aligned, length is {len(fasta)} instead of {len(reference)}."
            )
        else:
            ambiguous_count = 0
            start_cov = 1
            for i in range(1, len(reference) + 1):
                r = reference[i - 1]
                s = fasta[i - 1]

                if s not in no_cov_matches:
                    coverage.append(i)

                if s in missings_matches:
                    missings.append(i)

                if r != s and s not in missings_matches:
                    subs_dict[i] = Sub(r, i, s)  # nucleotide substitution

                if not s in "AGTCN-":
                    ambiguous_count += 1  # count mixtures

            # Collapse bases into interval
            coverage = list(to_ranges(coverage))
            missings = list(to_ranges(missings))

            if ambiguous_count <= args.max_ambiguous:
                sequences[name] = {
                    "name": name,  # isn't this redundant?
                    "subs_dict": subs_dict,
                    "subs_list": list(subs_dict.values()),
                    "subs_set": set(subs_dict.values()),
                    "missings": missings,
                    "coverage": coverage,
                }
            else:
                removed_due_to_ambig += 1

    if removed_due_to_ambig:
        print(
            f"Removed {removed_due_to_ambig} of {len(fastas)} sequences with more than { args.max_ambiguous} ambiguous nucs."
        )

    return sequences


class Sub(NamedTuple):
    ref: str
    coordinate: int
    mut: str


def parse_sub(s):
    if s[0].isdigit():
        coordinate = int(s[0:-1])
        return Sub(reference[coordinate - 1], coordinate, s[-1])
    else:
        return Sub(s[0], int(s[1:-1]), s[-1])


def prunt(s, color=None):
    if color:
        cprint(s, color, end="")
    else:
        print(s, end="")


def fixed_len(s, l):
    trunc = s[0:l]
    return trunc.ljust(l)


def show_matches(examples, samples, writer):
    """
    Display results to screen
    :param examples:  list, dict for every variant reference genome with keys:
                      ['name', 'NextstrainClade', 'PangoLineage', 'subs_dict',
                      'subs_list', 'subs_set', 'missings', 'unique_subs_set']
    :param samples:  list, dict for every query genome, same structure as above
    :param writer:  csv.DictWriter, optional (defaults to None)
    """
    ml = args.max_name_length
    examples_str = ",".join([ex["name"] for ex in examples])

    if args.sort_by_id:
        samples.sort(key=lambda sample: sample["name"][: args.sort_by_id])

    # set union of mutations in all example genomes
    coords = set()
    for ex in examples:
        for sub in ex["subs_list"]:
            coords.add(sub.coordinate)

    private_coords = set()
    if args.show_private_mutations:
        # append mutations unique to sample genomes
        for sa in samples:
            for sub in sa["subs_list"]:
                # Check if this is a private mutation
                if sub.coordinate not in coords:
                    private_coords.add(sub.coordinate)

        # Add in the private mutations
        coords = coords.union(private_coords)

    if args.ignore_shared:
        filter_coords = set()
        for coord in coords:
            parents_matches = 0
            for ex in examples:
                # Store of list of substitutions coords for this example
                ex_coords = [sub.coordinate for sub in ex["subs_list"]]
                # check if the coord matches this parent
                if coord in ex_coords:
                    parents_matches += 1

            # Ignore this coord it if was found in all parents (except if there was only 1 parent)
            if parents_matches == len(examples) and len(examples) != 1:
                continue
            # Always add a definitive match or private
            elif parents_matches <= 1:
                filter_coords.add(coord)
            # Check if we're showing substitutions found in multiple parents
            elif parents_matches > 1 and not args.ignore_shared:
                filter_coords.add(coord)

        coords = filter_coords

    if args.primers:
        for name, primer_set in primer_sets.items():
            for pool in primer_set.values():
                for amplicon in pool.values():
                    if args.primer_intervals:
                        # check if amplicon should be shown at all, or if it's outside primer_intervals
                        amplicon_matches = False
                        for interval in args.primer_intervals:
                            if amplicon.overlaps_interval(interval):
                                amplicon_matches = True
                                break
                        if not amplicon_matches:
                            continue

                    # check if enough of the actual amplicon range is shown to display its number
                    name_len = len(str(amplicon.number))
                    matched_coords = 0
                    for coord in coords:
                        if amplicon.overlaps_coord(coord, True):
                            matched_coords += 1
                    if matched_coords < name_len:
                        coords.update(
                            range(amplicon.amp_start, amplicon.amp_start + name_len)
                        )

                    # make sure that every alt primer is shown for at least one coord
                    # otherwise mismatches in the primary primer may look as if they
                    # would not be compensated by an alt primer
                    for primer in amplicon.left_primers + amplicon.right_primers:
                        if primer.alt:
                            coords.add(primer.start)

                    # if amplicon.number == 76:
                    #     coords.update(range(amplicon.start, amplicon.end + 1))

    ordered_coords = list(coords)
    ordered_coords.sort()

    ordered_privates = list(private_coords)
    ordered_privates.sort()

    color_by_name = dict()
    color_index = 0
    for ex in examples:
        color_by_name[ex["name"]] = get_color(color_index)
        color_index += 1

    # This method works in a weird way: it pre-constructs the lines for the actual sequences,
    # and while it constructs the strings, it decides if they are worth showing at the same time.
    # Then, if at least one such string was collected, it prints the header lines for them, and after that the strings.

    ###### SHOW SAMPLES
    current_color = "grey"
    collected_outputs = []
    last_id = ""

    for sa in my_tqdm(
        samples, desc=f"Second pass scan for {[ex['name'] for ex in examples]}"
    ):
        # current_color = get_color(color_index)
        # color_by_name[sa['name']] = current_color

        prev_definitive_match = None
        breakpoints = 0
        definitives_since_breakpoint = 0
        definitives_count = []
        unique_subs = []
        alleles = []
        regions = []  # for CSV output
        privates = []
        last_coord = None

        if len(ordered_coords) == 0:
            continue
        else:
            start_coord = ordered_coords[0]

        output = ""

        output += fixed_len(sa["name"], ml) + " "

        for c, coord in enumerate(ordered_coords):

            matching_exs = []

            if args.add_spaces and c % args.add_spaces == 0:
                output += " "

            # -----------------------------------------------------------------
            # OPTION 1: MISSING DATA

            if is_missing(coord, sa["missings"]):
                # TBD: Is this always going to be an N?

                alleles.append("{}|{}|{}".format(coord, "Missing", "N"))
                output += colored("N", "white", attrs=["reverse"])

                # Did we find a matching example in the previous region?
                if prev_definitive_match:

                    # If we have recently seen a definitive, add to the counts
                    if definitives_since_breakpoint:
                        definitives_count.append(
                            (prev_definitive_match, definitives_since_breakpoint)
                        )

                    # Since we don't know the parent of missing, treat as a breakpoint
                    breakpoints += 1
                    regions.append((start_coord, last_coord, prev_definitive_match))
                    # Reset the previous match
                    prev_definitive_match = None
                    # Reset definitives count
                    definitives_since_breakpoint = 0

            # -----------------------------------------------------------------
            # OPTION 2: NON-MISSING DATA

            else:

                # -------------------------------------------------------------
                # OPTION 2a: Substitution

                if sa["subs_dict"].get(coord):

                    # Search for an example that matches this substitution
                    for ex in examples:
                        if (
                            ex["subs_dict"].get(coord)
                            and ex["subs_dict"].get(coord).mut
                            == sa["subs_dict"][coord].mut
                        ):
                            matching_exs.append(ex["name"])

                    # Initialize the formatting of the output base
                    text = sa["subs_dict"][coord].mut
                    fg = "white"
                    bg = None
                    attrs = ["bold"]

                    # If this is a terminal deletion, recode to N
                    if text == "-":

                        # Has there been coverage in prior coords?
                        # Just check the first tuple of coverage (beginning)
                        prev_terminal_deletion = True
                        first_cov_coord = sa["coverage"][0][0]
                        if first_cov_coord < coord:
                            prev_terminal_deletion = False

                        # Has there been coverage in proceeding coords?
                        # Just check the last tuple of coverage (end)
                        proc_terminal_deletion = True
                        last_cov_coord = sa["coverage"][-1][1]
                        if last_cov_coord > coord:
                            proc_terminal_deletion = False

                        if prev_terminal_deletion or proc_terminal_deletion:
                            text = "N"

                    # Check if this is an N
                    if text == "N":
                        alleles.append("{}|{}|{}".format(coord, "Missing", "N"))
                        fg = "white"
                        attrs = ["reverse"]

                    # none of the examples match - private mutation
                    elif len(matching_exs) == 0:
                        bg = "on_cyan"
                        privates.append(sa["subs_dict"].get(coord))
                        # Output the base, then skip to the next record
                        # ie. don't save the current coords as a last coord for breakpoints
                        alleles.append("{}|{}|{}".format(coord, "Private", text))
                        output += colored(text, fg, bg, attrs=attrs)
                        continue

                    # exactly one of the examples match - definite match
                    elif len(matching_exs) == 1:
                        unique_subs.append("{}|{}".format(coord, matching_exs[0]))
                        alleles.append("{}|{}|{}".format(coord, matching_exs[0], text))

                        fg = color_by_name[matching_exs[0]]

                        # If the previous region matched a different example, this is the start of a new parental region
                        if matching_exs[0] != prev_definitive_match:

                            if prev_definitive_match:
                                # record the previous parental region
                                regions.append(
                                    (start_coord, last_coord, prev_definitive_match)
                                )
                                # record a breakpoint
                                breakpoints += 1

                            # Record definitive substitutions observed in the previous region
                            if definitives_since_breakpoint:
                                definitives_count.append(
                                    (
                                        prev_definitive_match,
                                        definitives_since_breakpoint,
                                    )
                                )

                            # The current coordinate begins the new region
                            start_coord = coord
                            # The current example is the new parent
                            prev_definitive_match = matching_exs[0]
                            # Reset the definitives count to 0
                            definitives_since_breakpoint = 0

                        # Increment the counter of definitives
                        definitives_since_breakpoint += 1

                    # more than one, but not all examples match - can't provide proper color
                    elif len(matching_exs) < len(examples):
                        # bg = 'on_blue'
                        alleles.append(
                            "{}|{}|{}".format(coord, ";".join(matching_exs), text)
                        )
                        attrs = ["bold", "underline"]

                    # all examples match
                    else:
                        if args.ignore_shared:
                            continue
                        else:
                            alleles.append(
                                "{}|{}|{}".format(coord, ";".join(matching_exs), text)
                            )

                    output += colored(text, fg, bg, attrs=attrs)

                # -------------------------------------------------------------
                # Not a Substitution
                else:

                    # Find examples that have the reference allele
                    matching_exs = []
                    for ex in examples:
                        if not ex["subs_dict"].get(coord):
                            matching_exs.append(ex["name"])

                    text = dot_character
                    fg = "white"
                    bg = None
                    attrs = []
                    ref_allele = reference[coord - 1]

                    # Option 1: none of the examples match - private reverse mutation
                    if len(matching_exs) == 0:
                        alleles.append("{}|{}|{}".format(coord, "Private", ref_allele))
                        bg = "on_magenta"

                    elif len(matching_exs) == 1:
                        # exactly one of the examples match - definite match
                        alleles.append(
                            "{}|{}|{}".format(coord, matching_exs[0], ref_allele)
                        )
                        fg = color_by_name[matching_exs[0]]
                        # If we haven't found a definitive match yet, this is the start coord
                        if not prev_definitive_match:
                            start_coord = coord

                        if matching_exs[0] != prev_definitive_match:
                            if prev_definitive_match:
                                breakpoints += 1
                                regions.append(
                                    (start_coord, last_coord, prev_definitive_match)
                                )
                                start_coord = coord  # start of a new region

                            if definitives_since_breakpoint:
                                definitives_count.append(
                                    (
                                        prev_definitive_match,
                                        definitives_since_breakpoint,
                                    )
                                )

                            prev_definitive_match = matching_exs[0]
                            definitives_since_breakpoint = 0

                        definitives_since_breakpoint += 1

                    elif len(matching_exs) < len(examples):
                        # more than one, but not all examples match - can't provide proper color
                        # bg = 'on_yellow'
                        attrs = ["underline"]
                        # Output the base, then skip to the next record
                        # ie. don't save the current coords as a last coord for breakpoints
                        alleles.append(
                            "{}|{}|{}".format(coord, ";".join(matching_exs), ref_allele)
                        )
                        output += colored(text, fg, bg, attrs=attrs)
                        continue

                    else:
                        # all examples match (which means this is a private mutation in another sample)
                        # Output the base, then skip to the next record
                        # ie. don't save the current coords as a last coord for breakpoints
                        alleles.append(
                            "{}|{}|{}".format(coord, ";".join(matching_exs), ref_allele)
                        )
                        output += colored(text, fg, bg, attrs=attrs)
                        continue

                    output += colored(text, fg, bg, attrs=attrs)

            last_coord = coord  # save current coord before iterating to next

        # Finish iterating through all coords for a sample

        # output last region, if it wasn't missing
        if prev_definitive_match:
            regions.append((start_coord, last_coord, prev_definitive_match))

        if definitives_since_breakpoint:
            definitives_count.append(
                (prev_definitive_match, definitives_since_breakpoint)
            )

        # now transform definitive streaks: every sequence like ..., X, S, Y, ... where S is a small numer into ..., (X+Y), ...

        reduced = list(
            filter(
                lambda ex_count: ex_count[1] > args.max_intermission_length,
                definitives_count,
            )
        )
        num_intermissions = len(definitives_count) - len(reduced)

        further_reduced = []

        if len(reduced):
            last_ex = reduced[0][0]
            last_count = 0
            for (ex, count) in reduced:
                if ex != last_ex:
                    further_reduced.append(last_count)
                    last_count = count
                    last_ex = ex
                else:
                    last_count += count
            if last_count:
                further_reduced.append(last_count)

        postfix = ""
        num_breakpoints = len(further_reduced) - 1
        if num_intermissions > args.max_intermission_count:
            postfix = "/" + str(num_intermissions)
            num_breakpoints += (num_intermissions - args.max_intermission_count) * 2
            num_intermissions = args.max_intermission_count

        output += f" {num_breakpoints} BP"
        if num_intermissions:
            output += (
                f", {num_intermissions}{postfix} I <= {args.max_intermission_length}"
            )

        if args.breakpoints.matches(num_breakpoints):
            if (
                args.sort_by_id
                and args.sort_by_id != 999
                and last_id
                != sa["name"][: args.sort_by_id]
                != last_id[: args.sort_by_id]
            ):
                collected_outputs.append("---")

            last_id = sa["name"]
            collected_outputs.append(output)
            if writer:
                row = {
                    "sample": last_id,
                    "examples": examples_str.replace(" ", ""),
                    "intermissions": num_intermissions,
                    "breakpoints": num_breakpoints,
                    "regions": ",".join(
                        [
                            f"{start}:{stop}|{ex.replace(' ', '')}"
                            for start, stop, ex in regions
                        ]
                    ),
                    "unique_subs": ",".join(unique_subs).replace(" ", ""),
                    "alleles": ",".join(alleles).replace(" ", ""),
                }
                if args.show_private_mutations:
                    row.update(
                        {
                            "privates": ",".join(
                                [f"{ps.ref}{ps.coordinate}{ps.mut}" for ps in privates]
                            )
                        }
                    )
                writer.writerow(row)

    if len(collected_outputs) == 0:
        print(
            f"\n\nSecond pass scan found no potential recombinants between {[ex['name'] for ex in examples]}.\n"
        )
    else:
        print(
            f"\n\nPotential recombinants between {[ex['name'] for ex in examples]}:\n"
        )

        ###### SHOW COORDS

        for exp in range(5, 0, -1):
            div = 10 ** (exp - 1)

            if exp == 5:
                prunt(fixed_len("coordinates", ml + 1))
            else:
                prunt(" " * (ml + 1))

            for c, coord in enumerate(ordered_coords):
                if args.add_spaces and c % args.add_spaces == 0:
                    prunt(" ")
                if coord // div > 0:
                    prunt((coord // div) % 10)
                else:
                    prunt(" ")
                # print(f"{coord} // {div} = {(coord//div)}")
            print()
        print()

        ###### SHOW GENES
        prunt(fixed_len("genes", ml + 1))

        current_name = ""
        color_index = 0
        current_color = get_color(color_index)
        text_index = 0

        for c, coord in enumerate(ordered_coords):
            for name, limits in genes.items():
                if coord >= limits[0] and coord <= limits[1]:
                    if current_name != name:
                        current_name = name
                        color_index += 1
                        current_color = get_color(color_index)
                        text_index = 0

            # Do this once or twice, depending on space insertion
            for i in range(1 + (args.add_spaces and c % args.add_spaces == 0)):
                char = " "
                if len(current_name) > text_index:
                    char = current_name[text_index]
                cprint(char, "grey", "on_" + current_color, end="")
                text_index += 1

        print(" ")

        if args.primers:
            ###### SHOW PRIMERS

            prunt("\n")
            for name, primer_set in primer_sets.items():
                for index, pool in primer_set.items():
                    prunt(fixed_len(f"{name}, pool {index}", ml + 1))

                    for c, coord in enumerate(ordered_coords):
                        char = " "
                        for amplicon in pool.values():

                            if args.primer_intervals:
                                amplicon_matches = False
                                for interval in args.primer_intervals:
                                    if amplicon.overlaps_interval(interval):
                                        amplicon_matches = True
                                        break
                                if not amplicon_matches:
                                    continue

                            if amplicon.overlaps_coord(coord, False):
                                char = amplicon.get_char(coord)
                                if current_name != str(amplicon.number):
                                    current_name = str(amplicon.number)
                                    text_index = 0
                                current_color = amplicon.color

                        if args.add_spaces and c % args.add_spaces == 0:
                            prunt(" ")

                        if char == "-" and len(current_name) > text_index:
                            char = current_name[text_index]
                            text_index += 1
                        cprint(char, current_color, end="")

                    print(" ")

                print()

        ###### SHOW REF

        prunt(fixed_len("ref", ml + 1))
        for c, coord in enumerate(ordered_coords):
            if args.add_spaces and c % args.add_spaces == 0:
                prunt(" ")
            prunt(reference[coord - 1])
        print()
        print()

        ###### SHOW EXAMPLES

        for ex in examples:
            current_color = color_by_name[ex["name"]]
            prunt(fixed_len(ex["name"], ml) + " ", current_color)
            for c, coord in enumerate(ordered_coords):
                if args.add_spaces and c % args.add_spaces == 0:
                    prunt(" ")
                if ex["subs_dict"].get(coord):
                    prunt(ex["subs_dict"][coord].mut, current_color)
                else:
                    prunt(dot_character)
            print()
        print()

        for output in collected_outputs:
            print(output)

        print()
        cprint(
            "made with Sc2rf - available at https://github.com/lenaschimmel/sc2rf",
            "white",
        )
        print()


def get_color(color_index):
    return colors[color_index % len(colors)]


def read_mappings(path):
    with open(path, newline="") as csvfile:
        mappings = {"by_clade": dict(), "by_lineage": dict(), "list": list()}
        reader = csv.DictReader(csvfile)
        line_count = 0
        for row in reader:
            if len(row["NextstrainClade"]):
                mappings["by_clade"][row["NextstrainClade"]] = row
            if len(row["PangoLineage"]):
                mappings["by_lineage"][row["PangoLineage"]] = row
            mappings["list"].append(row)
    return mappings


def read_subs(path, delimiter=",", max_lines=-1):
    with open(path, newline="") as csvfile:
        sequences = {}
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        line_count = 0
        for row in reader:
            subs_dict = dict()
            missings = list()
            for s in row["substitutions"].split(","):
                s = s.strip()
                if len(s) > 0:
                    sub = parse_sub(s)
                    subs_dict[sub.coordinate] = sub

            for m in row["missing"].split(","):
                m = m.strip()
                if len(m) > 0:
                    parts = m.split("-")
                    if len(parts) == 1:
                        missings.append((int(parts[0]), int(parts[0])))
                    else:
                        missings.append((int(parts[0]), int(parts[1])))

            sequences[row["seqName"]] = {
                "name": row["seqName"],
                "subs_dict": subs_dict,
                "subs_list": list(subs_dict.values()),
                "subs_set": set(subs_dict.values()),
                "missings": missings,
            }

            line_count += 1
            if max_lines != -1 and line_count == max_lines:
                break
    return sequences


def is_missing(coordinate, missings):
    for missing in missings:
        if coordinate >= missing[0] and coordinate <= missing[1]:
            return True
    return False


def calculate_relations(examples):
    """ """
    for example in examples:
        union = set()
        for other in examples:
            if other is not example:
                union = union | (other["subs_set"])
        example["unique_subs_set"] = example["subs_set"] - union
        unique_count = len(example["unique_subs_set"])
        color = None
        if unique_count < 5:
            color = "yellow"
        if unique_count < 3:
            color = "red"
        vprint(
            colored(
                f"Clade  {example['name']} has {len(example['subs_set'])} mutations, of which {unique_count} are unique.",
                color,
            )
        )


def to_ranges(iterable):
    """
    Credits: @luca, https://stackoverflow.com/a/43091576
    """
    iterable = sorted(set(iterable))
    for key, group in itertools.groupby(enumerate(iterable), lambda t: t[1] - t[0]):
        group = list(group)
        yield group[0][1], group[-1][1]


class ArgumentAdvancedDefaultsHelpFormatter(argparse.HelpFormatter):
    """In contrast to ArgumentDefaultsHelpFormatter from argparse,
    this formatter also shows 'const' values if they are present, and
    adds blank lines between actions.
    """

    def __init__(self, prog, indent_increment=2, max_help_position=24, width=None):

        global width_override

        if width_override:
            width = width_override

        super().__init__(prog, indent_increment, max_help_position, width)

    def _get_help_string(self, action):
        help = action.help
        if "%(default)" not in action.help and not isinstance(
            action, argparse._StoreConstAction
        ):
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    if action.const:
                        help += " (default without flag: %(default)s, default with flag: %(const)s)"
                    else:
                        help += " (default: %(default)s)"
        return help

    def _format_action(self, action):
        return super()._format_action(action) + "\n"


if __name__ == "__main__":
    main()
