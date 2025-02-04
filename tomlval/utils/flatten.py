""" A function to flatten a dictionary into a single level dictionary. """

import re
from collections import defaultdict


def flatten_all(dictionary: dict):
    """
    Function to flatten a dictionary into a single level dictionary.
    This includes lists, which will be flattened into a single level list.
    (e.g. key = [1, 2] -> key.[0] = 1, key.[1] = 2)

    Args:
        dictionary: dict - The dictionary to flatten.
    Returns:
        dict - The flattened dictionary
    Raises:
        None
    """

    def _flatten(data: dict, parent_key: str = "") -> dict:
        """A recursive function to flatten a dictionary."""
        _data = {}
        for key, value in data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):
                _data.update(_flatten(value, full_key))
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    list_key = f"{full_key}.[{idx}]"
                    if isinstance(item, (dict, list)):
                        _data.update(_flatten(item, list_key))
                    else:
                        _data[list_key] = item
            else:
                _data[full_key] = value
        return _data

    return _flatten(dictionary)


def flatten(dictionary: dict) -> dict:
    """
    A function to flatten a dictionary into a single level dictionary.

    Args:
        dictionary: dict - The dictionary to flatten.
    Returns:
        dict - The flattened dictionary
    Raises:
        None
    """

    pattern = re.compile(r"^(.*)\.\[(\d+)\]$")
    result = {}
    temp = defaultdict(list)

    for key, value in flatten_all(dictionary).items():
        match = pattern.match(key)

        if match:
            base_key, index = match.groups()
            index = int(index)
            temp[base_key].append((index, value))
        else:
            result[key] = value

    for base_key, items in temp.items():
        sorted_values = [val for _, val in sorted(items, key=lambda x: x[0])]
        result[base_key] = sorted_values

    return result
