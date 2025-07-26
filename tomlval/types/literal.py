"""Literal type for TOML values."""

from typing import Optional

from tomlval.toml_error import TOMLError
from tomlval.toml_error_code import TOMLErrorCode
from tomlval.types.toml_type import TOMLType


class Literal(TOMLType):
    """Represents a literal value in a TOML schema."""

    def __init__(self, *values: str) -> None:
        """
        Initialize the Literal type.

        Args:
            value_type: The type or validator for the literal value
        """
        self.value_type = values[0] if len(values) == 1 else list(values)

    def __str__(self) -> str:
        if isinstance(self.value_type, list):
            values = " | ".join([f"'{v}'" for v in self.value_type])
            return f"<Literal {values}>"

        return f"<Literal '{self.value_type}'>"

    def __repr__(self) -> str:
        return str(self)

    def validate(self, value: str) -> Optional[TOMLError]:
        if isinstance(self.value_type, list):
            if value not in self.value_type:
                return TOMLError(TOMLErrorCode.INVALID_LITERAL_VALUE)

        elif value != self.value_type:
            return TOMLError(TOMLErrorCode.INVALID_LITERAL_VALUE)

        return None
