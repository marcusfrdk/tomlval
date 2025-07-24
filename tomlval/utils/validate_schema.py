"""Module for validating TOML schemas."""

import inspect
from datetime import date, datetime, time
from re import Pattern, sub
from typing import Any, Callable, Dict

from tomlval.errors import TOMLSchemaConflictError, TOMLSchemaValidationError
from tomlval.types import Invalid, Optional
from tomlval.utils.validate_key import validate_key


def validate_schema(schema: Dict[str, Any]) -> None:
    """
    Validate the provided schema for TOML values.

    A schema is a dictionary of functions and objects that define the expected
    types and constraints for TOML values.

    Args:
        schema (Dict[str, Any]): The schema to validate.
    Returns:
        None
    Raises:
        TOMLSchemaValidationError: If the schema is invalid.
        TOMLKeyValidationError: If a key in the schema is invalid.
        TOMLSchemaConflictError: If conflicting keys are found.
    """
    if not isinstance(schema, dict):
        raise TOMLSchemaValidationError("Schema must be a dictionary.")

    _check_schema_conflicts(schema)
    _validate_schema_recursive(schema, "")


def _check_schema_conflicts(schema: Dict[str, Any]) -> None:
    """Check for conflicting key paths in the schema."""
    _collect_all_paths(schema, "", {})


def _collect_all_paths(
    schema: Dict[str, Any], parent_key: str, all_paths: Dict[str, str]
) -> None:
    """Collect all possible key paths from the schema with their source."""
    for key, value in schema.items():
        if parent_key:
            full_key = f"{parent_key}.{key}"
        else:
            full_key = key

        normalized_path = _normalize_path(full_key)

        if normalized_path in all_paths:
            raise TOMLSchemaConflictError(
                f"Found conflicting keys for path '{normalized_path}'."
            )

        all_paths[normalized_path] = full_key

        if isinstance(value, Optional):
            value = value.value_type
        elif isinstance(value, Invalid):
            continue

        if isinstance(value, dict):
            _collect_all_paths(value, full_key, all_paths)
        elif (
            isinstance(value, list)
            and len(value) == 1
            and isinstance(value[0], dict)
        ):
            _collect_all_paths(value[0], f"{full_key}[0]", all_paths)


def _normalize_path(path: str) -> str:
    """Normalize a path for conflict detection by removing array indices."""
    normalized = sub(r"\[\d+\]", "", path)
    return normalized


def _validate_schema_recursive(schema: Dict[str, Any], parent_key: str) -> None:
    """Recursively validate schema with full key path tracking."""
    for key, value in schema.items():
        if parent_key:
            full_key = f"{parent_key}.{key}"
        else:
            full_key = key

        validate_key(full_key)
        _validate_schema_value(full_key, value)


def _validate_schema_value(key: str, value: Any) -> None:
    """Validate a single schema value."""
    # Primitive or Invalid
    if (
        _is_primitive_type(value)
        or isinstance(value, Invalid)
        or value is Invalid
    ):
        return

    # Optional
    if isinstance(value, Optional):
        _validate_optional_value(key, value)
        return

    # Function/lambda
    if callable(value) and not isinstance(value, type):
        _validate_function_signature(key, value)
        return

    # Nested table (dict)
    if isinstance(value, dict):
        _validate_schema_recursive(value, key)
        return

    # Mixed types (tuple)
    if isinstance(value, tuple):
        _validate_tuple_value(key, value)
        return

    # Array
    if isinstance(value, list):
        _validate_array_value(key, value)
        return

    raise TOMLSchemaValidationError(
        f"Schema key '{key}' has invalid type '{type(value).__name__}'. "
        f"Must be a primitive type, tuple of primitives, table (dict), "
        f"function, array, Optional, or Invalid."
    )


def _validate_optional_value(key: str, optional_value: Optional) -> None:
    """Validate an Optional schema value."""
    # Wildcard + Optional check
    if key == "*":
        raise TOMLSchemaValidationError(
            f"Schema key '{key}' cannot combine catch-all wildcard '*' "
            f"with Optional. Catch-all wildcards match existing keys, "
            f"making Optional meaningless."
        )

    # Invalid in Optional
    if (
        isinstance(optional_value.value_type, Invalid)
        or optional_value.value_type is Invalid
    ):
        raise TOMLSchemaValidationError(
            f"Schema key '{key}' cannot wrap Invalid type with Optional. "
            f"Use Invalid directly instead."
        )

    _validate_schema_value(key, optional_value.value_type)


def _validate_tuple_value(key: str, tuple_value: tuple) -> None:
    """Validate a tuple schema value."""
    if len(tuple_value) == 0:
        raise TOMLSchemaValidationError(
            f"Schema key '{key}' has empty tuple. "
            f"Tuples must contain at least one primitive type."
        )

    for i, item in enumerate(tuple_value):
        if isinstance(item, Invalid) or item is Invalid:
            raise TOMLSchemaValidationError(
                f"Schema key '{key}' tuple cannot contain Invalid type. "
                f"Invalid should be used at the key level, "
                f"not within tuples."
            )

        if isinstance(item, Optional):
            _validate_schema_value(f"{key}[{i}]", item.value_type)
            continue

        if (
            not _is_primitive_type(item)
            and not isinstance(item, dict)
            and not (callable(item) and not isinstance(item, type))
        ):
            raise TOMLSchemaValidationError(
                f"Schema key '{key}' tuple item at index {i} "
                f"is not a primitive type, table, function, or Optional."
            )

        if callable(item) and not isinstance(item, type):
            _validate_function_signature(f"{key}[{i}]", item)


def _validate_array_value(key: str, array_value: list) -> None:
    """Validate an array schema value."""
    if len(array_value) == 0:
        raise TOMLSchemaValidationError(
            f"Schema key '{key}' array cannot be empty. "
            f"Must contain at least one element defining allowed types."
        )

    if len(array_value) == 1:
        _validate_single_element_array(key, array_value[0])
    else:
        _validate_mixed_type_array(key, array_value)


def _validate_single_element_array(key: str, array_type: Any) -> None:
    """Validate a single-element array schema."""
    # Array with Invalid
    if isinstance(array_type, Invalid) or array_type is Invalid:
        raise TOMLSchemaValidationError(
            f"Schema key '{key}' array cannot contain Invalid type. "
            f"Invalid should be used at the key level, "
            f"not within arrays."
        )

    # Optional array
    if isinstance(array_type, Optional):
        array_type = array_type.value_type

    # Array of primitives
    if _is_primitive_type(array_type):
        return

    # Array of tables
    if isinstance(array_type, dict):
        _validate_schema_recursive(array_type, f"{key}[0]")
        return

    # Array of functions
    if callable(array_type) and not isinstance(array_type, type):
        _validate_function_signature(f"{key}[0]", array_type)
        return

    raise TOMLSchemaValidationError(
        f"Schema key '{key}' array type must "
        f"be a primitive type, a nested table (dict), function, "
        f"or Optional."
    )


def _validate_mixed_type_array(key: str, array_types: list) -> None:
    """Validate a mixed-type array schema."""
    for i, array_type in enumerate(array_types):
        if isinstance(array_type, Invalid) or array_type is Invalid:
            raise TOMLSchemaValidationError(
                f"Schema key '{key}' array cannot contain "
                f"Invalid type. Invalid should be used at "
                f"the key level, not within arrays."
            )

        # Optional array elements
        if isinstance(array_type, Optional):
            array_type = array_type.value_type

        if (
            not _is_primitive_type(array_type)
            and not isinstance(array_type, dict)
            and not (callable(array_type) and not isinstance(array_type, type))
        ):
            raise TOMLSchemaValidationError(
                f"Schema key '{key}' array element at index {i} "
                f"must be a primitive type, table (dict), or function. "
                f"Got {type(array_type).__name__}."
            )

        if callable(array_type) and not isinstance(array_type, type):
            _validate_function_signature(f"{key}[{i}]", array_type)


def _validate_function_signature(key: str, func: Callable) -> None:
    """Validate that a function has the correct signature for validation."""
    try:
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        param_count = len(params)

        if param_count == 0:
            return

        if param_count == 1:
            param_name = params[0]
            if param_name not in ("key", "value"):
                raise TOMLSchemaValidationError(
                    f"Schema key '{key}' function parameter must be named "
                    f"'key' or 'value'. Found parameter '{param_name}'."
                )
            return

        if param_count == 2:
            if set(params) != {"key", "value"}:
                raise TOMLSchemaValidationError(
                    f"Schema key '{key}' function with 2 parameters must have "
                    f"parameters named 'key' and 'value'. "
                    f"Found parameters: {', '.join(params)}."
                )
            return

        raise TOMLSchemaValidationError(
            f"Schema key '{key}' function must accept 0, 1, or 2 "
            f"parameters. Valid signatures: (), (key), (value), or "
            f"(key, value). Found {param_count} parameters."
        )

    except (ValueError, TypeError) as e:
        raise TOMLSchemaValidationError(
            f"Schema key '{key}' function signature could not be inspected: {e}"
        ) from e


def _is_primitive_type(value: Any) -> bool:
    """Check if a value represents a valid primitive type."""
    # Built-in types
    builtin_types = (int, float, str, bool)
    if value in builtin_types:
        return True

    if isinstance(value, type) and issubclass(value, builtin_types):
        return True

    # Regex pattern
    if isinstance(value, Pattern):
        return True

    # datetime
    datetime_types = (datetime, date, time)
    if value in datetime_types:
        return True

    if isinstance(value, type) and issubclass(value, datetime_types):
        return True

    return False
