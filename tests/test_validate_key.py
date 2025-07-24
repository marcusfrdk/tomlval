"""Tests for the validate_key module."""

import pytest

from tomlval.errors import TOMLKeyValidationError
from tomlval.utils.validate_key import validate_key


class TestValidateKey:
    """Test cases for the validate_key function."""

    def test_valid_bare_keys(self):
        """Test valid bare keys."""
        valid_keys = [
            "key",
            "key123",
            "key_name",
            "key-name",
            "user_id",
            "app-config",
            "a",
            "A",
            "123",
            "_",
            "-",
        ]

        for key in valid_keys:
            validate_key(key)

    def test_valid_quoted_keys(self):
        """Test valid quoted keys."""
        valid_keys = [
            '"key"',
            "'key'",
            '"key with spaces"',
            '"key*with*stars"',
            '"127.0.0.1"',
            '"character encoding"',
            '"ʎǝʞ"',
            '""',  # Empty quoted key
            "''",  # Empty quoted key
            '"key.with.dots"',  # Single quoted key with dots
            "'key.with.dots'",  # Single quoted key with dots
            '"key[with]brackets"',  # Single quoted key with brackets
        ]

        for key in valid_keys:
            validate_key(key)

    def test_valid_dotted_keys(self):
        """Test valid dotted keys."""
        valid_keys = [
            "user.name",
            "app.database.host",
            "a.b.c.d.e",
            '"user"."name"',
            "user.'name with spaces'",
        ]

        for key in valid_keys:
            validate_key(key)

    def test_valid_array_notation_keys(self):
        """Test valid array notation keys."""
        valid_keys = [
            "users[0]",
            "data[123]",
            "items[0].name",
            "config[0].database[1]",
            "nested[0].array[1].value",
        ]

        for key in valid_keys:
            validate_key(key)

    def test_valid_wildcard_keys(self):
        """Test valid wildcard keys."""
        valid_keys = [
            "user*",
            "*name",
            "app*config",
            "data*.value",
            "users*.name*",
            "config*123",
            "test_*_value",
        ]

        for key in valid_keys:
            validate_key(key)

    def test_invalid_non_string_keys(self):
        """Test that non-string keys raise TOMLKeyValidationError."""
        invalid_keys = [None, 123, [], {}, True, 3.14]

        for key in invalid_keys:
            with pytest.raises(
                TOMLKeyValidationError, match="Key must be a string"
            ):
                validate_key(key)

    def test_empty_key(self):
        """Test that empty key raises TOMLKeyValidationError."""
        with pytest.raises(TOMLKeyValidationError, match="Key cannot be empty"):
            validate_key("")

    def test_empty_dotted_segments_in_bare_keys(self):
        """
        Test that empty segments in dot notation raise errors for bare keys.
        """
        invalid_keys = [
            "user..name",  # Double dots create empty segment
            "a..b.c",  # Double dots create empty segment
            "...key",  # Multiple leading dots create empty segments
        ]

        for key in invalid_keys:
            with pytest.raises(TOMLKeyValidationError, match="empty segment"):
                validate_key(key)

    def test_dotted_keys_with_leading_trailing_dots(self):
        """Test dotted keys with leading/trailing dots."""
        valid_quoted_keys = [
            '".user"',  # Quoted key starting with dot
            '"user."',  # Quoted key ending with dot
        ]

        for key in valid_quoted_keys:
            validate_key(key)

        invalid_bare_keys = [
            ".user",  # Leading dot creates empty first segment
            "user.",  # Trailing dot creates empty last segment
        ]

        for key in invalid_bare_keys:
            with pytest.raises(TOMLKeyValidationError, match="empty segment"):
                validate_key(key)

    def test_invalid_bare_keys(self):
        """Test invalid bare keys."""
        invalid_keys = [
            "key with spaces",
            "key@symbol",
            "key#hash",
            "key$dollar",
            "key%percent",
            "key&ampersand",
            "key(parenthesis",
            "key)parenthesis",
            "key+plus",
            "key=equals",
            "key{brace",
            "key}brace",
            "key|pipe",
            "key\\backslash",
            "key:colon",
            "key;semicolon",
            "key<less",
            "key>greater",
            "key?question",
            "key/slash",
            "key,comma",
        ]

        for key in invalid_keys:
            with pytest.raises(TOMLKeyValidationError):
                validate_key(key)

    def test_invalid_quoted_keys(self):
        """Test invalid quoted keys."""
        invalid_keys = [
            '"',  # Single quote
            "'",  # Single quote
            '"key',  # Missing closing quote
            "key'",  # Missing opening quote
            "\"key'",  # Mismatched quotes
            "'key\"",  # Mismatched quotes
        ]

        for key in invalid_keys:
            with pytest.raises(TOMLKeyValidationError):
                validate_key(key)

    def test_invalid_array_notation(self):
        """Test invalid array notation."""
        invalid_keys = [
            "key[",  # Missing closing bracket
            "key]",  # Missing opening bracket
            "key[]",  # Empty brackets
            "key[abc]",  # Non-numeric index
            "key[-1]",  # Negative index
            "key[1.5]",  # Float index
            "key[ 1 ]",  # Spaces in index
            "key[1][2",  # Malformed nested
        ]

        for key in invalid_keys:
            with pytest.raises(TOMLKeyValidationError):
                validate_key(key)

    def test_invalid_wildcard_keys(self):
        """Test invalid wildcard keys."""
        invalid_keys = [
            "key*?",  # Invalid characters with wildcard
            "key* space",  # Space with wildcard
        ]

        for key in invalid_keys:
            with pytest.raises(TOMLKeyValidationError):
                validate_key(key)

    def test_complex_valid_keys(self):
        """Test complex but valid key combinations."""
        valid_keys = [
            "app.database.users[0].profile.settings",
            '"complex key".simple.users[123]',
            "config*.database*.host",
            'users[0]."full name".settings',
            "data*_test.values[0]",
        ]

        for key in valid_keys:
            validate_key(key)

    def test_unicode_in_quoted_keys(self):
        """Test unicode characters in quoted keys."""
        valid_keys = [
            '"café"',
            '"测试"',
            '"🔑"',
            '"naïve"',
        ]

        for key in valid_keys:
            validate_key(key)

    def test_escape_sequences_in_quoted_keys(self):
        """Test escape sequences in quoted keys."""
        valid_keys = [
            r'"key\nwith\nnewlines"',
            r'"key\twith\ttabs"',
            r'"key\"with\"quotes"',
            r'"key\\with\\backslashes"',
        ]

        for key in valid_keys:
            validate_key(key)

    def test_control_characters_in_quoted_keys(self):
        """Test that control characters (except tab) are invalid."""
        # Control character (ASCII 1)
        invalid_key = '"key\x01invalid"'
        with pytest.raises(TOMLKeyValidationError):
            validate_key(invalid_key)

    def test_unescaped_quotes_in_basic_strings(self):
        """Test that unescaped quotes in basic strings are invalid."""
        invalid_key = '"key"with"quote"'
        with pytest.raises(TOMLKeyValidationError):
            validate_key(invalid_key)

    def test_quoted_keys_are_valid_single_keys(self):
        """Test that quoted keys with special characters are valid."""
        valid_keys = [
            '"key.with.dots"',
            "'key.with.dots'",
            '"key[with]brackets"',
            '"key*with*stars"',
        ]

        for key in valid_keys:
            validate_key(key)

    def test_dotted_keys_behavior(self):
        """Test actual behavior of dotted keys with special characters."""
        valid_keys = [
            "key.with.dots",
        ]

        for key in valid_keys:
            validate_key(key)

        with pytest.raises(TOMLKeyValidationError):
            validate_key("key[with]brackets")

    def test_wildcard_edge_cases(self):
        """Test wildcard edge cases."""
        validate_key("*")  # Single wildcard is allowed
        validate_key("user.*.name")  # Wildcard in middle is allowed
        validate_key(
            "*.key"
        )  # Leading wildcard targeting shared key is allowed
        validate_key("*.user*")  # Wildcard with trailing segment is allowed

        with pytest.raises(
            TOMLKeyValidationError, match="consecutive wildcard"
        ):
            validate_key("*.*")

    def test_mixed_quoted_and_bare_in_dotted_keys(self):
        """Test mixed quoted and bare keys in dotted notation."""
        valid_keys = [
            'bare."simple quoted"',
            '"simple quoted".bare',
            '"user"."name"',
        ]

        for key in valid_keys:
            validate_key(key)

    def test_array_notation_edge_cases(self):
        """Test edge cases for array notation."""
        # Valid array notation
        valid_keys = [
            "key[0]",
            "users[123]",
        ]

        for key in valid_keys:
            validate_key(key)

        # Invalid array notation
        invalid_keys = [
            "key[]",  # Empty brackets
            "key[abc]",  # Non-numeric
            "key[1.5]",  # Float
        ]

        for key in invalid_keys:
            with pytest.raises(TOMLKeyValidationError):
                validate_key(key)
