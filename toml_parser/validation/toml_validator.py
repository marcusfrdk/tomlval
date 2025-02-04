""" Validator class for validating TOML data. """

from toml_parser.errors import TOMLHandlerError
from toml_parser.types import Handler


class TOMLValidator:
    """Class to validate TOML data."""

    def __init__(self, data: dict, schema: dict):
        """
        Initialize the TOML validator.

        Args:
            data: dict - The TOML data to validate.
            schema: dict - The TOML schema to validate against.
        Returns:
            None
        Raises:
            TypeError - If data or schema is not a dictionary.
        """

        if not isinstance(data, dict) or not isinstance(schema, dict):
            raise TypeError("Data and schema must be dictionaries.")

        self._data = data
        self._schema = schema
        self._handlers = {}

    def add_handler(self, key: str, handler: Handler):
        """
        Adds a new handler for a specific (e.g. 'my', 'my.key') or global key
        (e.g. '*', 'my.*', 'my.*.key').

        Complex expressions including brackets, such as 'my.[a-z]'
        are currently not supported.

        A handler is a function that can be one of 'fn()',
        'fn(key)', 'fn(value)' or 'fn(key, value)'.

        Args:
            key: str - The key to add the handler to.
            handler: Handler - The handler to add.
        Returns:
            None
        Raises:
            TypeError - If key is not a string.
            toml_parser.errors.TOMLHandlerError - If the handler is invalid.
        """

        if not isinstance(handler, Handler):
            raise TOMLHandlerError("Handler must be a callable.")
