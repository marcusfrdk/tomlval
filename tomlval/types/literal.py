"""Literal type for TOML values."""

from typing import Optional

from tomlval.errors.error_code import ErrorCode
from tomlval.types._primitive import Primitive, is_primitive
from tomlval.types._toml_error import TOMLError
from tomlval.types._toml_type import TOMLType
from tomlval.utils import quote_list

VALUE_COUNT_MESSAGE = "At least one value must be provided in Literal."
INVALID_TYPES_MESSAGE = (
    "Invalid value types found in Literal: %s. "
    "Only str, int, float, and bool are allowed."
)


class Literal(TOMLType):
    """Represents a literal value in a TOML schema."""

    def __init__(self, *values: Primitive) -> None:
        """
        Initialize the Literal type.

        Args:
            *values (Primitive): One or more primitive values
                                 that can be validated.
        Raises:
            ValueError: If no values are provided or if the values are not a
                        primitive type (str, int, float, bool).
        """
        if not values:
            raise ValueError(VALUE_COUNT_MESSAGE)

        if invalid_types := [v for v in values if not is_primitive(v)]:
            found_types = ", ".join([type(v).__name__ for v in invalid_types])
            raise ValueError(INVALID_TYPES_MESSAGE % found_types)

        self.value_type = [values[0]] if len(values) == 1 else list(values)

    def __str__(self) -> str:
        return f"<Literal {', '.join(quote_list(self.value_type, True))}>"

    def __repr__(self) -> str:
        return str(self)

    def validate(self, value: Primitive) -> Optional[TOMLError]:
        if isinstance(self.value_type, list):
            if value not in self.value_type:
                return TOMLError(ErrorCode.INVALID_LITERAL_VALUE)

        elif value != self.value_type:
            return TOMLError(ErrorCode.INVALID_LITERAL_VALUE)

        return None
