"""Initialization file for the tomlval package."""

from tomlval.toml_schema import TOMLSchema
from tomlval.utils.validate_data import validate_data

__all__ = [
    "TOMLSchema",
    "validate_data",
]
