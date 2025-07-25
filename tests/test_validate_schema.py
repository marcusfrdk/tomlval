"""Tests for the validate_schema module."""

# pylint: disable=unused-argument

import re
from datetime import date, datetime, time

import pytest

from tomlval import Invalid, Literal, Optional
from tomlval.errors import (
    TOMLKeyValidationError,
    TOMLSchemaConflictError,
    TOMLSchemaValidationError,
)
from tomlval.utils.validate_schema import validate_schema


class TestValidateSchema:
    """Test cases for the validate_schema function."""

    def test_valid_primitive_types(self):
        """Test schema with valid primitive types."""
        valid_schemas = [
            {"key": int},
            {"key": float},
            {"key": str},
            {"key": bool},
            {"key": datetime},
            {"key": date},
            {"key": time},
            {"key": re.compile(r"test")},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_functions(self):
        """Test schema with valid function signatures."""

        def no_params():
            return True

        def key_param(key):
            return True

        def value_param(value):
            return True

        def key_value_params(key, value):
            return True

        def value_key_params(value, key):
            return True

        valid_schemas = [
            {"key": no_params},
            {"key": key_param},
            {"key": value_param},
            {"key": key_value_params},
            {"key": value_key_params},
            {"key": lambda: True},
            {"key": lambda key: True},
            {"key": lambda value: True},
            {"key": lambda key, value: True},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_nested_dictionaries(self):
        """Test schema with nested dictionaries."""
        valid_schemas = [
            {"user": {"name": str, "age": int}},
            {"app": {"database": {"host": str, "port": int}}},
            {"config": {"nested": {"deep": {"value": bool}}}},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_arrays(self):
        """Test schema with valid array definitions."""
        valid_schemas = [
            {"items": [str]},
            {"numbers": [int]},
            {"users": [{"name": str, "age": int}]},
            {"validators": [lambda value: True]},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_tuples(self):
        """Test schema with valid tuple definitions."""
        valid_schemas = [
            {"value": (int, str)},
            {"data": (int, float, str, bool)},
            {"mixed": (str, {"nested": int}, lambda value: True)},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_invalid_non_dict_schema(self):
        """Test that non-dictionary schemas raise error."""
        invalid_schemas = [
            "string",
            123,
            [],
            None,
            True,
        ]

        for schema in invalid_schemas:
            with pytest.raises(
                TOMLSchemaValidationError, match="Schema must be a dictionary"
            ):
                validate_schema(schema)

    def test_invalid_function_signatures(self):
        """Test functions with invalid signatures."""

        def too_many_params(a, b, c):
            return True

        def invalid_param_name(invalid_name):
            return True

        def invalid_two_params(param1, param2):
            return True

        def wrong_param_names(key, wrong_name):
            return True

        invalid_schemas = [
            {"key": too_many_params},
            {"key": invalid_param_name},
            {"key": invalid_two_params},
            {"key": wrong_param_names},
            {"key": lambda a, b, c: True},
            {"key": lambda invalid: True},
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_invalid_array_definitions(self):
        """Test invalid array definitions."""
        invalid_schemas = [
            {"key": []},  # Empty array
            {"key": [None]},  # Invalid element type
            {"key": [object]},  # Invalid type
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_invalid_tuple_definitions(self):
        """Test invalid tuple definitions."""
        invalid_schemas = [
            {"key": ()},  # Empty tuple
            {"key": (None,)},  # Invalid element type
            {"key": (object,)},  # Invalid type
            {"key": (int, None, str)},  # Invalid element in middle
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_invalid_value_types(self):
        """Test schemas with invalid value types."""
        invalid_schemas = [
            {"key": None},
            {"key": object()},
            {"key": Exception},
            {"key": set()},
            {"key": complex(1, 2)},
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_schema_conflicts(self):
        """Test detection of conflicting schema paths."""
        conflicting_schemas = [
            # Direct conflict
            {"user.name": str, "user": {"name": str}},
            # Array conflict
            {"items": [str], "items[0]": str},
            # Nested array conflict
            {"data.items": [{"value": str}], "data.items[0].value": str},
        ]

        for schema in conflicting_schemas:
            with pytest.raises(TOMLSchemaConflictError):
                validate_schema(schema)

    def test_complex_valid_schema(self):
        """Test a complex but valid schema."""

        def validate_email(value):
            return "@" in value

        schema = {
            "app": {"name": str, "version": str, "debug": bool},
            "database": {
                "host": str,
                "port": int,
                "credentials": {"username": str, "password": str},
            },
            "users": [
                {
                    "name": str,
                    "email": validate_email,
                    "age": int,
                    "roles": [str],
                }
            ],
            "features": (str, bool, int),
            "timestamps": {"created": datetime, "updated": datetime},
            "pattern_test": re.compile(r"\d+"),
        }

        validate_schema(schema)

    def test_invalid_key_in_schema(self):
        """Test that invalid keys are caught."""
        invalid_schemas = [
            {"": str},  # Empty key
            {"user..name": str},  # Empty segment in dot notation
            {"...key": str},  # Empty segments at start
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLKeyValidationError):
                validate_schema(schema)

    def test_nested_function_validation(self):
        """Test function validation in nested structures."""

        def valid_func(value):
            return True

        def invalid_func(wrong_param):
            return True

        valid_schema = {"data": {"items": [valid_func]}}
        validate_schema(valid_schema)

        invalid_schema = {"data": {"items": [invalid_func]}}
        with pytest.raises(TOMLSchemaValidationError):
            validate_schema(invalid_schema)

    def test_tuple_with_functions(self):
        """Test tuples containing functions."""

        def validator(value):
            return True

        def invalid_validator(wrong_param):
            return True

        valid_schema = {"mixed": (str, validator, int)}
        validate_schema(valid_schema)

        invalid_schema = {"mixed": (str, invalid_validator, int)}
        with pytest.raises(TOMLSchemaValidationError):
            validate_schema(invalid_schema)

    def test_regex_pattern_validation(self):
        """Test regex pattern validation."""
        valid_schema = {
            "email_pattern": re.compile(r"[^@]+@[^@]+\.[^@]+"),
            "nested": {"pattern": re.compile(r"\d{4}-\d{2}-\d{2}")},
        }
        validate_schema(valid_schema)

    def test_datetime_types_validation(self):
        """Test datetime types validation."""
        valid_schema = {
            "created_at": datetime,
            "birth_date": date,
            "alarm_time": time,
            "nested": {"timestamp": datetime},
        }
        validate_schema(valid_schema)

    def test_function_signature_inspection_error(self):
        """Test handling of functions that can't be inspected."""
        schema = {"key": lambda: True}
        validate_schema(schema)

    def test_dotted_key_validation_in_schema(self):
        """Test that dotted keys in schema are properly validated."""
        valid_schemas = [
            {"user.name": str},
            {"app.database.host": str},
            {"config.nested.value": int},
            {'"key.with.dots"': str},  # Valid quoted key
            {'".user"': str},  # Valid quoted key
            {'"user."': str},  # Valid quoted key
        ]

        for schema in valid_schemas:
            validate_schema(schema)

        # Invalid dotted keys
        invalid_schemas = [
            {"user..name": str},  # Empty segment
            {".user": str},  # Empty segment
            {"user.": str},  # Empty segment
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLKeyValidationError):
                validate_schema(schema)

    def test_array_notation_in_schema_keys(self):
        """Test array notation in schema keys."""
        valid_schemas = [
            {"users[0]": str},
            {"data[123].value": int},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_wildcard_keys_in_schema(self):
        """Test wildcard patterns in schema keys."""
        valid_schemas = [
            {"user*": str},
            {"*name": str},
            {"config*.value": int},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_schema_value_validation_edge_cases(self):
        """Test edge cases for schema value validation."""
        valid_schema = {"key": str}
        validate_schema(valid_schema)

        valid_schemas = [
            {"pattern": re.compile(r"test")},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_optional_primitive_types(self):
        """Test schema with valid optional primitive types."""
        valid_schemas = [
            {"key": Optional(int)},
            {"key": Optional(float)},
            {"key": Optional(str)},
            {"key": Optional(bool)},
            {"key": Optional(datetime)},
            {"key": Optional(date)},
            {"key": Optional(time)},
            {"key": Optional(re.compile(r"test"))},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_optional_functions(self):
        """Test schema with optional function validators."""

        def no_params():
            return True

        def value_param(value):
            return True

        def key_value_params(key, value):
            return True

        valid_schemas = [
            {"key": Optional(no_params)},
            {"key": Optional(value_param)},
            {"key": Optional(key_value_params)},
            {"key": Optional(lambda: True)},
            {"key": Optional(lambda value: True)},
            {"key": Optional(lambda key, value: True)},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_optional_nested_dictionaries(self):
        """Test schema with optional nested dictionaries."""
        valid_schemas = [
            {"user": Optional({"name": str, "age": int})},
            {"config": Optional({"database": {"host": str, "port": int}})},
            {"nested": {"data": Optional({"value": bool})}},
            {"app": {"name": str, "config": Optional({"debug": bool})}},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_optional_arrays(self):
        """Test schema with optional array definitions."""
        valid_schemas = [
            {"items": Optional([str])},
            {"numbers": Optional([int])},
            {"users": Optional([{"name": str, "age": int}])},
            {"validators": Optional([lambda value: True])},
            {"mixed_items": [Optional(str)]},
            {"optional_users": [Optional({"name": str})]},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_mixed_type_arrays(self):
        """Test schema with valid mixed-type array definitions."""
        valid_schemas = [
            {"items": [str, int]},  # Mixed string/int array
            {"data": [int, float, str]},  # Multiple mixed types
            {"values": [bool, str, int]},  # Mixed primitives
            {"mixed_nested": [str, {"name": str}]},  # Mixed primitives and dict
            {"validators": [str, lambda value: True]},  # Mixed functions
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_optional_tuples(self):
        """Test schema with optional tuple definitions."""
        valid_schemas = [
            {"value": Optional((int, str))},
            {"data": Optional((int, float, str, bool))},
            {"mixed": Optional((str, {"nested": int}, lambda value: True))},
            {"tuple_with_optional": (str, Optional(int), bool)},
            {"all_optional": (Optional(str), Optional(int), Optional(bool))},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_nested_optional_values(self):
        """Test deeply nested optional values."""
        valid_schemas = [
            {"config": Optional({"database": Optional({"host": str})})},
            {"tags": Optional([Optional(str)])},
            {"mixed": Optional((str, Optional(int), Optional(bool)))},
            {
                "users": Optional(
                    [
                        Optional(
                            {
                                "profile": Optional(
                                    {
                                        "email": Optional(str),
                                        "preferences": Optional(
                                            [Optional(str)]
                                        ),
                                    }
                                )
                            }
                        )
                    ]
                )
            },
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_optional_with_defaults(self):
        """Test optional values with default values."""
        valid_schemas = [
            {"port": Optional(int)},
            {"debug": Optional(bool)},
            {"name": Optional(str)},
            {"config": Optional({"timeout": int})},
            {"tags": Optional([str])},
            {"mixed": Optional((str, int))},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_invalid_optional_function_signatures(self):
        """Test optional functions with invalid signatures."""

        def invalid_param_name(invalid_name):
            return True

        def too_many_params(a, b, c):
            return True

        invalid_schemas = [
            {"key": Optional(invalid_param_name)},
            {"key": Optional(too_many_params)},
            {"key": Optional(lambda invalid: True)},
            {"key": Optional(lambda a, b, c: True)},
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_invalid_optional_array_definitions(self):
        """Test invalid optional array definitions."""
        invalid_schemas = [
            {"key": Optional([])},  # Empty array
            {"key": Optional([None])},  # Invalid element type
            {"key": Optional([object])},  # Invalid type
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_invalid_optional_tuple_definitions(self):
        """Test invalid optional tuple definitions."""
        invalid_schemas = [
            {"key": Optional(())},  # Empty tuple
            {"key": Optional((None,))},  # Invalid element type
            {"key": Optional((object,))},  # Invalid type
            {"key": Optional((int, None, str))},  # Invalid element in middle
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_invalid_optional_value_types(self):
        """Test optional schemas with invalid wrapped value types."""
        invalid_schemas = [
            {"key": Optional(None)},
            {"key": Optional(object())},
            {"key": Optional(Exception)},
            {"key": Optional(set())},
            {"key": Optional(complex(1, 2))},
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_optional_schema_conflicts(self):
        """Test detection of conflicting schema paths with optional values."""
        conflicting_schemas = [
            {"user": Optional({"name": str}), "user.name": str},
            {"items": Optional([str]), "items[0]": str},
            {"data.value": Optional(str), "data": Optional({"value": int})},
        ]

        for schema in conflicting_schemas:
            with pytest.raises(TOMLSchemaConflictError):
                validate_schema(schema)

    def test_complex_optional_schema(self):
        """Test a complex schema with mixed optional and required values."""

        def validate_email(value):
            return "@" in value

        def validate_port(value):
            return 1 <= value <= 65535

        schema = {
            "app": {
                "name": str,
                "version": str,
                "debug": Optional(bool),
                "features": Optional([str]),
            },
            "database": {
                "host": str,
                "port": Optional(int),
                "ssl": Optional(bool),
                "credentials": Optional(
                    {
                        "username": str,
                        "password": str,
                        "timeout": Optional(int),
                    }
                ),
            },
            "users": Optional(
                [
                    {
                        "name": str,
                        "email": validate_email,
                        "age": Optional(int),
                        "roles": Optional(
                            [str],
                        ),
                        "preferences": Optional(
                            {
                                "theme": Optional(str),
                                "notifications": Optional(bool),
                            }
                        ),
                    }
                ]
            ),
            "monitoring": Optional(
                {
                    "enabled": bool,
                    "endpoints": Optional([str]),
                    "alerts": Optional((str, validate_port, Optional(bool))),
                }
            ),
            "wildcards": {
                "*": Optional(str),
                "config*": Optional(lambda value: len(value) > 0),
            },
        }

        validate_schema(schema)

    def test_optional_with_wildcard_keys(self):
        """Test optional values with wildcard keys."""
        valid_schemas = [
            {"user*": Optional(int)},
            {"user.*": Optional(bool)},
            {"*.config": Optional(bool)},
            {"config*.value*": Optional(lambda value: True)},
            {"users": [Optional({"*": str})]},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

        invalid_schemas = [
            {"*": Optional(str)},
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_optional_edge_cases(self):
        """Test edge cases for optional values."""
        valid_schemas = [
            {"pattern": Optional(re.compile(r"\d+"))},
            {"timestamp": Optional(datetime)},
            {"date": Optional(date)},
            {"time": Optional(time)},
            {
                "level1": Optional(
                    {
                        "level2": Optional(
                            {"level3": Optional({"value": Optional(str)})}
                        )
                    }
                )
            },
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_invalid_type(self):
        """Test schema with valid Invalid type usage."""

        valid_schemas = [
            {"key": Invalid},  # Invalid class directly
            {"key": Invalid()},  # Invalid instance
            {"*": Invalid},  # Catch-all with Invalid class
            {"*": Invalid()},  # Catch-all with Invalid instance
            {"user*": Invalid},  # Wildcard with Invalid class
            {"*.config": Invalid()},  # Dotted wildcard with Invalid instance
            {"data.field": Invalid},  # Nested key with Invalid
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_invalid_invalid_in_arrays(self):
        """Test that Invalid cannot be used in arrays."""

        invalid_schemas = [
            {"key": [Invalid]},  # Invalid class in array
            {"key": [Invalid()]},  # Invalid instance in array
            {"items": [Invalid]},  # Array containing Invalid class
            {"data": [Invalid()]},  # Array containing Invalid instance
        ]

        for schema in invalid_schemas:
            with pytest.raises(
                TOMLSchemaValidationError,
                match="array cannot contain Invalid type",
            ):
                validate_schema(schema)

    def test_invalid_invalid_in_tuples(self):
        """Test that Invalid cannot be used in tuples."""

        invalid_schemas = [
            {"key": (Invalid,)},  # Invalid class in tuple
            {"key": (Invalid(),)},  # Invalid instance in tuple
            {"key": (str, Invalid)},  # Invalid class with other types
            {"key": (int, Invalid(), str)},  # Invalid instance with other types
            {"mixed": (str, Invalid, bool)},  # Invalid class in mixed tuple
        ]

        for schema in invalid_schemas:
            with pytest.raises(
                TOMLSchemaValidationError,
                match="tuple cannot contain Invalid type",
            ):
                validate_schema(schema)

    def test_invalid_optional_wrapping_invalid(self):
        """Test that Optional cannot wrap Invalid type."""

        invalid_schemas = [
            {"key": Optional(Invalid)},  # Optional wrapping Invalid class
            {"key": Optional(Invalid())},  # Optional wrapping Invalid instance
            {"data": Optional(Invalid)},  # Another case with class
            {"field": Optional(Invalid())},  # Another case with instance
        ]

        for schema in invalid_schemas:
            with pytest.raises(
                TOMLSchemaValidationError,
                match="cannot wrap Invalid type with Optional",
            ):
                validate_schema(schema)

    def test_invalid_with_nested_structures(self):
        """Test Invalid in various nested structures."""

        valid_schemas = [
            {
                "app": {
                    "name": str,
                    "legacy_field": Invalid,
                }
            },
            {
                "config": {
                    "database": {
                        "deprecated_option": Invalid(),
                    }
                }
            },
            {
                "users": [
                    {
                        "name": str,
                        "old_field": Invalid,
                    }
                ]
            },
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_invalid_edge_cases(self):
        """Test edge cases for Invalid type."""
        valid_schemas = [
            {"": Invalid},  # Empty key with Invalid (if allowed)
            {"user.name": Invalid},  # Dotted key with Invalid
            {"items[0]": Invalid},  # Array notation with Invalid
            {"*_deprecated": Invalid()},  # Wildcard pattern with Invalid
        ]

        for schema in valid_schemas:
            try:
                validate_schema(schema)
            except TOMLKeyValidationError:
                pass

    def test_invalid_class_vs_instance_equivalence(self):
        """
        Test that Invalid class and Invalid()
        instance are treated equivalently.
        """

        schema_with_class = {"deprecated": Invalid}
        schema_with_instance = {"deprecated": Invalid()}

        validate_schema(schema_with_class)
        validate_schema(schema_with_instance)

        invalid_schemas = [
            {"key": [Invalid]},  # Class in array
            {"key": [Invalid()]},  # Instance in array
            {"key": (Invalid,)},  # Class in tuple
            {"key": (Invalid(),)},  # Instance in tuple
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_mixed_invalid_and_valid_types(self):
        """Test schemas mixing Invalid with other valid types."""

        valid_schemas = [
            {
                "name": str,
                "age": int,
                "deprecated_field": Invalid,
                "optional_field": Optional(str),
            },
            {
                "app": {
                    "version": str,
                    "old_config": Invalid(),
                },
                "database": {
                    "host": str,
                    "port": int,
                },
            },
            {
                "users": [
                    {
                        "name": str,
                        "legacy_id": Invalid,
                    }
                ],
                "settings": {
                    "theme": str,
                    "deprecated_setting": Invalid(),
                },
            },
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_invalid_in_complex_wildcard_patterns(self):
        """Test Invalid with complex wildcard patterns."""

        valid_schemas = [
            {"*": Invalid},  # Catch-all wildcard
            {"user*": Invalid()},  # Prefix wildcard
            {"*_deprecated": Invalid},  # Suffix wildcard
            {"config*.old*": Invalid()},  # Multiple wildcards
            {"*.legacy": Invalid},  # Dotted wildcard
            {"data*.old*.field": Invalid()},  # Complex dotted wildcard
        ]

        for schema in valid_schemas:
            validate_schema(schema)


class TestLiteralTypeValidation:
    """Test cases for Literal type validation in schemas."""

    def test_valid_literal_single_string(self):
        """Test schema with valid single string literal."""
        valid_schemas = [
            {"status": Literal("active")},
            {"level": Literal("debug")},
            {"mode": Literal("production")},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_literal_multiple_strings(self):
        """Test schema with valid multiple string literals."""
        valid_schemas = [
            {"status": Literal(["active", "inactive", "pending"])},
            {"level": Literal(["debug", "info", "warning", "error"])},
            {"environment": Literal(["dev", "staging", "prod"])},
            {"priority": Literal(["low", "medium", "high", "critical"])},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_literal_nested_in_dict(self):
        """Test literals in nested dictionary structures."""
        valid_schemas = [
            {
                "config": {
                    "log_level": Literal(["debug", "info", "error"]),
                    "environment": Literal("production"),
                }
            },
            {
                "app": {
                    "database": {
                        "type": Literal(["mysql", "postgresql", "sqlite"]),
                        "ssl_mode": Literal("require"),
                    }
                }
            },
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_literal_in_arrays(self):
        """Test literals as array element types."""
        valid_schemas = [
            {"statuses": [Literal(["active", "inactive"])]},
            {"log_levels": [Literal("debug")]},
            {"environments": [Literal(["dev", "prod", "staging"])]},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_literal_in_tuples(self):
        """Test literals in tuple type definitions."""
        valid_schemas = [
            {"value": (str, Literal(["yes", "no"]))},
            {"config": (int, Literal("active"), bool)},
            {"mixed": (Literal(["small", "large"]), str, Literal("enabled"))},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_optional_literals(self):
        """Test optional literal types."""
        valid_schemas = [
            {"status": Optional(Literal(["active", "inactive"]))},
            {"level": Optional(Literal("debug"))},
            {"mode": Optional(Literal(["dev", "prod"]))},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_valid_literal_with_wildcards(self):
        """Test literals with wildcard patterns."""
        valid_schemas = [
            {"status_*": Literal(["active", "inactive"])},
            {"*_level": Literal("debug")},
            {"config.*.mode": Literal(["strict", "permissive"])},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_invalid_literal_empty_list(self):
        """Test that empty literal lists are invalid."""
        invalid_schemas = [
            {"status": Literal([])},
            {"level": Literal([])},
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_invalid_literal_non_string_values(self):
        """Test that non-string literal values are invalid."""
        invalid_schemas = [
            {"status": Literal([123])},  # type: ignore
            {"level": Literal([True, False])},  # type: ignore
            {"mode": Literal([1.5, 2.7])},  # type: ignore
            {"mixed": Literal(["valid", 123, "also_valid"])},  # type: ignore
            {"single": Literal(42)},  # type: ignore
            {"boolean": Literal(True)},  # type: ignore
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_invalid_literal_none_values(self):
        """Test that None values in literals are invalid."""
        invalid_schemas = [
            {"status": Literal([None])},  # type: ignore
            {"mixed": Literal(["active", None, "inactive"])},  # type: ignore
            {"single": Literal(None)},  # type: ignore
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_invalid_literal_nested_structures(self):
        """Test that nested structures in literals are invalid."""
        invalid_schemas = [
            {"config": Literal([{"nested": "dict"}])},  # type: ignore
            {"items": Literal([["nested", "list"]])},  # type: ignore
            {"mixed": Literal(["valid", {"invalid": "dict"}])},  # type: ignore
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_literal_duplicate_values(self):
        """Test that duplicate values in literals are handled."""
        valid_schemas = [
            {"status": Literal(["active", "active", "inactive"])},
            {"level": Literal(["debug", "info", "debug", "error"])},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_literal_case_sensitivity(self):
        """Test that literal values are case-sensitive."""
        valid_schemas = [
            {"status": Literal(["Active", "ACTIVE", "active"])},
            {"level": Literal(["Debug", "DEBUG", "debug"])},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_literal_empty_string_values(self):
        """Test literals with empty string values."""
        valid_schemas = [
            {"status": Literal(["", "active"])},
            {"level": Literal("")},
            {"mixed": Literal(["", "debug", "info", ""])},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_literal_whitespace_values(self):
        """Test literals with whitespace-only values."""
        valid_schemas = [
            {"status": Literal([" ", "active"])},
            {"level": Literal("   ")},
            {"mixed": Literal(["\t", "\n", "debug"])},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_literal_unicode_values(self):
        """Test literals with unicode values."""
        valid_schemas = [
            {"status": Literal(["активный", "неактивный"])},
            {"level": Literal("débogage")},
            {"emoji": Literal(["✅", "❌", "⚠️"])},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_complex_literal_schema(self):
        """Test a complex schema with various literal usages."""
        schema = {
            "app": {
                "name": str,
                "environment": Literal(
                    ["development", "staging", "production"]
                ),
                "log_level": Optional(
                    Literal(["debug", "info", "warning", "error"])
                ),
            },
            "database": {
                "type": Literal(["mysql", "postgresql", "sqlite"]),
                "ssl_mode": Optional(Literal("require")),
                "connection_pool": {
                    "strategy": Literal(["fixed", "dynamic"]),
                    "health_check": Optional(
                        Literal(["ping", "select", "none"])
                    ),
                },
            },
            "services": [
                {
                    "name": str,
                    "status": Literal(["running", "stopped", "error"]),
                    "restart_policy": Optional(
                        Literal(["always", "on-failure", "never"])
                    ),
                }
            ],
            "feature_flags": {
                "*_enabled": Literal(["true", "false", "auto"]),
                "experimental_*": Optional(Literal(["on", "off"])),
            },
            "mixed_config": (
                str,
                Literal(["json", "yaml", "toml"]),
                Optional(bool),
            ),
        }

        validate_schema(schema)

    def test_literal_conflicts_with_other_schema_keys(self):
        """Test literal definitions don't conflict with other schema keys."""
        valid_schemas = [
            {
                "status": Literal(["active"]),
                "user.status": str,
            },
            {
                "config": {
                    "mode": Literal(["strict"]),
                    "debug": bool,
                },
                "config.level": str,
            },
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_literal_with_array_notation_keys(self):
        """Test literals with array notation keys."""
        valid_schemas = [
            {"items[0]": Literal(["first", "primary"])},
            {"users[1].role": Literal(["admin", "user", "guest"])},
            {"config.servers[0].type": Optional(Literal(["web", "api", "db"]))},
        ]

        for schema in valid_schemas:
            validate_schema(schema)

    def test_invalid_literal_in_optional_wrapping(self):
        """Test invalid literal definitions when wrapped in Optional."""
        invalid_schemas = [
            {"status": Optional(Literal([]))},
            {"level": Optional(Literal([123]))},  # type: ignore
            {"mode": Optional(Literal(None))},  # type: ignore
        ]

        for schema in invalid_schemas:
            with pytest.raises(TOMLSchemaValidationError):
                validate_schema(schema)

    def test_literal_edge_cases_in_validation(self):
        """Test edge cases for literal validation."""
        valid_schemas = [
            {"key": Literal("single_value")},
            {"special_chars": Literal(["@#$%", "^&*()", "{}[]"])},
            {"numbers_as_strings": Literal(["123", "456", "0"])},
            {"mixed_case": Literal(["CamelCase", "snake_case", "UPPER_CASE"])},
        ]

        for schema in valid_schemas:
            validate_schema(schema)
