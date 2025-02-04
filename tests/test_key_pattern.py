""" Test cases for the key pattern regex. """

import pathlib

import pytest

from tomlval.utils.regex import key_pattern

# Paths
data_path = pathlib.Path(__file__).parent / "data"
valid_path = data_path / "valid_key.txt"
invalid_path = data_path / "invalid_key.txt"


def load_test_cases(file_path):
    """Load test cases from a file."""
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


# Test cases
valid_cases = load_test_cases(valid_path)
invalid_cases = load_test_cases(invalid_path)


@pytest.mark.parametrize("test_input", valid_cases)
def test_valid_keys(test_input):
    """Test valid keys."""
    assert key_pattern.fullmatch(
        test_input
    ), f"Expected valid but failed: {test_input}"


@pytest.mark.parametrize("test_input", invalid_cases)
def test_invalid_keys(test_input):
    """Test invalid keys."""
    assert not key_pattern.fullmatch(
        test_input
    ), f"Expected invalid but passed: {test_input}"
