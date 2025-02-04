""" Tests for the 'toml_parser.utils.is_toml' module. """

import tomllib
from io import BytesIO

from tomlval.utils.is_toml import is_toml


class DummyPath:
    """Dummy class to simulate a pathlib.Path object."""

    def __init__(self, content: bytes, exists: bool = True):
        self.content = content
        self._exists = exists

    def is_file(self):
        """Simulate the is_file method of a pathlib.Path object."""
        return self._exists

    def open(self, mode: str):
        """Simulate the open method of a pathlib.Path object."""
        return BytesIO(self.content)


def test_valid_toml(monkeypatch):
    """Test that a valid TOML file is correctly identified."""
    valid_toml = b"[section]\nkey = 'value'\n"
    monkeypatch.setitem(
        is_toml.__globals__, "to_path", lambda path: DummyPath(valid_toml)
    )
    result = is_toml("dummy_path")
    assert result is True


def fake_tomllib_load(_file):
    """Fake tomllib.load that raises a TOMLDecodeError."""

    raise tomllib.TOMLDecodeError("Invalid TOML", "", 0)


def test_invalid_toml(monkeypatch):
    """Test that an invalid TOML file is correctly identified."""

    invalid_toml = b"not valid toml"
    monkeypatch.setitem(
        is_toml.__globals__, "to_path", lambda path: DummyPath(invalid_toml)
    )

    monkeypatch.setattr(tomllib, "load", fake_tomllib_load)
    result = is_toml("dummy_path")
    assert result is False


def test_file_not_found(monkeypatch):
    """Test that a non-existent file is correctly identified."""

    monkeypatch.setitem(
        is_toml.__globals__,
        "to_path",
        lambda path: DummyPath(b"", exists=False),
    )
    result = is_toml("non_existent_file")
    assert result is False
