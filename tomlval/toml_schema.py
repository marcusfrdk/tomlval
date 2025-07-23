"""The TOMLSchema module for validating TOML values."""

from typing import Dict

from tomlval.utils.validate_schema import validate_schema


class TOMLSchema:
    """A TOMLSchema class to define and validate a schema for TOML values."""

    def __init__(self, schema: Dict) -> None:
        """
        Initialize the TOMLSchema with a dictionary of expected
        types and constraints.

        Args:
            schema (Dict): A dictionary defining the schema.
        """
        validate_schema(schema)

        self.schema = schema

    def __str__(self) -> str:
        return "<TOMLSchema>"

    def __repr__(self) -> str:
        return "<TOMLSchema>"
