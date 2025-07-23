"""Module for defining the TOMLKeyValidationError class."""


class TOMLKeyValidationError(Exception):
    """Exception raised for key validation errors in TOML values."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
