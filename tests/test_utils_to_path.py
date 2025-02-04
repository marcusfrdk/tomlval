""" Tests for the 'toml_parser.utils.to_path' module. """

import pathlib
from unittest.mock import patch

import pytest

from tomlval.utils.to_path import to_path


def test_to_path_with_pathlib_path():
    """Should return the same pathlib.Path object."""
    path = pathlib.Path("/tmp/test")
    assert to_path(path) == path, "Should return the same pathlib.Path object"


@patch("pathlib.Path.resolve", return_value=pathlib.Path("/mocked/path"))
def test_to_path_with_absolute_string(mock_resolve):
    """Should convert absolute string path to pathlib.Path."""
    path_str = "/tmp/test"
    expected = pathlib.Path("/mocked/path")
    assert (
        to_path(path_str) == expected
    ), "Should convert absolute string path to pathlib.Path"


@patch("os.path.abspath", return_value="/mocked/absolute/path")
def test_to_path_with_relative_string(mock_abspath):
    """Should convert relative string path to absolute pathlib.Path."""
    path_str = "./test_dir"
    expected = pathlib.Path("/mocked/absolute/path")
    assert (
        to_path(path_str) == expected
    ), "Should convert relative path to absolute pathlib.Path"


@patch("os.path.expanduser", return_value="/mocked/home/test_file")
@patch(
    "pathlib.Path.resolve", return_value=pathlib.Path("/mocked/home/test_file")
)
def test_to_path_with_user_home(mock_resolve, mock_expanduser):
    """Should correctly expand the user home directory."""
    path_str = "~/test_file"
    expected = pathlib.Path("/mocked/home/test_file")
    assert (
        to_path(path_str) == expected
    ), "Should correctly expand the user home directory"


@patch("os.path.abspath", return_value="/mocked/current/dir")
def test_to_path_with_dot(mock_abspath):
    """Should resolve '.' to the absolute current working directory."""
    path_str = "."
    expected = pathlib.Path("/mocked/current/dir")
    assert (
        to_path(path_str) == expected
    ), "Should resolve '.' to the absolute current working directory"


@patch("os.path.abspath", return_value="/mocked/parent/dir")
def test_to_path_with_double_dots(mock_abspath):
    """Should resolve '..' to the absolute parent directory."""
    path_str = ".."
    expected = pathlib.Path("/mocked/parent/dir")
    assert (
        to_path(path_str) == expected
    ), "Should resolve '..' to the absolute parent directory"


@patch("os.path.abspath", return_value="/mocked/nonexistent/path")
def test_to_path_with_nonexistent_directory(mock_abspath):
    """Should convert nonexistent paths without checking existence."""
    path_str = "/this/path/should/not/exist"
    expected = pathlib.Path("/mocked/nonexistent/path")
    assert (
        to_path(path_str) == expected
    ), "Should convert nonexistent paths without checking existence"


@patch("os.path.abspath", return_value="/mocked/symlink/path")
def test_to_path_with_symlink(mock_abspath):
    """Should resolve symlink paths as normal paths."""
    symlink_path = "/tmp/symlink_test"
    expected = pathlib.Path("/mocked/symlink/path")
    assert (
        to_path(symlink_path) == expected
    ), "Should resolve symlink paths as normal paths"


def test_to_path_with_numeric_input():
    """Should raise a TypeError for invalid input types."""
    with pytest.raises(TypeError):
        to_path(1234)


def test_to_path_with_none_input():
    """Should raise a TypeError for None input."""
    with pytest.raises(TypeError):
        to_path(None)


def test_to_path_with_bytes_input():
    """Should raise a TypeError for byte input."""
    with pytest.raises(TypeError):
        to_path(b"/tmp/test")
