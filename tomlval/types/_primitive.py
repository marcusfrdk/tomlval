"""Module for defining a type for primitives."""

from typing import Any, Union

Primitive = Union[str, int, float, bool]

primitive = (str, int, float, bool)


def is_primitive(value: Any) -> bool:
    """
    Check if the value is a primitive type.

    Args:
        value (Any): The value to check.
    Returns:
        bool: True if the value is a primitive type, False otherwise.
    """
    return isinstance(value, primitive)
