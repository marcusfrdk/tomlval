"""Invalid type for TOML values."""


class Invalid:
    """Represents an invalid/forbidden value in a TOML schema."""

    def __init__(self) -> None:
        """Initialize the Invalid type."""

    def __str__(self) -> str:
        return "<Invalid>"

    def __repr__(self) -> str:
        return str(self)
