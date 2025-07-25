"""Tests for the validate_data function."""

import re
from datetime import date, datetime, time

import pytest

from tomlval.enums import ValidationErrorCode
from tomlval.errors.key_validation_error import TOMLKeyValidationError
from tomlval.toml_schema import TOMLSchema
from tomlval.types import Invalid, Optional
from tomlval.utils.validate_data import validate_data


class TestValidateDataBasic:
    """Test basic validation functionality."""

    def test_valid_data_no_errors(self):
        """Test that valid data returns no errors."""
        data = {"name": "John", "age": 30}
        schema = TOMLSchema({"name": str, "age": int})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_data_type(self):
        """Test validation with non-dictionary data."""
        with pytest.raises(TypeError, match="Data must be a dictionary"):
            validate_data("no dict", TOMLSchema({}))  # type: ignore[arg-type]

    def test_invalid_schema_type(self):
        """Test validation with non-TOMLSchema schema."""
        with pytest.raises(
            TypeError, match="Schema must be a TOMLSchema instance"
        ):
            validate_data({}, {})  # type: ignore[arg-type]


class TestPrimitiveTypes:
    """Test validation of primitive types."""

    def test_valid_string(self):
        """Test valid string validation."""
        data = {"name": "John"}
        schema = TOMLSchema({"name": str})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_string_type(self):
        """Test invalid string type."""
        data = {"name": 123}
        schema = TOMLSchema({"name": str})

        errors = validate_data(data, schema)

        assert errors == {"name": ValidationErrorCode.INVALID_TYPE}

    def test_valid_integer(self):
        """Test valid integer validation."""
        data = {"age": 30}
        schema = TOMLSchema({"age": int})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_integer_type(self):
        """Test invalid integer type."""
        data = {"age": "thirty"}
        schema = TOMLSchema({"age": int})

        errors = validate_data(data, schema)

        assert errors == {"age": ValidationErrorCode.INVALID_TYPE}

    def test_valid_float(self):
        """Test valid float validation."""
        data = {"score": 95.5}
        schema = TOMLSchema({"score": float})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_float_type(self):
        """Test invalid float type."""
        data = {"score": "high"}
        schema = TOMLSchema({"score": float})

        errors = validate_data(data, schema)

        assert errors == {"score": ValidationErrorCode.INVALID_TYPE}

    def test_valid_boolean(self):
        """Test valid boolean validation."""
        data = {"active": True}
        schema = TOMLSchema({"active": bool})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_boolean_type(self):
        """Test invalid boolean type."""
        data = {"active": "yes"}
        schema = TOMLSchema({"active": bool})

        errors = validate_data(data, schema)

        assert errors == {"active": ValidationErrorCode.INVALID_TYPE}


class TestDatetimeTypes:
    """Test validation of datetime types."""

    def test_valid_datetime(self):
        """Test valid datetime validation."""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        data = {"created": dt}
        schema = TOMLSchema({"created": datetime})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_datetime_type(self):
        """Test invalid datetime type."""
        data = {"created": "2023-01-01"}
        schema = TOMLSchema({"created": datetime})

        errors = validate_data(data, schema)

        assert errors == {"created": ValidationErrorCode.DATETIME_PARSE_ERROR}

    def test_valid_date(self):
        """Test valid date validation."""
        d = date(2023, 1, 1)
        data = {"birthday": d}
        schema = TOMLSchema({"birthday": date})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_date_type(self):
        """Test invalid date type."""
        data = {"birthday": "January 1st"}
        schema = TOMLSchema({"birthday": date})

        errors = validate_data(data, schema)

        assert errors == {"birthday": ValidationErrorCode.DATETIME_PARSE_ERROR}

    def test_valid_time(self):
        """Test valid time validation."""
        t = time(12, 30, 0)
        data = {"meeting": t}
        schema = TOMLSchema({"meeting": time})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_time_type(self):
        """Test invalid time type."""
        data = {"meeting": "noon"}
        schema = TOMLSchema({"meeting": time})

        errors = validate_data(data, schema)

        assert errors == {"meeting": ValidationErrorCode.DATETIME_PARSE_ERROR}


class TestRegexValidation:
    """Test regex pattern validation."""

    def test_valid_regex_match(self):
        """Test valid regex pattern match."""
        pattern = re.compile(r"^\d{3}-\d{3}-\d{4}$")
        data = {"phone": "123-456-7890"}
        schema = TOMLSchema({"phone": pattern})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_regex_match(self):
        """Test invalid regex pattern match."""
        pattern = re.compile(r"^\d{3}-\d{3}-\d{4}$")
        data = {"phone": "invalid-phone"}
        schema = TOMLSchema({"phone": pattern})

        errors = validate_data(data, schema)

        assert errors == {"phone": ValidationErrorCode.REGEX_MISMATCH}

    def test_regex_with_non_string_value(self):
        """Test regex validation with non-string value."""
        pattern = re.compile(r"^\d+$")
        data = {"code": 123}
        schema = TOMLSchema({"code": pattern})

        errors = validate_data(data, schema)

        assert errors == {"code": ValidationErrorCode.INVALID_TYPE}


class TestFunctionValidation:
    """Test custom function validation."""

    def test_function_no_params_success(self):
        """Test function with no parameters that passes."""

        def always_true():
            return True

        data = {"value": "anything"}
        schema = TOMLSchema({"value": always_true})

        errors = validate_data(data, schema)

        assert not errors

    def test_function_no_params_failure(self):
        """Test function with no parameters that fails."""

        def always_false():
            return False

        data = {"value": "anything"}
        schema = TOMLSchema({"value": always_false})

        errors = validate_data(data, schema)

        assert errors == {"value": ValidationErrorCode.VALIDATION_FAILURE}

    def test_function_value_param_success(self):
        """Test function with value parameter that passes."""

        def check_positive(value):
            return value > 0

        data = {"number": 5}
        schema = TOMLSchema({"number": check_positive})

        errors = validate_data(data, schema)

        assert not errors

    def test_function_value_param_failure(self):
        """Test function with value parameter that fails."""

        def check_positive(value):
            return value > 0

        data = {"number": -5}
        schema = TOMLSchema({"number": check_positive})

        errors = validate_data(data, schema)

        assert errors == {"number": ValidationErrorCode.VALIDATION_FAILURE}

    def test_function_key_param_success(self):
        """Test function with key parameter that passes."""

        def check_key_length(key):
            return len(key) > 3

        data = {"username": "john"}
        schema = TOMLSchema({"username": check_key_length})

        errors = validate_data(data, schema)

        assert not errors

    def test_function_key_param_failure(self):
        """Test function with key parameter that fails."""

        def check_key_length(key):
            return len(key) > 10

        data = {"name": "john"}
        schema = TOMLSchema({"name": check_key_length})

        errors = validate_data(data, schema)

        assert errors == {"name": ValidationErrorCode.VALIDATION_FAILURE}

    def test_function_both_params_success(self):
        """Test function with both key and value parameters that passes."""

        def check_key_value_match(key, value):
            return key == value

        data = {"test": "test"}
        schema = TOMLSchema({"test": check_key_value_match})

        errors = validate_data(data, schema)

        assert not errors

    def test_function_both_params_failure(self):
        """Test function with both key and value parameters that fails."""

        def check_key_value_match(key, value):
            return key == value

        data = {"test": "different"}
        schema = TOMLSchema({"test": check_key_value_match})

        errors = validate_data(data, schema)

        assert errors == {"test": ValidationErrorCode.VALIDATION_FAILURE}

    def test_function_execution_error(self):
        """Test function that raises an exception."""

        def failing_function(value):
            raise ValueError("This function always fails")

        data = {"value": "test"}
        schema = TOMLSchema({"value": failing_function})

        errors = validate_data(data, schema)

        assert errors == {"value": ValidationErrorCode.FUNCTION_EXECUTION_ERROR}


class TestOptionalValues:
    """Test Optional wrapper validation."""

    def test_optional_present_valid(self):
        """Test optional value that is present and valid."""
        data = {"name": "John"}
        schema = TOMLSchema({"name": Optional(str)})

        errors = validate_data(data, schema)

        assert not errors

    def test_optional_present_invalid(self):
        """Test optional value that is present but invalid."""
        data = {"age": "thirty"}
        schema = TOMLSchema({"age": Optional(int)})

        errors = validate_data(data, schema)

        assert errors == {"age": ValidationErrorCode.INVALID_TYPE}

    def test_optional_missing(self):
        """Test optional value that is missing."""
        data = {}
        schema = TOMLSchema({"name": Optional(str)})

        errors = validate_data(data, schema)

        assert not errors

    def test_required_missing(self):
        """Test required value that is missing."""
        data = {}
        schema = TOMLSchema({"name": str})

        errors = validate_data(data, schema)

        assert errors == {"name": ValidationErrorCode.MISSING_KEY}


class TestInvalidType:
    """Test Invalid type validation."""

    def test_invalid_type_present(self):
        """Test that Invalid type marks key as invalid."""
        data = {"forbidden": "value"}
        schema = TOMLSchema({"forbidden": Invalid})

        errors = validate_data(data, schema)

        assert errors == {"forbidden": ValidationErrorCode.INVALID_KEY}

    def test_invalid_instance_present(self):
        """Test that Invalid instance marks key as invalid."""
        data = {"forbidden": "value"}
        schema = TOMLSchema({"forbidden": Invalid()})

        errors = validate_data(data, schema)

        assert errors == {"forbidden": ValidationErrorCode.INVALID_KEY}


class TestNestedDictionaries:
    """Test validation of nested dictionaries."""

    def test_valid_nested_dict(self):
        """Test valid nested dictionary validation."""
        data = {"user": {"name": "John", "age": 30}}
        schema = TOMLSchema({"user": {"name": str, "age": int}})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_nested_dict_type(self):
        """Test nested dictionary with wrong type for parent."""
        data = {"user": "not a dict"}
        schema = TOMLSchema({"user": {"name": str}})

        errors = validate_data(data, schema)

        assert errors == {"user": ValidationErrorCode.INVALID_TYPE}

    def test_invalid_nested_dict_field(self):
        """Test nested dictionary with invalid field."""
        data = {"user": {"name": 123, "age": 30}}  # Should be string
        schema = TOMLSchema({"user": {"name": str, "age": int}})

        errors = validate_data(data, schema)

        assert errors == {"name": ValidationErrorCode.INVALID_TYPE}

    def test_deeply_nested_dict(self):
        """Test deeply nested dictionary validation."""
        data = {"level1": {"level2": {"level3": {"value": "deep"}}}}
        schema = TOMLSchema({"level1": {"level2": {"level3": {"value": str}}}})

        errors = validate_data(data, schema)

        assert not errors


class TestArrayValidation:
    """Test array validation."""

    def test_valid_single_type_array(self):
        """Test valid single-type array."""
        data = {"numbers": [1, 2, 3, 4]}
        schema = TOMLSchema({"numbers": [int]})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_single_type_array(self):
        """Test invalid single-type array."""
        data = {"numbers": [1, "two", 3]}
        schema = TOMLSchema({"numbers": [int]})

        errors = validate_data(data, schema)

        assert errors == {"numbers[1]": ValidationErrorCode.INVALID_TYPE}

    def test_valid_mixed_type_array(self):
        """Test valid mixed-type array."""
        data = {"values": [1, "two", 3.0]}
        schema = TOMLSchema({"values": [int, str, float]})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_mixed_type_array(self):
        """Test invalid mixed-type array."""
        data = {"values": [1, True, 3.0]}
        schema = TOMLSchema({"values": [int, str, float]})

        errors = validate_data(data, schema)

        assert errors == {
            "values[1]": ValidationErrorCode.INVALID_ARRAY_ELEMENT
        }

    def test_array_with_wrong_container_type(self):
        """Test array schema with non-array data."""
        data = {"items": "not an array"}
        schema = TOMLSchema({"items": [str]})

        errors = validate_data(data, schema)

        assert errors == {"items": ValidationErrorCode.INVALID_TYPE}

    def test_array_of_dicts(self):
        """Test array containing dictionaries."""
        data = {
            "users": [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        }
        schema = TOMLSchema({"users": [{"name": str, "age": int}]})

        errors = validate_data(data, schema)

        assert not errors

    def test_array_of_dicts_with_error(self):
        """Test array of dictionaries with validation error."""
        data = {
            "users": [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": "twenty-five"},  # Invalid age
            ]
        }
        schema = TOMLSchema({"users": [{"name": str, "age": int}]})

        errors = validate_data(data, schema)

        assert errors == {"age": ValidationErrorCode.INVALID_TYPE}


class TestTupleValidation:
    """Test tuple (union type) validation."""

    def test_valid_tuple_first_type(self):
        """Test tuple validation with first type matching."""
        data = {"value": 42}
        schema = TOMLSchema({"value": (int, str)})

        errors = validate_data(data, schema)

        assert not errors

    def test_valid_tuple_second_type(self):
        """Test tuple validation with second type matching."""
        data = {"value": "hello"}
        schema = TOMLSchema({"value": (int, str)})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_tuple_no_match(self):
        """Test tuple validation with no type matching."""
        data = {"value": 3.14}  # float not in (int, str)
        schema = TOMLSchema({"value": (int, str)})

        errors = validate_data(data, schema)

        assert errors == {"value": ValidationErrorCode.INVALID_TUPLE_TYPE}

    def test_complex_tuple_with_functions(self):
        """Test tuple with functions and types."""

        def is_positive(value):
            return isinstance(value, int) and value > 0

        data = {"value": -5}
        schema = TOMLSchema({"value": (is_positive, str)})

        errors = validate_data(data, schema)

        assert errors == {"value": ValidationErrorCode.INVALID_TUPLE_TYPE}


class TestDottedKeyValidation:
    """Test dotted key notation validation."""

    def test_valid_dotted_key(self):
        """Test valid dotted key validation."""
        data = {"user": {"profile": {"name": "John"}}}
        schema = TOMLSchema({"user.profile.name": str})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_dotted_key_type(self):
        """Test invalid dotted key type."""
        data = {"user": {"profile": {"name": 123}}}
        schema = TOMLSchema({"user.profile.name": str})

        errors = validate_data(data, schema)

        assert errors == {"user.profile.name": ValidationErrorCode.INVALID_TYPE}

    def test_missing_dotted_key_path(self):
        """Test missing path in dotted key."""
        data = {"user": {"other": "value"}}
        schema = TOMLSchema({"user.profile.name": str})

        errors = validate_data(data, schema)

        assert errors == {"user.profile.name": ValidationErrorCode.MISSING_KEY}

    def test_optional_dotted_key_missing(self):
        """Test missing optional dotted key."""
        data = {"user": {"other": "value"}}
        schema = TOMLSchema({"user.profile.name": Optional(str)})

        errors = validate_data(data, schema)

        assert not errors

    def test_dotted_key_with_non_dict_intermediate(self):
        """Test dotted key with non-dict in path."""
        data = {"user": "not a dict"}
        schema = TOMLSchema({"user.name": str})

        errors = validate_data(data, schema)

        assert errors == {"user.name": ValidationErrorCode.MISSING_KEY}


class TestArrayNotationValidation:
    """Test array notation validation."""

    def test_valid_array_notation(self):
        """Test valid array notation validation."""
        data = {"items": ["first", "second", "third"]}
        schema = TOMLSchema({"items[1]": str})

        errors = validate_data(data, schema)

        assert not errors

    def test_invalid_array_notation_type(self):
        """Test invalid array notation type."""
        data = {"items": ["first", 123, "third"]}
        schema = TOMLSchema({"items[1]": str})

        errors = validate_data(data, schema)

        assert errors == {"items[1]": ValidationErrorCode.INVALID_TYPE}

    def test_array_notation_missing_array(self):
        """Test array notation with missing array."""
        data = {}
        schema = TOMLSchema({"items[0]": str})

        errors = validate_data(data, schema)

        assert errors == {"items[0]": ValidationErrorCode.MISSING_KEY}

    def test_array_notation_wrong_container_type(self):
        """Test array notation with non-array."""
        data = {"items": "not an array"}
        schema = TOMLSchema({"items[0]": str})

        errors = validate_data(data, schema)

        assert errors == {"items[0]": ValidationErrorCode.INVALID_TYPE}

    def test_array_notation_index_out_of_bounds(self):
        """Test array notation with out of bounds index."""
        data = {"items": ["only one"]}
        schema = TOMLSchema({"items[5]": str})

        errors = validate_data(data, schema)

        assert errors == {"items[5]": ValidationErrorCode.MISSING_KEY}

    def test_array_notation_invalid_index(self):
        """Test array notation with invalid index during schema creation."""
        with pytest.raises(
            TOMLKeyValidationError, match="Array index 'invalid'"
        ):
            TOMLSchema({"items[invalid]": str})

    def test_optional_array_notation_missing(self):
        """Test optional array notation that's missing."""
        data = {"items": ["only one"]}
        schema = TOMLSchema({"items[5]": Optional(str)})

        errors = validate_data(data, schema)

        assert not errors


class TestWildcardPatterns:
    """Test wildcard pattern validation."""

    def test_simple_wildcard_match(self):
        """Test simple wildcard pattern matching."""
        data = {"user1": "John", "user2": "Jane", "admin": "Bob"}
        schema = TOMLSchema({"user*": str, "admin": str})

        errors = validate_data(data, schema)

        assert not errors

    def test_simple_wildcard_invalid(self):
        """Test simple wildcard with invalid type."""
        data = {"user1": 123, "user2": "Jane"}  # user1 should be string
        schema = TOMLSchema({"user*": str})

        errors = validate_data(data, schema)

        assert errors == {"user1": ValidationErrorCode.INVALID_TYPE}

    def test_dotted_wildcard_pattern(self):
        """Test dotted wildcard pattern."""
        data = {
            "user1": {"name": "John"},
            "user2": {"name": "Jane"},
            "admin": {"name": "Bob"},
        }
        schema = TOMLSchema({"user*.name": str})

        errors = validate_data(data, schema)

        assert not errors

    def test_pattern_specificity_priority(self):
        """Test that more specific patterns have priority."""
        data = {"user123": "specific", "user": "general"}
        schema = TOMLSchema(
            {
                "*": Invalid,  # Catch-all forbids everything
                "user*": str,  # More specific allows user* patterns
                "user123": str,  # Most specific
            }
        )

        errors = validate_data(data, schema)

        assert not errors

    def test_catch_all_wildcard_allow(self):
        """Test catch-all wildcard allowing keys."""
        data = {"anything": "value", "whatever": "data"}
        schema = TOMLSchema({"*": str})

        errors = validate_data(data, schema)

        assert not errors

    def test_catch_all_wildcard_forbid(self):
        """Test catch-all wildcard forbidding keys."""
        data = {"forbidden": "value"}
        schema = TOMLSchema({"*": Invalid})

        errors = validate_data(data, schema)

        assert errors == {"forbidden": ValidationErrorCode.INVALID_KEY}

    def test_mixed_wildcard_priority(self):
        """Test mixed wildcard patterns with priority."""
        data = {
            "user_admin": "should be string",
            "user_guest": "should be string",
            "other_key": "should be invalid",
        }
        schema = TOMLSchema(
            {
                "user_*": str,  # Specific pattern
                "*": Invalid,  # Catch-all forbids others
            }
        )

        errors = validate_data(data, schema)

        assert errors == {"other_key": ValidationErrorCode.INVALID_KEY}


class TestComplexScenarios:
    """Test complex validation scenarios."""

    def test_comprehensive_schema(self):
        """Test comprehensive schema with multiple validation types."""
        data = {
            "app": {"name": "MyApp", "version": "1.0.0", "debug": True},
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {"username": "admin", "password": "secret123"},
            },
            "features": ["auth", "logging", "metrics"],
            "servers": [{"name": "web1", "cpu": 4}, {"name": "web2", "cpu": 8}],
        }

        def valid_version(value):
            return bool(re.match(r"^\d+\.\d+\.\d+$", value))

        schema = TOMLSchema(
            {
                "app.name": str,
                "app.version": valid_version,
                "app.debug": bool,
                "database": {
                    "host": str,
                    "port": int,
                    "credentials": {"username": str, "password": str},
                },
                "features": [str],
                "servers": [{"name": str, "cpu": int}],
            }
        )

        errors = validate_data(data, schema)

        assert not errors

    def test_comprehensive_schema_with_errors(self):
        """Test comprehensive schema with various errors."""
        data = {
            "app": {
                "name": 123,  # Should be string
                "version": "invalid-version",  # Should match version pattern
                "debug": "yes",  # Should be boolean
            },
            "database": {
                "host": "localhost",
                "port": "5432",  # Should be int
                "credentials": {
                    "username": "admin"
                    # Missing password
                },
            },
            "features": ["auth", 123, "metrics"],  # 123 should be string
            "servers": [
                {"name": "web1", "cpu": "four"},  # cpu should be int
                {"name": 456, "cpu": 8},  # name should be string
            ],
        }

        def valid_version(value):
            return bool(re.match(r"^\d+\.\d+\.\d+$", value))

        schema = TOMLSchema(
            {
                "app.name": str,
                "app.version": valid_version,
                "app.debug": bool,
                "database": {
                    "host": str,
                    "port": int,
                    "credentials": {"username": str, "password": str},
                },
                "features": [str],
                "servers": [{"name": str, "cpu": int}],
            }
        )

        errors = validate_data(data, schema)

        expected_errors = {
            "app.name": ValidationErrorCode.INVALID_TYPE,
            "app.version": ValidationErrorCode.VALIDATION_FAILURE,
            "app.debug": ValidationErrorCode.INVALID_TYPE,
            "port": ValidationErrorCode.INVALID_TYPE,
            "password": ValidationErrorCode.MISSING_KEY,
            "features[1]": ValidationErrorCode.INVALID_TYPE,
            "cpu": ValidationErrorCode.INVALID_TYPE,
            "name": ValidationErrorCode.INVALID_TYPE,
        }

        assert errors == expected_errors

    def test_priority_system_comprehensive(self):
        """Test comprehensive priority system."""
        data = {
            "user_admin_settings": "specific",
            "user_guest_profile": "general user",
            "system_config": "system",
            "random_key": "should be forbidden",
        }

        schema = TOMLSchema(
            {
                "user_admin_settings": str,  # Most specific
                "user_*_profile": str,  # Medium specific
                "user_*": str,  # Less specific
                "system_*": str,  # Different pattern
                "*": Invalid,  # Catch-all forbids others
            }
        )

        errors = validate_data(data, schema)

        assert errors == {"random_key": ValidationErrorCode.INVALID_KEY}

    def test_edge_case_empty_data(self):
        """Test edge case with empty data."""
        data = {}
        schema = TOMLSchema(
            {"required": str, "optional": Optional(str), "*": Invalid}
        )

        errors = validate_data(data, schema)

        assert errors == {"required": ValidationErrorCode.MISSING_KEY}

    def test_edge_case_empty_schema(self):
        """Test edge case with empty schema."""
        data = {"key": "value"}
        schema = TOMLSchema({})

        errors = validate_data(data, schema)

        assert not errors

    def test_quoted_keys(self):
        """Test handling of quoted keys."""
        data = {"key.with.dots": "value"}
        schema = TOMLSchema({"'key.with.dots'": str})

        errors = validate_data(data, schema)

        assert errors == {"'key.with.dots'": ValidationErrorCode.MISSING_KEY}
