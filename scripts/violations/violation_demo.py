#!/usr/bin/env python3
"""Demo file to showcase the hooks system catching violations."""

import json  # Should use orjson
import datetime  # Should use pendulum
from typing import Any  # Should avoid Any

class DataProcessor:
    """A class with various violations."""
    
    def __init__(self):
        self.data = []
        self.config = json.loads('{}')  # Using json instead of orjson
    
    def process(self, items: Any):  # Any type violation
        """Process items with manual loops."""
        results = []
        for item in items:  # Manual loop violation
            if item > 0:
                results.append(item * 2)
        return results
    
    def get_timestamp(self):  # Missing return type hint
        """Get current timestamp."""
        return datetime.datetime.now()  # Using datetime instead of pendulum
    
    def validate_data(self, data):  # Missing type hints
        """Validate data without proper typing."""
        valid_items = []
        for item in data:  # Another manual loop
            if self.is_valid(item):
                valid_items.append(item)
        return valid_items
    
    def is_valid(self, item):  # Missing type hints
        """Check if item is valid."""
        return item is not None
    
    def run_forever(self):
        """Bad practice: infinite loop."""
        counter = 0
        while True:  # Should use apscheduler
            counter += 1
            if counter > 1000:
                break
            # Do something
            pass
        return counter

# Unused variable that will trigger F841
temp_variable = "I am not used anywhere"

def standalone_function(x, y):  # Missing type hints
    """Function without type annotations."""
    result = []
    for i in range(x):  # Manual loop
        for j in range(y):  # Nested manual loop
            result.append(i * j)
    return result

# Another unused import example
from pathlib import Path
unused_path = Path(".")  # Will trigger F841

# Extra lines to make file longer
def extra_function_1():
    pass

def extra_function_2():
    pass

def extra_function_3():
    pass

def extra_function_4():
    pass

def extra_function_5():
    pass

def extra_function_6():
    pass

def extra_function_7():
    pass

def extra_function_8():
    pass

def extra_function_9():
    pass

def extra_function_10():
    pass

def extra_function_11():
    pass

def extra_function_12():
    pass

def extra_function_13():
    pass

def extra_function_14():
    pass

def extra_function_15():
    pass

def extra_function_16():
    pass

def extra_function_17():
    pass

def extra_function_18():
    pass

def extra_function_19():
    pass

def extra_function_20():
    pass

def extra_function_21():
    pass

def extra_function_22():
    pass

def extra_function_23():
    pass

def extra_function_24():
    pass

def extra_function_25():
    pass

def extra_function_26():
    pass

def extra_function_27():
    pass

def extra_function_28():
    pass

def extra_function_29():
    pass

def extra_function_30():
    pass

def extra_function_31():
    pass

def extra_function_32():
    pass

def extra_function_33():
    pass

def extra_function_34():
    pass

def extra_function_35():
    pass

def extra_function_36():
    pass

def extra_function_37():
    pass

def extra_function_38():
    pass

def extra_function_39():
    pass

def extra_function_40():
    pass

# This file now exceeds 150 lines