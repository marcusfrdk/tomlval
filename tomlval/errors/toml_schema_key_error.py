""" Error for invalid TOML schema keys. """


class TOMLSchemaKeyError(Exception):
    """Error for invalid TOML schema keys."""

    def __init__(self, key: str):
        """
        Initialize the TOMLSchemaKeyError.

        Args:
            key: str - The invalid key.
        Returns:
            None
        Raises:
            None
        """
        message = f"Invalid key '{key}' in schema."
        super().__init__(message)
