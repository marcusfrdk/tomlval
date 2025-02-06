""" Module to check if a value is a valid handler. """

import inspect
from typing import Any


def is_handler(fn: Any) -> str:
    """
    Function to check if a value is a valid handler.

    Args:
        fn: Any - The value to check.
    Returns:
        str - The error message if the value is not a valid handler.
    Raises:
        None
    """
    # Built-in types
    if isinstance(fn, type):
        return ""

    # Type check
    if not inspect.isfunction(fn):
        return "'fn' is not a function."

    # Parameters
    params = inspect.signature(fn).parameters

    invalid_keys = []
    for key in params:
        if key not in ["key", "value"]:
            invalid_keys.append(key)

    if invalid_keys:
        msg_sing = f"Key '{invalid_keys[0]}' is not valid."
        keys_str = ", ".join(f"'{k}'" for k in invalid_keys)
        msg_plur = f"Keys {keys_str} are not valid."
        return msg_sing if len(invalid_keys) == 1 else msg_plur

    return ""
