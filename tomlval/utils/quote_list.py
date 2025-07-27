"""Utility functions for quoting lists of values."""

from typing import Any, List, Optional


def quote_list(
    values: List[Any], only_strings: Optional[bool] = False
) -> List[str]:
    """
    Quote a list of values, optionally only quoting strings.

    Args:
        values (List[Any]): The list of values to quote.
        only_strings (bool): If True, only quote string values.

    Returns:
        List[str]: A list of quoted values.

    Raises:
        TypeError: If a value cannot be quoted.
    """
    quoted = []
    for value in values:
        try:
            if not only_strings:
                quoted.append(f"'{value}'")
            else:
                if isinstance(value, str):
                    quoted.append(f"'{value}'")
                else:
                    quoted.append(str(value))
        except Exception as e:
            raise TypeError(f"Cannot quote value: {value}") from e
    return quoted
