""" Custom error for invalid schemas. """


class TOMLSchemaError(Exception):
    """Custom error for invalid schemas."""

    def __init__(self, message: str = "Invalid TOML schema."):
        """
        Initialize the TOMLSchemaError.

        Args:
            message: str - The error message.
        Returns:
            None
        Raises:
            None
        """
        super().__init__(message)
