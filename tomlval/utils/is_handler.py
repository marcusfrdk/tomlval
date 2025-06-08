"""Module to check if a value is a valid handler."""

import inspect
from typing import Any


def is_handler(fn: Any, key: str | None = None) -> str:
    """
    Function to check if a value is a valid handler.

    Args:
        fn: Any - The value to check.
        key: str - The key of the value in the schema.
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
        if key:
            return f"Key '{key}' is not a function."
        return "'fn' is not a function."

    # Parameters
    params = inspect.signature(fn).parameters

    invalid_keys = []
    for k in params:
        if k not in ["key", "value"]:
            invalid_keys.append(k)

    if invalid_keys:
        if key:
            msg_sing = (
                f"Key '{key}' has an invalid parameter '{invalid_keys[0]}'."
            )
            keys_str = ", ".join(f"'{k}'" for k in invalid_keys)
            msg_plur = f"Key '{key}' has invalid parameters {keys_str}."
        else:
            msg_sing = f"Function has an invalid parameter '{invalid_keys[0]}'."
            keys_str = ", ".join(f"'{k}'" for k in invalid_keys)
            msg_plur = f"Function has invalid parameters {keys_str}."
        return msg_sing if len(invalid_keys) == 1 else msg_plur

    return ""
