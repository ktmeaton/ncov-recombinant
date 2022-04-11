import os
import sys
import inspect
import common

sys.path.insert(0, os.path.dirname(__file__))


def test_template():

    targets = []
    rule_name = inspect.stack()[0][3].replace("test_", "")
    runner = common.WorkflowRunner(rule_name=rule_name, targets=targets)
    runner.run()


# manual testing
test_template()
