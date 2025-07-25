"""Tests for the to_dict utility function."""

import pytest

from tomlval.toml_error import (
    INVALID_ARRAY_ELEMENT,
    INVALID_TYPE,
    MISSING_KEY,
    REGEX_MISMATCH,
    VALIDATION_FAILURE,
    TOMLError,
)
from tomlval.utils.to_dict import _parse_key_path, _set_nested_value, to_dict


class TestToDict:
    """Test cases for the to_dict function."""

    def test_empty_dict(self):
        """Test with empty input dictionary."""
        result = to_dict({})
        assert not result

    def test_simple_keys(self):
        """Test with simple flat keys (no nesting)."""
        flat_errors = {
            "name": TOMLError(INVALID_TYPE),
            "age": TOMLError(MISSING_KEY),
            "active": TOMLError(VALIDATION_FAILURE),
        }
        expected = {
            "name": TOMLError(INVALID_TYPE),
            "age": TOMLError(MISSING_KEY),
            "active": TOMLError(VALIDATION_FAILURE),
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_nested_keys(self):
        """Test with dot notation nested keys."""
        flat_errors = {
            "user.name": TOMLError(INVALID_TYPE),
            "user.email": TOMLError(REGEX_MISMATCH),
            "config.debug": TOMLError(INVALID_TYPE),
        }
        expected = {
            "user": {
                "name": TOMLError(INVALID_TYPE),
                "email": TOMLError(REGEX_MISMATCH),
            },
            "config": {"debug": TOMLError(INVALID_TYPE)},
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_deep_nesting(self):
        """Test with deeply nested keys."""
        flat_errors = {
            "app.database.connection.host": TOMLError(MISSING_KEY),
            "app.database.connection.port": TOMLError(INVALID_TYPE),
            "app.cache.redis.timeout": TOMLError(VALIDATION_FAILURE),
        }
        expected = {
            "app": {
                "database": {
                    "connection": {
                        "host": TOMLError(MISSING_KEY),
                        "port": TOMLError(INVALID_TYPE),
                    }
                },
                "cache": {"redis": {"timeout": TOMLError(VALIDATION_FAILURE)}},
            }
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_array_indices(self):
        """Test with array index notation."""
        flat_errors = {
            "items[0].name": TOMLError(INVALID_TYPE),
            "items[0].price": TOMLError(MISSING_KEY),
            "items[2].category": TOMLError(VALIDATION_FAILURE),
        }
        expected = {
            "items": [
                {
                    "name": TOMLError(INVALID_TYPE),
                    "price": TOMLError(MISSING_KEY),
                },
                None,
                {"category": TOMLError(VALIDATION_FAILURE)},
            ]
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_array_element_errors(self):
        """Test with errors on array elements themselves."""
        flat_errors = {
            "tasks[0]": TOMLError(INVALID_ARRAY_ELEMENT),
            "tasks[2]": TOMLError(INVALID_TYPE),
            "data[1].value": TOMLError(MISSING_KEY),
        }
        expected = {
            "tasks": [
                TOMLError(INVALID_ARRAY_ELEMENT),
                None,
                TOMLError(INVALID_TYPE),
            ],
            "data": [None, {"value": TOMLError(MISSING_KEY)}],
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_mixed_structure(self):
        """Test with mixed dictionary and array structures."""
        flat_errors = {
            "config.servers[0].host": TOMLError(INVALID_TYPE),
            "config.servers[0].port": TOMLError(VALIDATION_FAILURE),
            "config.servers[1].ssl.enabled": TOMLError(MISSING_KEY),
            "config.debug": TOMLError(INVALID_TYPE),
            "users[0].permissions[1]": TOMLError(INVALID_ARRAY_ELEMENT),
        }
        expected = {
            "config": {
                "servers": [
                    {
                        "host": TOMLError(INVALID_TYPE),
                        "port": TOMLError(VALIDATION_FAILURE),
                    },
                    {"ssl": {"enabled": TOMLError(MISSING_KEY)}},
                ],
                "debug": TOMLError(INVALID_TYPE),
            },
            "users": [
                {"permissions": [None, TOMLError(INVALID_ARRAY_ELEMENT)]}
            ],
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_sparse_arrays(self):
        """Test with sparse array indices."""
        flat_errors = {
            "items[5].name": TOMLError(INVALID_TYPE),
            "items[10]": TOMLError(INVALID_ARRAY_ELEMENT),
        }
        expected = {
            "items": [
                None,
                None,
                None,
                None,
                None,
                {"name": TOMLError(INVALID_TYPE)},
                None,
                None,
                None,
                None,
                TOMLError(INVALID_ARRAY_ELEMENT),
            ]
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_complex_real_world_example(self):
        """Test with a complex real-world example."""
        flat_errors = {
            "startup_tasks[1].args": TOMLError(INVALID_TYPE),
            "startup_tasks[1].timeout": TOMLError(INVALID_TYPE),
            "database.connection.pool_size": TOMLError(VALIDATION_FAILURE),
            "api.cors.allowed_origins[0]": TOMLError(REGEX_MISMATCH),
            "plugins.analytics.config.tracking_id": TOMLError(MISSING_KEY),
            "scheduled_tasks[0].enabled": TOMLError(INVALID_TYPE),
        }
        expected = {
            "startup_tasks": [
                None,
                {
                    "args": TOMLError(INVALID_TYPE),
                    "timeout": TOMLError(INVALID_TYPE),
                },
            ],
            "database": {
                "connection": {"pool_size": TOMLError(VALIDATION_FAILURE)}
            },
            "api": {"cors": {"allowed_origins": [TOMLError(REGEX_MISMATCH)]}},
            "plugins": {
                "analytics": {"config": {"tracking_id": TOMLError(MISSING_KEY)}}
            },
            "scheduled_tasks": [{"enabled": TOMLError(INVALID_TYPE)}],
        }
        result = to_dict(flat_errors)
        assert result == expected


class TestParseKeyPath:
    """Test cases for the _parse_key_path function."""

    def test_simple_key(self):
        """Test parsing a simple key."""
        result = _parse_key_path("name")
        expected = [{"type": "key", "value": "name"}]
        assert result == expected

    def test_nested_keys(self):
        """Test parsing nested keys with dots."""
        result = _parse_key_path("user.profile.name")
        expected = [
            {"type": "key", "value": "user"},
            {"type": "key", "value": "profile"},
            {"type": "key", "value": "name"},
        ]
        assert result == expected

    def test_array_index(self):
        """Test parsing array index notation."""
        result = _parse_key_path("items[0]")
        expected = [
            {"type": "key", "value": "items"},
            {"type": "index", "value": 0},
        ]
        assert result == expected

    def test_array_with_nested_key(self):
        """Test parsing array index with nested key."""
        result = _parse_key_path("items[0].name")
        expected = [
            {"type": "key", "value": "items"},
            {"type": "index", "value": 0},
            {"type": "key", "value": "name"},
        ]
        assert result == expected

    def test_multiple_array_indices(self):
        """Test parsing multiple array indices."""
        result = _parse_key_path("matrix[1][2]")
        expected = [
            {"type": "key", "value": "matrix"},
            {"type": "index", "value": 1},
            {"type": "index", "value": 2},
        ]
        assert result == expected

    def test_complex_path(self):
        """Test parsing a complex path with mixed notation."""
        result = _parse_key_path("config.servers[0].ssl.certs[1].path")
        expected = [
            {"type": "key", "value": "config"},
            {"type": "key", "value": "servers"},
            {"type": "index", "value": 0},
            {"type": "key", "value": "ssl"},
            {"type": "key", "value": "certs"},
            {"type": "index", "value": 1},
            {"type": "key", "value": "path"},
        ]
        assert result == expected

    def test_invalid_array_index(self):
        """Test parsing invalid array index (non-numeric)."""
        result = _parse_key_path("items[invalid]")
        expected = [
            {"type": "key", "value": "items"},
            {"type": "key", "value": "[invalid]"},
        ]
        assert result == expected

    def test_unclosed_bracket(self):
        """Test parsing unclosed bracket."""
        result = _parse_key_path("items[0")
        expected = [
            {"type": "key", "value": "items"},
            {"type": "key", "value": "[0"},
        ]
        assert result == expected

    def test_empty_brackets(self):
        """Test parsing empty brackets."""
        result = _parse_key_path("items[]")
        expected = [
            {"type": "key", "value": "items"},
            {"type": "key", "value": "[]"},
        ]
        assert result == expected


class TestSetNestedValue:
    """Test cases for the _set_nested_value function."""

    def test_set_simple_key(self):
        """Test setting a simple key value."""
        nested = {}
        error = TOMLError(INVALID_TYPE)
        _set_nested_value(nested, "name", error)
        assert nested == {"name": error}

    def test_set_nested_key(self):
        """Test setting a nested key value."""
        nested = {}
        error = TOMLError(INVALID_TYPE)
        _set_nested_value(nested, "user.name", error)
        assert nested == {"user": {"name": error}}

    def test_set_array_element(self):
        """Test setting an array element."""
        nested = {}
        error = TOMLError(INVALID_ARRAY_ELEMENT)
        _set_nested_value(nested, "items[0]", error)
        assert nested == {"items": [error]}

    def test_set_nested_array_element(self):
        """Test setting a nested array element property."""
        nested = {}
        error = TOMLError(INVALID_TYPE)
        _set_nested_value(nested, "items[0].name", error)
        assert nested == {"items": [{"name": error}]}

    def test_type_error_on_non_list_index_access(self):
        """Test TypeError when trying to access index on non-list."""
        nested = {"items": "not-a-list"}
        with pytest.raises(
            TypeError, match="Expected list but got.*at index access"
        ):
            _set_nested_value(nested, "items[0]", "value")

    def test_extend_existing_structure(self):
        """Test extending existing nested structure."""
        regex_error = TOMLError(REGEX_MISMATCH)
        nested = {"user": {"name": "existing"}}
        _set_nested_value(nested, "user.email", regex_error)
        assert nested == {"user": {"name": "existing", "email": regex_error}}

    def test_create_sparse_array(self):
        """Test creating sparse array with gaps."""
        nested = {}
        error = TOMLError(INVALID_TYPE)
        _set_nested_value(nested, "items[5].name", error)
        expected = {"items": [None, None, None, None, None, {"name": error}]}
        assert nested == expected

    def test_mixed_operations(self):
        """Test multiple operations on same structure."""
        nested = {}
        invalid_type_error = TOMLError(INVALID_TYPE)
        missing_key_error = TOMLError(MISSING_KEY)
        invalid_array_error = TOMLError(INVALID_ARRAY_ELEMENT)

        _set_nested_value(nested, "config.debug", invalid_type_error)
        _set_nested_value(nested, "config.servers[0].host", missing_key_error)
        _set_nested_value(nested, "config.servers[1]", invalid_array_error)

        expected = {
            "config": {
                "debug": invalid_type_error,
                "servers": [{"host": missing_key_error}, invalid_array_error],
            }
        }
        assert nested == expected


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_overwrite_existing_values(self):
        """Test that existing values get overwritten."""
        flat_errors = {
            "user.name": TOMLError(
                VALIDATION_FAILURE
            ),  # This will be the final value
        }
        result = to_dict(flat_errors)
        assert result == {"user": {"name": TOMLError(VALIDATION_FAILURE)}}

    def test_numeric_string_keys(self):
        """Test with numeric string keys that aren't array indices."""
        flat_errors = {
            "config.123": TOMLError(INVALID_TYPE),
            "data.456.value": TOMLError(MISSING_KEY),
        }
        expected = {
            "config": {"123": TOMLError(INVALID_TYPE)},
            "data": {"456": {"value": TOMLError(MISSING_KEY)}},
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_special_characters_in_keys(self):
        """Test with special characters in keys."""
        flat_errors = {
            "config.api-key": TOMLError(INVALID_TYPE),
            "data.field_name": TOMLError(MISSING_KEY),
            "settings.max@size": TOMLError(VALIDATION_FAILURE),
        }
        expected = {
            "config": {"api-key": TOMLError(INVALID_TYPE)},
            "data": {"field_name": TOMLError(MISSING_KEY)},
            "settings": {"max@size": TOMLError(VALIDATION_FAILURE)},
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_large_array_indices(self):
        """Test with large array indices."""
        flat_errors = {"items[100].name": TOMLError(INVALID_TYPE)}
        result = to_dict(flat_errors)
        assert len(result["items"]) == 101
        assert result["items"][100] == {"name": TOMLError(INVALID_TYPE)}
        assert all(item is None for item in result["items"][:100])

    def test_zero_index(self):
        """Test with zero index."""
        flat_errors = {"items[0].name": TOMLError(INVALID_TYPE)}
        expected = {"items": [{"name": TOMLError(INVALID_TYPE)}]}
        result = to_dict(flat_errors)
        assert result == expected

    def test_toml_error_equality(self):
        """Test that TOMLError instances with same error codes are equal."""
        error1 = TOMLError(INVALID_TYPE)
        error2 = TOMLError(INVALID_TYPE)

        flat_errors = {"key": error1}
        result = to_dict(flat_errors)

        # Test that the error in the result is equivalent
        assert result["key"].code == error2.code
        assert str(result["key"]) == str(error2)

    def test_different_error_codes(self):
        """Test with different error codes to ensure they're preserved."""
        flat_errors = {
            "field1": TOMLError(INVALID_TYPE),
            "field2": TOMLError(MISSING_KEY),
            "field3": TOMLError(REGEX_MISMATCH),
            "field4": TOMLError(VALIDATION_FAILURE),
            "field5": TOMLError(INVALID_ARRAY_ELEMENT),
        }

        result = to_dict(flat_errors)

        assert result["field1"].code == INVALID_TYPE
        assert result["field2"].code == MISSING_KEY
        assert result["field3"].code == REGEX_MISMATCH
        assert result["field4"].code == VALIDATION_FAILURE
        assert result["field5"].code == INVALID_ARRAY_ELEMENT
