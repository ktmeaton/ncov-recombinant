import os
import sys
import inspect
import common

sys.path.insert(0, os.path.dirname(__file__))


def test_nextclade():

    targets = [
        "results/controls/nextclade.metadata.tsv",
        "results/controls/nextclade.aligned.fasta",
        "results/controls/translations",
        "results/controls/nextclade.qc.tsv",
        "results/controls/nextclade.errors.csv",
    ]
    rule_name = inspect.stack()[0][3].replace("test_", "")
    runner = common.WorkflowRunner(rule_name=rule_name, targets=targets)
    runner.run()


# manual testing
test_nextclade()
