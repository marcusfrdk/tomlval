"""
Utility functions for converting flat error dictionaries to nested structures.
"""

from typing import Any, Dict, List


def to_dict(errors: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a flat error dictionary to nested dictionary structure.

    Args:
        errors: Dictionary with dot notation keys and error values.

    Returns:
        Nested dictionary structure matching the original data hierarchy.
    """
    nested = {}

    for key_path, error_value in errors.items():
        _set_nested_value(nested, key_path, error_value)

    return nested


def _set_nested_value(
    nested_dict: Dict[str, Any], key_path: str, value: Any
) -> None:
    """
    Set a value in nested dictionary using dot notation and array indices.

    Args:
        nested_dict: The dictionary to modify.
        key_path: Path like "user.name" or "items[0].id".
        value: The error value to set.

    Raises:
        TypeError: If attempting to access an index on a non-list object.
    """
    parts = _parse_key_path(key_path)
    current = nested_dict

    for i, part in enumerate(parts[:-1]):
        if part["type"] == "key":
            key = part["value"]
            if key not in current:
                next_part = parts[i + 1]
                if next_part["type"] == "index":
                    current[key] = []
                else:
                    current[key] = {}
            current = current[key]

        elif part["type"] == "index":
            index = part["value"]

            if not isinstance(current, list):
                raise TypeError(
                    f"Expected list but got {type(current)} at index access"
                )

            while len(current) <= index:
                current.append(None)

            if current[index] is None:
                current[index] = {}
            current = current[index]

    final_part = parts[-1]
    if final_part["type"] == "key":
        current[final_part["value"]] = value
    elif final_part["type"] == "index":
        index = final_part["value"]

        if not isinstance(current, list):
            raise TypeError(
                f"Expected list but got {type(current)} at index access"
            )

        while len(current) <= index:
            current.append(None)
        current[index] = value


def _parse_key_path(key_path: str) -> List[Dict[str, Any]]:
    """
    Parse a key path into components.

    Args:
        key_path: The key path string to parse.

    Returns:
        List of dictionaries with 'type' and 'value' keys representing
        path components.
    """
    parts = []
    current_key = ""
    i = 0

    while i < len(key_path):
        char = key_path[i]

        if char == ".":
            if current_key:
                parts.append({"type": "key", "value": current_key})
                current_key = ""
        elif char == "[":
            if current_key:
                parts.append({"type": "key", "value": current_key})
                current_key = ""

            j = i + 1
            while j < len(key_path) and key_path[j] != "]":
                j += 1

            if j < len(key_path):
                index_str = key_path[i + 1 : j]
                try:
                    index = int(index_str)
                    parts.append({"type": "index", "value": index})
                except ValueError:
                    parts.append({"type": "key", "value": f"[{index_str}]"})
                i = j
            else:
                current_key += char
        else:
            current_key += char

        i += 1

    if current_key:
        parts.append({"type": "key", "value": current_key})

    return parts
