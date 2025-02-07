""" A function to flatten a dictionary into a single-level dictionary. """

import re
from collections import defaultdict
from typing import Literal

from tomlval import TOMLSchemaMergeError


def flatten(dictionary: dict, method: Literal["all", "schema"] = "all") -> dict:
    """
    Flatten a dictionary into a single-level dictionary with
    post-processed array values.

    Args:
        dictionary: dict - The dictionary to flatten.
        method: Literal["all", "schema"] - The flattening method.
            - all - Flatten all values, including lists.
            - schema - Flatten values suitable for a TOML schema.
    Returns:
        dict - The flattened dictionary.
    Raises:
        TOMLSchemaMergeError - If a merged schema contains an
        invalid list value.
    """
    pattern = re.compile(r"^(.*)\.\[(\d+)\]$")
    result = {}
    temp = defaultdict(list)

    flat_dict = {"all": flatten_all, "schema": flatten_schema}[method](
        dictionary
    )

    for key, value in flat_dict.items():
        match = pattern.match(key)
        if match:
            base_key, index = match.groups()
            temp[base_key].append((int(index), value))
        else:
            result[key] = value

    for base_key, items in temp.items():
        sorted_values = [val for _, val in sorted(items, key=lambda x: x[0])]
        result[base_key] = sorted_values
    return result


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


def flatten_schema(dictionary: dict):
    """
    Flatten a dictionary into a single-level dictionary
    suitable for use as a TOML schema.

    Args:
        dictionary: dict - The dictionary to be flattened.
    Returns:
        dict - A flattened dictionary with keys that represent
        the nested structure.
    Raises:
        None
    """

    def merge_values(old, new):
        """
        Merge two values into a single tuple.

        Args:
            old: type or tuple - The existing value.
            new: type or tuple - The new value to merge.
        Returns:
            tuple - A tuple containing the merged values.
        Raises:
            TOMLSchemaMergeError - If either 'old' or 'new'
            is not a type or tuple.
        """

        allowed = (tuple, type)
        if not isinstance(old, allowed):
            raise TOMLSchemaMergeError(old, new)
        if not isinstance(new, allowed):
            raise TOMLSchemaMergeError(old, new)
        if not isinstance(old, tuple):
            old = (old,)
        if not isinstance(new, tuple):
            new = (new,)
        return old + new

    def add_to_dict(d: dict, key: str, value, merge_as_tuple: bool = False):
        """
        Add a key-value pair to a dictionary, merging values if the key exists.

        Args:
            d: dict - The dictionary to update.
            key: str - The key to add or update.
            value: any - The value to add.
            merge_as_tuple: bool - Whether to merge values as a tuple.
        Returns:
            None
        Raises:
            TOMLSchemaMergeError - If merging values and invalid types
            are encountered.
        """
        if key in d:
            if merge_as_tuple:
                d[key] = merge_values(d[key], value)
            else:
                if isinstance(d[key], list):
                    d[key].append(value)
                else:
                    d[key] = [d[key], value]
        else:
            d[key] = value

    def merge_dicts(
        dest: dict, src: dict, merge_as_tuple: bool = False
    ) -> dict:
        """
        Merge a source dictionary into a destination dictionary.

        Args:
            dest: dict - The destination dictionary.
            src: dict - The source dictionary to merge.
            merge_as_tuple: bool - Whether to merge conflicting keys as a tuple.
        Returns:
            dict - The updated destination dictionary.
        Raises:
            TOMLSchemaMergeError - If merging values and invalid types
            are encountered.
        """
        for key, value in src.items():
            add_to_dict(dest, key, value, merge_as_tuple=merge_as_tuple)
        return dest

    def _flatten(
        data, parent_key: str = "", merge_as_tuple: bool = False
    ) -> dict:
        """
        Recursively flatten a nested dictionary.

        Args:
            data: dict - The current dictionary segment to flatten.
            parent_key: str - The accumulated key path from parent levels.
            merge_as_tuple: bool - Flag indicating if we are in a merged
            schema context.
        Returns:
            dict - The flattened dictionary for the current recursion level.
        Raises:
            TOMLSchemaMergeError - If a list is encountered in a merged
            schema context.
        """
        flat = {}
        for key, value in data.items():
            # Build the new key path
            new_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):
                # Recursively flatten sub-dictionaries
                merged = _flatten(value, new_key, merge_as_tuple=merge_as_tuple)
                flat = merge_dicts(flat, merged, merge_as_tuple=merge_as_tuple)
            elif isinstance(value, list):
                # If every item is a dict, treat the list as a
                # schema merge context
                if value and all(isinstance(item, dict) for item in value):
                    for item in value:
                        # Add the [] suffix to the key
                        merged = _flatten(
                            item, f"{new_key}[]", merge_as_tuple=True
                        )
                        flat = merge_dicts(flat, merged, merge_as_tuple=True)
                else:
                    if merge_as_tuple:
                        # For merge errors, list values are not allowed
                        raise TOMLSchemaMergeError(
                            "Cannot merge list with list", value
                        )
                    else:
                        # Process lists with index suffixes
                        for idx, item in enumerate(value):
                            if isinstance(item, dict):
                                list_key = f"{new_key}[]"
                                merged = _flatten(
                                    item,
                                    list_key,
                                    merge_as_tuple=merge_as_tuple,
                                )
                                flat = merge_dicts(
                                    flat, merged, merge_as_tuple=merge_as_tuple
                                )
                            elif isinstance(item, list):
                                list_key = f"{new_key}.[{idx}]"
                                merged = _flatten(
                                    item,
                                    list_key,
                                    merge_as_tuple=merge_as_tuple,
                                )
                                flat = merge_dicts(
                                    flat, merged, merge_as_tuple=merge_as_tuple
                                )
                            else:
                                list_key = f"{new_key}.[{idx}]"
                                add_to_dict(
                                    flat, list_key, item, merge_as_tuple=False
                                )
            else:
                # Directly add non-dict, non-list values
                add_to_dict(flat, new_key, value, merge_as_tuple=merge_as_tuple)
        return flat

    return _flatten(dictionary, parent_key="", merge_as_tuple=False)


if __name__ == "__main__":
    # _data = {
    #     "string": str,
    #     "multi_type": (int, float),
    #     "list1": [str],
    #     "list2": [int, float],
    #     "nested_list": [{"key": str}],
    #     "deeply_nested_list": [{"nested_list": [{"key": str}]}],
    #     "merged_nested_list": [{"key": str}, {"key": (int,)}],
    #     # "merged_nested_list2": [{"key": str}, {"key": [int, float]}],
    # }

    import os
    import tomllib

    path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "examples",
            "full_spec",
            "schema.toml",
        )
    )

    with open(path, "rb") as f:
        _data = tomllib.load(f)

    for k, v in flatten(_data).items():
        print(f"{k} = {v}")

    # try:
    #     for k, v in flatten_all(_data).items():
    #         print(f"{k} = {v}")
    # except TOMLSchemaMergeError as e:
    #     print(f"Error: {e}")
