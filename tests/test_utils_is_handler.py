""" Tests for the 'toml_parser.utils.is_toml' module. """

from tomlval.utils.is_handler import is_handler


def test_valid_named_handlers():
    """Test if the 'is_handler' function correctly identifies valid handlers."""

    def named_handler_empty():
        """Empty named handler."""

    def named_handler_key(key):
        """Named handler with 'key'."""

    def named_handler_value(value):
        """Named handler with 'value'."""

    def named_handler_key_value(key, value):
        """Named handler with 'key' and 'value'."""

    def named_handler_key_value_inverse(key, value):
        """Named handler with 'key' and 'value' mixed."""

    assert is_handler(named_handler_empty) == ""
    assert is_handler(named_handler_key) == ""
    assert is_handler(named_handler_value) == ""
    assert is_handler(named_handler_key_value) == ""
    assert is_handler(named_handler_key_value_inverse) == ""


def test_invalid_named_handlers():
    """Test is the 'is_handler' function correctly identifies invalid handlers."""

    def named_handler_invalid_key(key1):
        """Named handler with invalid key."""

    def named_handler_invalid_keys(key1, key2):
        """Named handler with invalid keys."""

    assert (
        is_handler(named_handler_invalid_key)
        == "Function has an invalid parameter 'key1'."
    )
    assert (
        is_handler(named_handler_invalid_keys)
        == "Function has invalid parameters 'key1', 'key2'."
    )


def test_type_handlers():
    """Test various built-in types as handlers."""
    types = [int, float, str, bool, list, tuple, dict, set]
    for t in types:
        assert is_handler(t) == ""


def test_valid_lambda_handlers():
    """
    Test if the 'is_handler' function
    correctly identifies valid lambda handlers.
    """
    assert is_handler(lambda: None) == ""
    assert is_handler(lambda key: None) == ""
    assert is_handler(lambda key, value: None) == ""
    assert is_handler(lambda value, key: None) == ""


def test_invalid_lambda_handlers():
    """
    Test if the 'is_handler' function correctly
    identifies invalid lambda handlers.
    """
    assert (
        is_handler(lambda key1: None)
        == "Function has an invalid parameter 'key1'."
    )
    assert is_handler(lambda key1, key2: None) == (
        "Function has invalid parameters 'key1', 'key2'."
    )
