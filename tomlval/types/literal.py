"""Literal type for TOML values."""

from typing import List, Union


class Literal:
    """Represents a literal value in a TOML schema."""

    def __init__(self, value_type: Union[str, List[str]]) -> None:
        """
        Initialize the Literal type.

        Args:
            value_type: The type or validator for the literal value
        """
        self.value_type = value_type

    def __str__(self) -> str:
        if isinstance(self.value_type, list):
            values = " | ".join([f"'{v}'" for v in self.value_type])
            return f"<Literal {values}>"

        return f"<Literal '{self.value_type}'>"

    def __repr__(self) -> str:
        return str(self)
