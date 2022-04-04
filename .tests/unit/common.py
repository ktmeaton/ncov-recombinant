"""
Common code for unit testing of rules generated with Snakemake 7.3.6.
"""

import os
import sys

import subprocess as sp
import tempfile
import shutil
from pathlib import Path, PurePosixPath


class WorkflowRunner:
    def __init__(self, rule_name, targets):
        self.rule_name = rule_name
        self.targets = targets
        self.defaults_path = PurePosixPath("defaults")
        self.input_path = PurePosixPath(".tests/unit/{}/data".format(rule_name))
        self.expected_path = PurePosixPath(".tests/unit/{}/expected".format(rule_name))
        self.output_path = PurePosixPath(".")

    def run(self):

        # Create a temporary working directory
        tmpdir = tempfile.mkdtemp()
        workdir = Path(tmpdir) / "workdir"

        # If the rule has inputs, copy to the working directory:
        if os.path.exists(self.input_path):
            shutil.copytree(self.input_path, Path(workdir))

        # Copy defaults to the temporary workdir
        shutil.copytree(self.defaults_path, Path(workdir) / "defaults")

        # construct command
        cmd = (
            "snakemake --profile profiles/ci -f --keep-target-files"
            + " --directory {dir} {targets}".format(
                dir=workdir,
                targets=" ".join(self.targets),
            )
        )
        cmd_list = cmd.split(" ")

        # Debugging
        print(cmd, file=sys.stderr)

        # Run the test job.
        sp.run(cmd_list, stdout=sp.PIPE)
        # Check the output byte by byte using cmp.
        OutputChecker(self.output_path, self.expected_path, workdir).check()

        # Debugging: comment out
        # shutil.rmtree(tmpdir)


class OutputChecker:
    def __init__(self, output_path, expected_path, workdir):
        self.output_path = output_path
        self.expected_path = expected_path
        self.workdir = workdir

    def check(self):
        input_files = set(
            (Path(path) / f).relative_to(self.output_path)
            for path, subdirs, files in os.walk(self.output_path)
            for f in files
        )
        expected_files = set(
            (Path(path) / f).relative_to(self.expected_path)
            for path, _subdirs, files in os.walk(self.expected_path)
            for f in files
        )
        ignore_prefixes = [
            ".snakemake",
            "benchmarks",
            "logs",
            "defaults",
        ]
        unexpected_files = set()
        for path, _subdirs, files in os.walk(self.workdir):
            for f in files:

                # ignore .snakemake files
                if str(f).startswith(".snakemake"):
                    continue

                f = (Path(path) / f).relative_to(self.workdir)

                # prefixes to ignore
                exclude_file = False
                for prefix in ignore_prefixes:
                    if str(f).startswith(prefix):
                        exclude_file = True
                if exclude_file:
                    continue

                if f in expected_files:
                    self.compare_files(self.workdir / f, self.expected_path / f)

                elif f in input_files:
                    # ignore input files
                    pass
                else:
                    unexpected_files.add(f)

        if unexpected_files:
            raise ValueError(
                "Unexpected files:\n{}".format(
                    "\n".join(sorted(map(str, unexpected_files)))
                )
            )

    def compare_files(self, generated_file, expected_file):
        sp.check_output(["cmp", generated_file, expected_file])
