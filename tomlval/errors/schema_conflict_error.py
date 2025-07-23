"""Module for defining the TOMLSchemaConflictError class."""


class TOMLSchemaConflictError(Exception):
    """Exception raised for schema conflict errors in TOML values."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
