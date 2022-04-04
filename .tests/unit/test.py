#!/usr/bin/env python3

import os

os.system(
    """
pytest \
    .tests/unit/test_nextclade_dataset.py \
    .tests/unit/test_nextclade.py
"""
)
