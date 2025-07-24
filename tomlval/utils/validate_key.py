"""Validate a key in a TOML schema."""

import re

from tomlval.errors import TOMLKeyValidationError


def validate_key(key: str) -> None:
    """
    Validate a key for use in a TOML schema.

    Args:
        key (str): The key to validate.

    Raises:
        TOMLKeyValidationError: If the key is invalid.
    """
    if not isinstance(key, str):
        raise TOMLKeyValidationError(
            f"Key must be a string, got {type(key).__name__}."
        )

    if not key:
        raise TOMLKeyValidationError("Key cannot be empty.")

    if _is_single_quoted_key(key):
        if _is_valid_toml_key(key):
            return
        else:
            raise TOMLKeyValidationError(
                f"Key '{key}' is not a valid quoted TOML key."
            )

    # Parse dot-notation keys
    key_parts = _parse_dotted_key(key)
    _validate_wildcard_patterns(key_parts, key)

    for part in key_parts:
        if not part:
            raise TOMLKeyValidationError(
                f"Key '{key}' contains empty segment in dot-notation."
            )
        _validate_key_part(part, key)


def _validate_wildcard_patterns(parts: list[str], full_key: str) -> None:
    """Validate wildcard patterns across dotted key parts."""
    for i in range(len(parts) - 1):
        current_part = parts[i]
        next_part = parts[i + 1]

        if current_part == "*" and next_part == "*":
            raise TOMLKeyValidationError(
                f"Key '{full_key}' contains consecutive wildcard segments. "
                f"Wildcard patterns like '*.*' are not allowed."
            )


def _is_single_quoted_key(key: str) -> bool:
    """Check if the key is a single quoted key (not dot-notation)."""
    if (key.startswith('"') and key.endswith('"')) or (
        key.startswith("'") and key.endswith("'")
    ):
        return "." not in key or not _has_unquoted_dots(key)
    return False


def _has_unquoted_dots(key: str) -> bool:
    """Check if the key has dots outside of quoted sections."""
    in_quotes = False
    quote_char = None
    i = 0

    while i < len(key):
        char = key[i]

        if not in_quotes and char in ('"', "'"):
            in_quotes = True
            quote_char = char
        elif in_quotes and char == quote_char:
            escape_count = 0
            j = i - 1
            while j >= 0 and key[j] == "\\":
                escape_count += 1
                j -= 1
            if escape_count % 2 == 0:
                in_quotes = False
                quote_char = None
        elif not in_quotes and char == ".":
            return True

        i += 1

    return False


def _parse_dotted_key(key: str) -> list[str]:
    """Parse a dotted key into its components, respecting quoted sections."""
    parts = []
    current_part = ""
    in_quotes = False
    quote_char = None
    i = 0

    while i < len(key):
        char = key[i]

        if not in_quotes and char in ('"', "'"):
            in_quotes = True
            quote_char = char
            current_part += char
        elif in_quotes and char == quote_char:
            escape_count = 0
            j = i - 1
            while j >= 0 and key[j] == "\\":
                escape_count += 1
                j -= 1
            if escape_count % 2 == 0:
                in_quotes = False
                quote_char = None
            current_part += char
        elif not in_quotes and char == ".":
            parts.append(current_part)
            current_part = ""
        else:
            current_part += char

        i += 1

    parts.append(current_part)

    return parts


def _validate_key_part(part: str, full_key: str) -> None:
    """Validate a single part of a dotted key."""
    if _is_valid_toml_key(part):
        return

    # Array notation (only for bare keys or after quoted keys)
    if "[" in part and "]" in part and not _is_quoted_key(part):
        _validate_array_notation_key(part, full_key)
        return

    # Wildcard patterns (only for bare keys)
    if "*" in part and not _is_quoted_key(part):
        _validate_wildcard_key(part, full_key)
        return

    raise TOMLKeyValidationError(
        f"Key part '{part}' in '{full_key}' is not a "
        f"valid TOML key or wildcard pattern."
    )


def _is_quoted_key(key: str) -> bool:
    """Check if a key is quoted."""
    return (key.startswith('"') and key.endswith('"')) or (
        key.startswith("'") and key.endswith("'")
    )


def _validate_array_notation_key(part: str, full_key: str) -> None:
    """Validate a key part with array notation like 'key[0]'."""
    if not part.endswith("]"):
        raise TOMLKeyValidationError(
            f"Array notation key part '{part}' in '{full_key}' is malformed."
        )

    bracket_pos = part.find("[")
    if bracket_pos == -1:
        raise TOMLKeyValidationError(
            f"Array notation key part '{part}' in '{full_key}' is malformed."
        )

    key_name = part[:bracket_pos]
    array_index = part[bracket_pos + 1 : -1]

    # Validate the key name part
    if key_name:
        if "*" in key_name:
            _validate_wildcard_key(key_name, full_key)
        elif not _is_valid_toml_key(key_name):
            raise TOMLKeyValidationError(
                f"Key name '{key_name}' in array notation "
                f"'{part}' in '{full_key}' is not a valid TOML key."
            )

    # Validate the array index
    if not array_index.isdigit():
        raise TOMLKeyValidationError(
            f"Array index '{array_index}' in '{part}' in '{full_key}' "
            f"must be a number."
        )


def _validate_wildcard_key(part: str, full_key: str) -> None:
    """Validate a wildcard key pattern."""
    if part == "*":
        return

    non_wildcard_chars = part.replace("*", "")

    if non_wildcard_chars and not _is_valid_toml_key_chars(non_wildcard_chars):
        raise TOMLKeyValidationError(
            f"Wildcard key part '{part}' in '{full_key}' "
            f"contains invalid characters."
        )


def _is_valid_toml_key(key: str) -> bool:
    """Check if a key is valid according to TOML specification."""
    # Quoted key
    if (key.startswith('"') and key.endswith('"')) or (
        key.startswith("'") and key.endswith("'")
    ):
        return _is_valid_quoted_key(key)

    # Bare key
    return _is_valid_bare_key(key)


def _is_valid_bare_key(key: str) -> bool:
    """Validate bare key according to TOML spec."""
    bare_key_pattern = re.compile(r"^[A-Za-z0-9_-]+$")
    return bool(bare_key_pattern.match(key))


def _is_valid_quoted_key(key: str) -> bool:
    """Validate quoted key according to TOML spec."""
    if len(key) < 2:
        return False

    quote_char = key[0]
    if quote_char not in ('"', "'"):
        return False

    if key[-1] != quote_char:
        return False

    if quote_char == '"':
        return _is_valid_basic_string(key[1:-1])

    return True


def _is_valid_basic_string(content: str) -> bool:
    """Validate content of a basic string (quoted with double quotes)."""
    i = 0
    while i < len(content):
        char = content[i]

        # Control characters (except tab) are not allowed
        if ord(char) < 0x20 and char != "\t":
            return False

        # Unescaped quotes
        if char == '"':
            return False

        # Escape sequences
        if char == "\\":
            if i + 1 >= len(content):
                return False
            next_char = content[i + 1]
            if next_char in '"\\bfnrt':
                i += 2
            elif next_char == "u":
                # Unicode escape \uXXXX
                if i + 5 >= len(content):
                    return False
                i += 6
            elif next_char == "U":
                # Unicode escape \UXXXXXXXX
                if i + 9 >= len(content):
                    return False
                i += 10
            else:
                return False
        else:
            i += 1

    return True


def _is_valid_toml_key_chars(chars: str) -> bool:
    """
    Check if characters are valid for TOML keys
    (excluding quotes and wildcards).
    """
    bare_key_pattern = re.compile(r"^[A-Za-z0-9_-]*$")
    return bool(bare_key_pattern.match(chars))
