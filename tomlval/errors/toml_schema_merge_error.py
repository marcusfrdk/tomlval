""" Custom error for invalid schemas. """

from typing import Any


class TOMLSchemaMergeError(Exception):
    """Exception raised when incompatible types are attempted to be merged."""

    def __init__(self, value1: Any, value2: Any):
        """
        Initialize the TOMLSchemaMergeError.

        Args:
            value1: type - The first value.
            value2: type - The second value.
        Returns:
            None
        Raises:
            None
        """

        def _get_type_name(value):
            if isinstance(value, type):
                return value.__name__
            return type(value).__name__

        message = " ".join(
            [
                "Cannot merge",
                f"{_get_type_name(value1)} with {_get_type_name(value2)}.",
            ]
        )

        super().__init__(message)
