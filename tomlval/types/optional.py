"""Optional type for TOML values."""

from typing import Any

from tomlval.types.toml_type import TOMLType


class Optional(TOMLType):
    """Represents an optional value in a TOML schema."""

    def __init__(self, value_type: Any) -> None:
        """
        Initialize the Optional type.

        Args:
            value_type: The type or validator for the optional value
        """
        self.value_type = value_type

    def __str__(self) -> str:
        return f"<Optional {self.value_type.__class__.__name__}>"

    def __repr__(self) -> str:
        return str(self)
