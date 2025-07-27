"""Module for defining a combined int, float type."""

from typing import Any, Union

Number = Union[int, float, bool]

number = (int, float, bool)


def is_number(value: Any) -> bool:
    """
    Check if the value is a number type.

    Args:
        value (Any): The value to check.
    Returns:
        bool: True if the value is a number type, False otherwise.
    """
    return isinstance(value, number)
