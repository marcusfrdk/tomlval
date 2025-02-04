""" TOMLHandlerError module. """


class TOMLHandlerError(Exception):
    """Exception raised when a TOML handler is invalid."""

    def __init__(self, message: str):
        """
        Initialize the TOMLHandlerError.

        Args:
            message: str - The error message.
        Returns:
            None
        Raises:
            None
        """
        super().__init__(message)
        self.explanation = (
            "A TOML handler must be a callable object that accepts "
            "either no arguments, a single key, a single value, or "
            "both a key and a value."
        )
