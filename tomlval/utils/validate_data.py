"""Validation utilities for validating TOML data."""

import inspect
import re
from datetime import date, datetime, time
from typing import Any, Callable, Dict, List, Tuple

from tomlval.enums import ValidationErrorCode
from tomlval.toml_schema import TOMLSchema
from tomlval.types import Invalid, Optional


def validate_data(
    data: Dict[str, Any], schema: TOMLSchema
) -> Dict[str, ValidationErrorCode]:
    """
    Validate the data against the provided TOML schema.

    Args:
        data (Dict[str, Any]): The TOML data to validate.
        schema (TOMLSchema): The schema against which to validate the data.

    Returns:
        Dict[str, ValidationErrorCode]: A dictionary containing validation
            errors, if any. The keys are the data paths and the values are
            the error codes.

    Raises:
        TypeError: If the data is not a dictionary or if the schema
                   is not an instance of TOMLSchema.
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary.")

    if not isinstance(schema, TOMLSchema):
        raise TypeError("Schema must be a TOMLSchema instance.")

    errors = {}
    validator = DataValidator(data, schema.schema, errors)
    validator.validate()

    return errors


def _validate_function_signature(
    key_path: str, data_value: Any, func: Callable
) -> bool:
    """
    Validate data using a custom function.

    Returns True if validation passes, False otherwise.
    Raises exception if function execution fails.
    """
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())
    param_count = len(params)

    if param_count == 0:
        result = func()
    elif param_count == 1:
        param_name = params[0]
        if param_name == "key":
            result = func(key_path)
        else:
            result = func(data_value)
    else:
        if "key" in params and "value" in params:
            result = func(key=key_path, value=data_value)
        else:
            result = func(key_path, data_value)

    return bool(result)


class DataValidator:
    """Internal validator class for TOML data validation."""

    def __init__(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any],
        errors: Dict[str, ValidationErrorCode],
    ):
        self.data = data
        self.schema = schema
        self.errors = errors
        self.applied_keys = set()

    def validate(self) -> None:
        """Main validation entry point with priority handling."""
        self._validate_exact_matches()
        self._validate_wildcard_patterns()
        self._validate_catch_all()

    def get_errors(self) -> Dict[str, ValidationErrorCode]:
        """Public method to get validation errors."""
        return self.errors.copy()

    def _validate_exact_matches(self) -> None:
        """Validate exact key matches and dot notation keys."""
        for schema_key, schema_value in self.schema.items():
            if "*" not in schema_key:
                self._validate_schema_key(schema_key, schema_value)

    def _validate_wildcard_patterns(self) -> None:
        """Validate wildcard patterns (excluding catch-all '*')."""
        wildcard_schemas = {
            k: v for k, v in self.schema.items() if "*" in k and k != "*"
        }

        sorted_wildcards = sorted(
            wildcard_schemas.items(),
            key=lambda x: self._calculate_pattern_specificity(x[0]),
            reverse=True,
        )

        for pattern, schema_value in sorted_wildcards:
            matching_keys = self._find_matching_keys(pattern)
            for data_key in matching_keys:
                if data_key not in self.applied_keys:
                    self.validate_data_value(
                        data_key, self._get_nested_value(data_key), schema_value
                    )
                    self.applied_keys.add(data_key)

    def _validate_catch_all(self) -> None:
        """Validate remaining keys with catch-all wildcard '*'."""
        if "*" in self.schema:
            catch_all_schema = self.schema["*"]
            for data_key, data_value in self.data.items():
                if data_key not in self.applied_keys:
                    if (
                        isinstance(catch_all_schema, Invalid)
                        or catch_all_schema is Invalid
                    ):
                        self.errors[data_key] = ValidationErrorCode.INVALID_KEY
                    else:
                        self.validate_data_value(
                            data_key, data_value, catch_all_schema
                        )
                    self.applied_keys.add(data_key)

    def _validate_schema_key(self, schema_key: str, schema_value: Any) -> None:
        """Validate a specific schema key against data."""
        if "." in schema_key and not self._is_quoted_key(schema_key):
            self._validate_dotted_key(schema_key, schema_value)
        elif "[" in schema_key and "]" in schema_key:
            self._validate_array_notation_key(schema_key, schema_value)
        else:
            if schema_key in self.data:
                self.validate_data_value(
                    schema_key, self.data[schema_key], schema_value
                )
                self.applied_keys.add(schema_key)
            elif not self._is_optional(schema_value):
                self.errors[schema_key] = ValidationErrorCode.MISSING_KEY

    def _validate_dotted_key(self, schema_key: str, schema_value: Any) -> None:
        """Validate dotted notation keys like 'user.name'."""
        parts = schema_key.split(".")
        current_data = self.data

        for part in parts[:-1]:
            if not isinstance(current_data, dict) or part not in current_data:
                if not self._is_optional(schema_value):
                    self.errors[schema_key] = ValidationErrorCode.MISSING_KEY
                return
            current_data = current_data[part]

        final_key = parts[-1]
        if final_key in current_data:
            self.validate_data_value(
                schema_key, current_data[final_key], schema_value
            )
            if parts[0] in self.data:
                self.applied_keys.add(parts[0])
        elif not self._is_optional(schema_value):
            self.errors[schema_key] = ValidationErrorCode.MISSING_KEY

    def _validate_array_notation_key(
        self, schema_key: str, schema_value: Any
    ) -> None:
        """Validate array notation keys like 'users[0]'."""
        bracket_pos = schema_key.find("[")
        array_key = schema_key[:bracket_pos]
        index_part = schema_key[bracket_pos + 1 : -1]

        if array_key not in self.data:
            if not self._is_optional(schema_value):
                self.errors[schema_key] = ValidationErrorCode.MISSING_KEY
            return

        array_data = self.data[array_key]
        if not isinstance(array_data, list):
            self.errors[schema_key] = ValidationErrorCode.INVALID_TYPE
            return

        try:
            index = int(index_part)
            if 0 <= index < len(array_data):
                self.validate_data_value(
                    schema_key, array_data[index], schema_value
                )
            elif not self._is_optional(schema_value):
                self.errors[schema_key] = ValidationErrorCode.MISSING_KEY
        except ValueError:
            self.errors[schema_key] = ValidationErrorCode.INVALID_TYPE

        self.applied_keys.add(array_key)

    def validate_data_value(
        self, key_path: str, data_value: Any, schema_value: Any
    ) -> None:
        """Validate a data value against its schema definition."""
        if isinstance(schema_value, Invalid) or schema_value is Invalid:
            self.errors[key_path] = ValidationErrorCode.INVALID_KEY
            return

        if isinstance(schema_value, Optional):
            schema_value = schema_value.value_type

        try:
            if self._validate_primitive_types(
                key_path, data_value, schema_value
            ):
                return
            if self._validate_datetime_types(
                key_path, data_value, schema_value
            ):
                return
            if self._validate_regex_pattern(key_path, data_value, schema_value):
                return
            if self._validate_callable(key_path, data_value, schema_value):
                return
            if self._validate_nested_dict(key_path, data_value, schema_value):
                return
            if self._validate_array(key_path, data_value, schema_value):
                return
            if self._validate_tuple(key_path, data_value, schema_value):
                return

            self.errors[key_path] = ValidationErrorCode.UNKNOWN_ERROR

        except Exception:
            self.errors[key_path] = ValidationErrorCode.FUNCTION_EXECUTION_ERROR

    def _validate_primitive_types(
        self, key_path: str, data_value: Any, schema_value: Any
    ) -> bool:
        """Validate primitive types. Returns True if handled."""
        if schema_value in (int, float, str, bool):
            if not isinstance(data_value, schema_value):
                self.errors[key_path] = ValidationErrorCode.INVALID_TYPE
            return True
        return False

    def _validate_datetime_types(
        self, key_path: str, data_value: Any, schema_value: Any
    ) -> bool:
        """Validate datetime types. Returns True if handled."""
        if schema_value in (datetime, date, time):
            if not isinstance(data_value, schema_value):
                self.errors[key_path] = ValidationErrorCode.DATETIME_PARSE_ERROR
            return True
        return False

    def _validate_regex_pattern(
        self, key_path: str, data_value: Any, schema_value: Any
    ) -> bool:
        """Validate regex patterns. Returns True if handled."""
        if isinstance(schema_value, re.Pattern):
            if not isinstance(data_value, str):
                self.errors[key_path] = ValidationErrorCode.INVALID_TYPE
            elif not schema_value.match(data_value):
                self.errors[key_path] = ValidationErrorCode.REGEX_MISMATCH
            return True
        return False

    def _validate_callable(
        self, key_path: str, data_value: Any, schema_value: Any
    ) -> bool:
        """Validate callable functions. Returns True if handled."""
        if callable(schema_value) and not isinstance(schema_value, type):
            try:
                result = _validate_function_signature(
                    key_path, data_value, schema_value
                )
                if not result:
                    self.errors[key_path] = (
                        ValidationErrorCode.VALIDATION_FAILURE
                    )
            except Exception:
                self.errors[key_path] = (
                    ValidationErrorCode.FUNCTION_EXECUTION_ERROR
                )
            return True
        return False

    def _validate_nested_dict(
        self, key_path: str, data_value: Any, schema_value: Any
    ) -> bool:
        """Validate nested dictionaries. Returns True if handled."""
        if isinstance(schema_value, dict):
            if not isinstance(data_value, dict):
                self.errors[key_path] = ValidationErrorCode.INVALID_TYPE
            else:
                nested_validator = DataValidator(
                    data_value, schema_value, self.errors
                )
                nested_validator.validate()
            return True
        return False

    def _validate_array(
        self, key_path: str, data_value: Any, schema_value: Any
    ) -> bool:
        """Validate arrays. Returns True if handled."""
        if isinstance(schema_value, list):
            if not isinstance(data_value, list):
                self.errors[key_path] = ValidationErrorCode.INVALID_TYPE
            else:
                self._validate_array_elements(
                    key_path, data_value, schema_value
                )
            return True
        return False

    def _validate_tuple(
        self, key_path: str, data_value: Any, schema_value: Any
    ) -> bool:
        """Validate tuples. Returns True if handled."""
        if isinstance(schema_value, tuple):
            self._validate_tuple_types(key_path, data_value, schema_value)
            return True
        return False

    def _validate_array_elements(
        self, key_path: str, array_data: List[Any], element_schema: List[Any]
    ) -> None:
        """Validate array elements."""
        if len(element_schema) == 1:
            single_type = element_schema[0]
            for i, element in enumerate(array_data):
                element_path = f"{key_path}[{i}]"
                self.validate_data_value(element_path, element, single_type)
        else:
            allowed_types = element_schema
            for i, element in enumerate(array_data):
                element_path = f"{key_path}[{i}]"
                self._validate_mixed_type_element(
                    element_path, element, allowed_types
                )

    def _validate_mixed_type_element(
        self, key_path: str, element_value: Any, allowed_types: List[Any]
    ) -> None:
        """Validate an element against multiple allowed types."""
        valid_type_found = False
        sorted_types = sorted(
            allowed_types, key=lambda t: t == bool, reverse=True
        )

        for allowed_type in sorted_types:
            try:
                if allowed_type in (int, float, str, bool):
                    if allowed_type == int:
                        if isinstance(element_value, int) and not isinstance(
                            element_value, bool
                        ):
                            valid_type_found = True
                            break
                    else:
                        if isinstance(element_value, allowed_type):
                            valid_type_found = True
                            break
                    continue

                temp_errors = {}
                temp_validator = DataValidator(
                    {key_path: element_value},
                    {key_path: allowed_type},
                    temp_errors,
                )
                temp_validator.validate_data_value(
                    key_path, element_value, allowed_type
                )

                if not temp_errors:
                    valid_type_found = True
                    break

            except Exception:
                continue

        if not valid_type_found:
            self.errors[key_path] = ValidationErrorCode.INVALID_ARRAY_ELEMENT

    def _validate_tuple_types(
        self, key_path: str, data_value: Any, tuple_schema: Tuple
    ) -> None:
        """Validate tuple with multiple allowed types."""
        valid_type_found = False

        for schema_type in tuple_schema:
            try:
                temp_errors = {}
                temp_validator = DataValidator(
                    {key_path: data_value}, {key_path: schema_type}, temp_errors
                )
                temp_validator.validate_data_value(
                    key_path, data_value, schema_type
                )

                if not temp_errors:
                    valid_type_found = True
                    break

            except Exception:
                continue

        if not valid_type_found:
            self.errors[key_path] = ValidationErrorCode.INVALID_TUPLE_TYPE

    def _find_matching_keys(self, pattern: str) -> List[str]:
        """Find data keys that match a wildcard pattern."""
        matching_keys = []

        if "." in pattern:
            pattern_parts = pattern.split(".")
            matching_keys.extend(
                self._find_dotted_pattern_matches(pattern_parts)
            )
        else:
            for data_key in self.data.keys():
                if self._matches_pattern(data_key, pattern):
                    matching_keys.append(data_key)

        return matching_keys

    def _find_dotted_pattern_matches(
        self, pattern_parts: List[str]
    ) -> List[str]:
        """Find matches for dotted wildcard patterns."""
        matches = []

        def search_nested(
            current_data: Dict, current_path: str, remaining_parts: List[str]
        ) -> None:
            if not remaining_parts:
                return

            current_pattern = remaining_parts[0]
            remaining = remaining_parts[1:]

            if isinstance(current_data, dict):
                for key in current_data.keys():
                    if self._matches_pattern(key, current_pattern):
                        new_path = (
                            f"{current_path}.{key}" if current_path else key
                        )

                        if not remaining:
                            matches.append(new_path)
                        else:
                            search_nested(
                                current_data[key], new_path, remaining
                            )

        search_nested(self.data, "", pattern_parts)
        return matches

    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches a wildcard pattern."""
        if "*" not in pattern:
            return text == pattern

        regex_pattern = pattern.replace("*", ".*")
        return bool(re.fullmatch(regex_pattern, text))

    def _calculate_pattern_specificity(self, pattern: str) -> int:
        """Calculate pattern specificity for sorting."""
        specificity = len(pattern.replace("*", ""))
        specificity -= pattern.count("*") * 10
        specificity += pattern.count(".") * 5
        return specificity

    def _get_nested_value(self, key_path: str) -> Any:
        """Get nested value from data using dot notation."""
        if "." not in key_path:
            return self.data.get(key_path)

        parts = key_path.split(".")
        current = self.data

        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]

        return current

    def _is_optional(self, schema_value: Any) -> bool:
        """Check if a schema value is optional."""
        return isinstance(schema_value, Optional)

    def _is_quoted_key(self, key: str) -> bool:
        """Check if a key is quoted."""
        return (key.startswith('"') and key.endswith('"')) or (
            key.startswith("'") and key.endswith("'")
        )
