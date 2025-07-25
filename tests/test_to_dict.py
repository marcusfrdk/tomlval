"""Tests for the to_dict utility function."""

import pytest

from tomlval.errors.error_codes import (
    INVALID_ARRAY_ELEMENT,
    INVALID_TYPE,
    MISSING_KEY,
    REGEX_MISMATCH,
    VALIDATION_FAILURE,
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
            "name": INVALID_TYPE,
            "age": MISSING_KEY,
            "active": VALIDATION_FAILURE,
        }
        expected = {
            "name": INVALID_TYPE,
            "age": MISSING_KEY,
            "active": VALIDATION_FAILURE,
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_nested_keys(self):
        """Test with dot notation nested keys."""
        flat_errors = {
            "user.name": INVALID_TYPE,
            "user.email": REGEX_MISMATCH,
            "config.debug": INVALID_TYPE,
        }
        expected = {
            "user": {"name": INVALID_TYPE, "email": REGEX_MISMATCH},
            "config": {"debug": INVALID_TYPE},
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_deep_nesting(self):
        """Test with deeply nested keys."""
        flat_errors = {
            "app.database.connection.host": MISSING_KEY,
            "app.database.connection.port": INVALID_TYPE,
            "app.cache.redis.timeout": VALIDATION_FAILURE,
        }
        expected = {
            "app": {
                "database": {
                    "connection": {
                        "host": MISSING_KEY,
                        "port": INVALID_TYPE,
                    }
                },
                "cache": {"redis": {"timeout": VALIDATION_FAILURE}},
            }
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_array_indices(self):
        """Test with array index notation."""
        flat_errors = {
            "items[0].name": INVALID_TYPE,
            "items[0].price": MISSING_KEY,
            "items[2].category": VALIDATION_FAILURE,
        }
        expected = {
            "items": [
                {"name": INVALID_TYPE, "price": MISSING_KEY},
                None,
                {"category": VALIDATION_FAILURE},
            ]
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_array_element_errors(self):
        """Test with errors on array elements themselves."""
        flat_errors = {
            "tasks[0]": INVALID_ARRAY_ELEMENT,
            "tasks[2]": INVALID_TYPE,
            "data[1].value": MISSING_KEY,
        }
        expected = {
            "tasks": [INVALID_ARRAY_ELEMENT, None, INVALID_TYPE],
            "data": [None, {"value": MISSING_KEY}],
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_mixed_structure(self):
        """Test with mixed dictionary and array structures."""
        flat_errors = {
            "config.servers[0].host": INVALID_TYPE,
            "config.servers[0].port": VALIDATION_FAILURE,
            "config.servers[1].ssl.enabled": MISSING_KEY,
            "config.debug": INVALID_TYPE,
            "users[0].permissions[1]": INVALID_ARRAY_ELEMENT,
        }
        expected = {
            "config": {
                "servers": [
                    {"host": INVALID_TYPE, "port": VALIDATION_FAILURE},
                    {"ssl": {"enabled": MISSING_KEY}},
                ],
                "debug": INVALID_TYPE,
            },
            "users": [{"permissions": [None, INVALID_ARRAY_ELEMENT]}],
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_sparse_arrays(self):
        """Test with sparse array indices."""
        flat_errors = {
            "items[5].name": INVALID_TYPE,
            "items[10]": INVALID_ARRAY_ELEMENT,
        }
        expected = {
            "items": [
                None,
                None,
                None,
                None,
                None,
                {"name": INVALID_TYPE},
                None,
                None,
                None,
                None,
                INVALID_ARRAY_ELEMENT,
            ]
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_complex_real_world_example(self):
        """Test with a complex real-world example."""
        flat_errors = {
            "startup_tasks[1].args": INVALID_TYPE,
            "startup_tasks[1].timeout": INVALID_TYPE,
            "database.connection.pool_size": VALIDATION_FAILURE,
            "api.cors.allowed_origins[0]": REGEX_MISMATCH,
            "plugins.analytics.config.tracking_id": MISSING_KEY,
            "scheduled_tasks[0].enabled": INVALID_TYPE,
        }
        expected = {
            "startup_tasks": [
                None,
                {"args": INVALID_TYPE, "timeout": INVALID_TYPE},
            ],
            "database": {"connection": {"pool_size": VALIDATION_FAILURE}},
            "api": {"cors": {"allowed_origins": [REGEX_MISMATCH]}},
            "plugins": {"analytics": {"config": {"tracking_id": MISSING_KEY}}},
            "scheduled_tasks": [{"enabled": INVALID_TYPE}],
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
        _set_nested_value(nested, "name", INVALID_TYPE)
        assert nested == {"name": INVALID_TYPE}

    def test_set_nested_key(self):
        """Test setting a nested key value."""
        nested = {}
        _set_nested_value(nested, "user.name", INVALID_TYPE)
        assert nested == {"user": {"name": INVALID_TYPE}}

    def test_set_array_element(self):
        """Test setting an array element."""
        nested = {}
        _set_nested_value(nested, "items[0]", INVALID_ARRAY_ELEMENT)
        assert nested == {"items": [INVALID_ARRAY_ELEMENT]}

    def test_set_nested_array_element(self):
        """Test setting a nested array element property."""
        nested = {}
        _set_nested_value(nested, "items[0].name", INVALID_TYPE)
        assert nested == {"items": [{"name": INVALID_TYPE}]}

    def test_type_error_on_non_list_index_access(self):
        """Test TypeError when trying to access index on non-list."""
        nested = {"items": "not-a-list"}
        with pytest.raises(
            TypeError, match="Expected list but got.*at index access"
        ):
            _set_nested_value(nested, "items[0]", "value")

    def test_extend_existing_structure(self):
        """Test extending existing nested structure."""
        nested = {"user": {"name": "existing"}}
        _set_nested_value(nested, "user.email", REGEX_MISMATCH)
        assert nested == {"user": {"name": "existing", "email": REGEX_MISMATCH}}

    def test_create_sparse_array(self):
        """Test creating sparse array with gaps."""
        nested = {}
        _set_nested_value(nested, "items[5].name", INVALID_TYPE)
        expected = {
            "items": [None, None, None, None, None, {"name": INVALID_TYPE}]
        }
        assert nested == expected

    def test_mixed_operations(self):
        """Test multiple operations on same structure."""
        nested = {}
        _set_nested_value(nested, "config.debug", INVALID_TYPE)
        _set_nested_value(nested, "config.servers[0].host", MISSING_KEY)
        _set_nested_value(nested, "config.servers[1]", INVALID_ARRAY_ELEMENT)

        expected = {
            "config": {
                "debug": INVALID_TYPE,
                "servers": [{"host": MISSING_KEY}, INVALID_ARRAY_ELEMENT],
            }
        }
        assert nested == expected


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_overwrite_existing_values(self):
        """Test that existing values get overwritten."""
        flat_errors = {  # pylint: disable=duplicate-key
            "user.name": INVALID_TYPE,
            "user.name": VALIDATION_FAILURE,
        }
        result = to_dict(flat_errors)
        assert result == {"user": {"name": VALIDATION_FAILURE}}

    def test_numeric_string_keys(self):
        """Test with numeric string keys that aren't array indices."""
        flat_errors = {
            "config.123": INVALID_TYPE,
            "data.456.value": MISSING_KEY,
        }
        expected = {
            "config": {"123": INVALID_TYPE},
            "data": {"456": {"value": MISSING_KEY}},
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_special_characters_in_keys(self):
        """Test with special characters in keys."""
        flat_errors = {
            "config.api-key": INVALID_TYPE,
            "data.field_name": MISSING_KEY,
            "settings.max@size": VALIDATION_FAILURE,
        }
        expected = {
            "config": {"api-key": INVALID_TYPE},
            "data": {"field_name": MISSING_KEY},
            "settings": {"max@size": VALIDATION_FAILURE},
        }
        result = to_dict(flat_errors)
        assert result == expected

    def test_large_array_indices(self):
        """Test with large array indices."""
        flat_errors = {"items[100].name": INVALID_TYPE}
        result = to_dict(flat_errors)
        assert len(result["items"]) == 101
        assert result["items"][100] == {"name": INVALID_TYPE}
        assert all(item is None for item in result["items"][:100])

    def test_zero_index(self):
        """Test with zero index."""
        flat_errors = {"items[0].name": INVALID_TYPE}
        expected = {"items": [{"name": INVALID_TYPE}]}
        result = to_dict(flat_errors)
        assert result == expected
