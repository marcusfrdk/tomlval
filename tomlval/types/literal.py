"""Literal type for TOML values."""


class Literal:
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
