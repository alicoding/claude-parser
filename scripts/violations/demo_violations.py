#!/usr/bin/env python3
"""Demo file showing correct 95/5 patterns."""

import orjson  # Correct: using orjson
import pendulum  # Correct: using pendulum
from typing import List  # Correct: specific type
from toolz import pipe, map

def process_data(data: List[int]):  # Specific type
    """Process data using functional approach."""
    from operator import mul
    from functools import partial
    return pipe(
        data,
        map(partial(mul, 2)),
        list
    )