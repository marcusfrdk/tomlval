"""Module for defining the TOMLSchemaValidationError class."""


class TOMLSchemaValidationError(Exception):
    """Exception raised for schema validation errors in TOML values."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
