"""Optional type for TOML values."""

from typing import Any

from tomlval.types._toml_type import TOMLType


class Optional(TOMLType):
    """Represents an optional value."""

    def __init__(self, value: Any) -> None:
        """
        Initialize the Optional type.

        Args:
            value: The type or validator for the optional value
        """
        self.value = value

    def __str__(self) -> str:
        return f"<Optional {self.value.__class__.__name__}>"

    def __repr__(self) -> str:
        return str(self)
