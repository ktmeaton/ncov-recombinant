import os
import sys
import inspect
import common

sys.path.insert(0, os.path.dirname(__file__))


def test_nextclade_dataset():

    targets = ["data/sars-cov-2_2022-03-31T12:00:00Z"]
    rule_name = inspect.stack()[0][3].replace("test_", "")
    runner = common.WorkflowRunner(rule_name=rule_name, targets=targets)
    runner.run()


# manual testing
test_nextclade_dataset()
