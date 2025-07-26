"""Length type for TOML values."""

from typing import Optional

from tomlval.toml_error import TOMLError
from tomlval.toml_error_code import TOMLErrorCode
from tomlval.types.toml_type import TOMLType


class Length(TOMLType):
    """Represents a length constraint for TOML values."""

    def __init__(
        self, min_length: Optional[int] = None, max_length: Optional[int] = None
    ) -> None:
        """
        Initialize the Length type.

        Args:
            min_length (int): The minimum length of the value (inclusive).
            max_length (int): The maximum length of the value (inclusive).
        Raises:
            ValueError: If both min_length and max_length are None, or if
                min_length is greater than max_length, or if either
                min_length or max_length is negative.
        """
        if min_length is not None and min_length < 0:
            raise ValueError("Minimum length must be non-negative.")
        if max_length is not None and max_length < 0:
            raise ValueError("Length constraints must be non-negative.")
        if (
            min_length is not None
            and max_length is not None
            and min_length > max_length
        ):
            raise ValueError(
                "Minimum length cannot be greater than maximum length."
            )

        self.min_length = min_length
        self.max_length = max_length

    def __str__(self) -> str:
        if self.min_length is not None and self.max_length is not None:
            return f"<Length {self.min_length} to {self.max_length}>"

        if self.min_length is not None:
            return f"<Length >= {self.min_length}>"

        return f"<Length <= {self.max_length}>"

    def __repr__(self) -> str:
        return str(self)

    def validate(self, value: str) -> Optional[TOMLError]:
        if self.min_length is not None and len(value) < self.min_length:
            return TOMLError(TOMLErrorCode.TOO_SHORT)

        if self.max_length is not None and len(value) > self.max_length:
            return TOMLError(TOMLErrorCode.TOO_LONG)

        return None
