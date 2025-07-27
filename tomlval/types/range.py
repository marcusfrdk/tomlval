"""Represents a range of values in TOML."""

from typing import Optional

from tomlval.errors.error_code import ErrorCode
from tomlval.types._number import Number, is_number
from tomlval.types._toml_error import TOMLError
from tomlval.types._toml_type import TOMLType

MIN_RANGE_TYPE_MESSAGE = "Minimum range must be a real number."
MIN_RANGE_NON_NEGATIVE_MESSAGE = "Minimum range must be non-negative."

MAX_RANGE_TYPE_MESSAGE = "Maximum range must be a real number."
MAX_RANGE_NON_NEGATIVE_MESSAGE = "Maximum range must be non-negative."
MAX_RANGE_MINIMUM_MESSAGE = (
    "Maximum range must be greater than "
    "or equal to minimum range."
)


class Range(TOMLType):
    """Represents a range of values."""

    def __init__(
        self,
        min_range: Optional[Number] = None,
        max_range: Optional[Number] = None,
    ) -> None:
        """
        Initialize the Range type.

        Args:
            min_range (Optional[Number]):
                The minimum value of the range (inclusive).
            max_range (Optional[Number]):
                The maximum value of the range (inclusive).
        """

        if min_range is not None:
            if not is_number(min_range):
                raise TypeError(MIN_RANGE_TYPE_MESSAGE)
            if min_range < 0:
                raise ValueError(MIN_RANGE_NON_NEGATIVE_MESSAGE)

        if max_range is not None:
            if not is_number(max_range):
                raise TypeError(MAX_RANGE_TYPE_MESSAGE)
            if max_range < 0:
                raise ValueError(MAX_RANGE_NON_NEGATIVE_MESSAGE)
            if min_range is not None and max_range < min_range:
                raise ValueError(MAX_RANGE_MINIMUM_MESSAGE)

        self.min_range = min_range
        self.max_range = max_range

    def __str__(self) -> str:
        if self.min_range is not None and self.max_range is not None:
            return f"<Range [{self.min_range}, {self.max_range}]>"

        if self.min_range is not None:
            return f"<Range (-inf, {self.max_range}])>"

        return f"<Range [{self.max_range}, inf)>"

    def __repr__(self) -> str:
        return str(self)

    def validate(self, value: Number) -> Optional[TOMLError]:
        if self.min_range is not None and value < self.min_range:
            return TOMLError(ErrorCode.TOO_SMALL)
        if self.max_range is not None and value > self.max_range:
            return TOMLError(ErrorCode.TOO_LARGE)
        return None
