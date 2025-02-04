""" Validator class for validating TOML data. """

import inspect
import re
from typing import Any, Callable

from toml_parser.errors import TOMLHandlerError
from toml_parser.types import Handler


class TOMLValidator:
    """Class to validate TOML data."""

    def __init__(self, data: dict, schema: dict = None):
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

        # Data
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary.")

        # Schema
        if schema is not None and not isinstance(schema, dict):
            raise TypeError("Schema must be a dictionary.")

        self._data = data
        self._schema = schema
        self._handlers = {}

    def _map_keys(self) -> dict[str, Any]:
        """A method to map keys in dot notation to their values."""

        def _flatten(data: dict, parent_key: str = "") -> dict[str, Any]:
            """A recursive function to flatten a dictionary."""

            _data = {}
            for key, value in data.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                if isinstance(value, dict):
                    _data.update(_flatten(value, full_key))
                elif isinstance(value, list):
                    for idx, item in enumerate(value):
                        list_key = f"{full_key}.[{idx}]"
                        if isinstance(item, (dict, list)):
                            _data.update(_flatten(item, list_key))
                        else:
                            _data[list_key] = item
                else:
                    _data[full_key] = value
            return _data

        return _flatten(self._data)

    def _map_handlers(self) -> dict[str, Handler]:
        """A method to map each key to a handler."""

        def _match_key(key: str) -> Handler:
            """The method that finds the most appropriate handler for a key."""

            if key in self._handlers:
                return self._handlers[key]

            best_specificity = -1
            best_wildcard_count = float("inf")
            matched_handler = None

            for pattern, handler in self._handlers.items():
                if "*" in pattern:
                    regex = "^" + re.escape(pattern).replace("\\*", ".*") + "$"
                    if re.fullmatch(regex, key):
                        specificity = len(pattern.replace("*", ""))
                        wildcard_count = pattern.count("*")
                        if specificity > best_specificity or (
                            specificity == best_specificity
                            and wildcard_count < best_wildcard_count
                        ):
                            best_specificity = specificity
                            best_wildcard_count = wildcard_count
                            matched_handler = handler

            return matched_handler

        keys = self._map_keys()
        return {k: _match_key(k) for k in keys}

    def _inspect_function(self, fn: Callable) -> list[str]:
        """
        Gets the parameters of a function.

        Args:
            fn: Callable - The function to inspect.
        Returns:
            list[str] - The parameters of the function.
        Raises:
            TypeError - If fn is not a callable.
        """
        if not isinstance(fn, Callable):
            raise TypeError("fn must be a callable.")

        return list(inspect.signature(fn).parameters.keys())

    def add_handler(self, key: str, handler: Handler):
        """
        Adds a new handler for a specific (e.g. 'my', 'my.key') or global key
        (e.g. '*', 'my.*', 'my.*.key').

        Complex expressions including brackets, such as 'my.[a-z]'
        are currently not supported.

        A handler is a function that can be one of 'fn()',
        'fn(key)', 'fn(value)' or 'fn(key, value)'. Handlers
        may also be built-in types such as 'int', 'float',
        'str', 'bool', 'list', etc.

        Args:
            key: str - The key to add the handler to.
            handler: Handler - The handler to add.
        Returns:
            None
        Raises:
            TypeError - If key is not a string.
            toml_parser.errors.TOMLHandlerError - If the handler is invalid.
        """

        # Built-in types
        if isinstance(handler, type):
            self._handlers[key] = handler
            return

        # Not a function
        if not isinstance(handler, Callable):
            raise TOMLHandlerError("Handler must be a callable.")

        # Check if arguments are valid
        args = self._inspect_function(handler)

        ## No arguments
        if len(args) == 0:
            self._handlers[key] = handler

        ## One argument
        elif len(args) == 1:
            if args[0] not in ["key", "value"]:
                raise TOMLHandlerError(
                    f"Handler must accept 'key' or 'value', got '{args[0]}'"
                )
            self._handlers[key] = handler

        ## Two arguments
        elif len(args) == 2:
            if args != ["key", "value"]:
                raise TOMLHandlerError(
                    " ".join(
                        [
                            "Handler must accept 'key' and 'value', got",
                            f"'{args[0]}' and '{args[1]}'",
                        ]
                    )
                )
            self._handlers[key] = handler

        ## Too many arguments
        else:
            raise TOMLHandlerError("Handler must accept 0, 1, or 2 arguments.")
