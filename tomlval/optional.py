"""Optional type for TOML values."""

from typing import Any


class Optional:
    """Represents an optional value in a TOML schema."""

    def __init__(self, value_type: Any, default: Any = None) -> None:
        """
        Initialize the Optional type.

        Args:
            value_type: The type or validator for the optional value
            default: Default value if the key is missing
        """
        self.value_type = value_type
        self.default = default

    def __repr__(self) -> str:
        if self.default is not None:
            return f"<Optional {self.value_type} default={self.default}>"
        return f"<Optional {self.value_type}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Optional):
            return False
        return (
            self.value_type == other.value_type
            and self.default == other.default
        )
