"""Length type representing a string with length constraints."""

from typing import Optional

from tomlval.errors.error_code import ErrorCode
from tomlval.types._toml_error import TOMLError
from tomlval.types._toml_type import TOMLType

MIN_LENGTH_TYPE_MESSAGE = "Minimum length must be an integer."
MIN_LENGTH_NON_NEGATIVE_MESSAGE = "Minimum length must be non-negative."
MIN_LENGTH_GT_MESSAGE = (
    "Minimum length must be less than or equal to maximum length."
)

MAX_LENGTH_TYPE_MESSAGE = "Maximum length must be an integer."
MAX_LENGTH_NON_NEGATIVE_MESSAGE = "Maximum length must be non-negative."
MAX_LENGTH_LT_MESSAGE = (
    "Maximum length must be greater than or equal to minimum length."
)

EXACTLY_TYPE_MESSAGE = "Exactly length must be an integer."
EXACTLY_NON_NEGATIVE_MESSAGE = "Exactly length must be non-negative."
EXACTLY_EXCLUSIVE_MESSAGE = (
    "Cannot specify 'exactly' with 'min_length' or 'max_length'."
)


class Length(TOMLType):
    """Represents a string with length constraints."""

    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        exactly: Optional[int] = None,
    ) -> None:
        """
        Initialize the Length type.

        Args:
            min_length (Optional[int]):
                The minimum length of the value (inclusive).
            max_length (Optional[int]):
                The maximum length of the value (inclusive).
            exactly (Optional[int]):
                The exact length of the value (must be equal to this length).
                Mutually exclusive with min_length and max_length.
        Raises:
            TypeError: If any parameter is not an integer when provided.
            ValueError: If any parameter is negative, if min_length >
                max_length, or if exactly is used with min_length or max_length.
        """
        if exactly is not None and (
            min_length is not None or max_length is not None
        ):
            raise ValueError(EXACTLY_EXCLUSIVE_MESSAGE)

        if exactly is not None:
            if not isinstance(exactly, int):
                raise TypeError(EXACTLY_TYPE_MESSAGE)

            if exactly < 0:
                raise ValueError(EXACTLY_NON_NEGATIVE_MESSAGE)

            self.min_length = None
            self.max_length = None
            self.exactly = exactly
            return

        if min_length is not None:
            if not isinstance(min_length, int):
                raise TypeError(MIN_LENGTH_TYPE_MESSAGE)

            if min_length < 0:
                raise ValueError(MIN_LENGTH_NON_NEGATIVE_MESSAGE)

            if max_length is not None and max_length < min_length:
                raise ValueError(MIN_LENGTH_GT_MESSAGE)

        if max_length is not None:
            if not isinstance(max_length, int):
                raise TypeError(MAX_LENGTH_TYPE_MESSAGE)

            if max_length < 0:
                raise ValueError(MAX_LENGTH_NON_NEGATIVE_MESSAGE)

            if min_length is not None and min_length > max_length:
                raise ValueError(MAX_LENGTH_LT_MESSAGE)

        self.min_length = min_length
        self.max_length = max_length
        self.exactly = None

    def __str__(self) -> str:
        if self.exactly is not None:
            return f"<Length {self.exactly}>"

        if self.min_length is not None and self.max_length is not None:
            return f"<Length [{self.min_length}, {self.max_length}]>"

        if self.min_length is not None:
            return f"<Length [{self.min_length}, inf)>"

        return f"<Length [0, {self.max_length}]>"

    def __repr__(self) -> str:
        return str(self)

    def validate(self, value: str):
        if not isinstance(value, str):
            return TOMLError(ErrorCode.INVALID_TYPE)

        if self.exactly is not None:
            if len(value) != self.exactly:
                return TOMLError(ErrorCode.INVALID_LENGTH)
            return None

        if self.min_length is not None and len(value) < self.min_length:
            return TOMLError(ErrorCode.TOO_SHORT)

        if self.max_length is not None and len(value) > self.max_length:
            return TOMLError(ErrorCode.TOO_LONG)

        return None
