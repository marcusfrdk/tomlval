"""Range type for TOML values."""

from typing import Optional, Union

from tomlval.toml_error import TOMLError
from tomlval.toml_error_code import TOMLErrorCode
from tomlval.types.toml_type import TOMLType


class Range(TOMLType):
    """Represents a range of values in a TOML schema."""

    def __init__(
        self,
        min_range: Optional[Union[int, float]] = None,
        max_range: Optional[Union[int, float]] = None,
    ) -> None:
        """
        Initialize the Range type.

        Args:
            min_range (Optional[Union[int, float]]): The minimum
                value of the range (inclusive)
            max_range (Optional[Union[int, float]]): The maximum
                value of the range (inclusive)
        """
        if min_range is None and max_range is None:
            raise ValueError(
                "At least one of min_range or max_range must be specified."
            )

        self.min_range = min_range
        self.max_range = max_range

    def __str__(self) -> str:
        if self.min_range is not None and self.max_range is not None:
            return f"<Range {self.min_range} to {self.max_range}>"

        if self.min_range is not None:
            return f"<Range >= {self.min_range}>"

        return f"<Range <= {self.max_range}>"

    def __repr__(self) -> str:
        return str(self)

    def validate(self, value: Union[int, float]) -> Optional[TOMLError]:
        if self.min_range is not None and value < self.min_range:
            return TOMLError(TOMLErrorCode.TOO_SMALL)
        if self.max_range is not None and value > self.max_range:
            return TOMLError(TOMLErrorCode.TOO_LARGE)
        return None
