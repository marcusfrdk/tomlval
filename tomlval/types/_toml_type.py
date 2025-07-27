"""Base abstract class for all TOML types."""

from typing import Any, Optional

from tomlval.types._toml_error import TOMLError


class TOMLType:
    """Base class for all TOML types."""

    def __str__(self) -> str:
        """Return a string representation of the TOML type."""
        raise NotImplementedError("Subclasses must implement this method.")

    def __repr__(self) -> str:
        """Return a detailed string representation of the TOML type."""
        raise NotImplementedError("Subclasses must implement this method.")

    def validate(self, value: Any) -> Optional[TOMLError]:
        """
        Validate the given value against this TOML type.

        Args:
            value: The value to validate.

        Returns:
            Optional[TOMLError]: An error if validation fails, None otherwise.
        """
