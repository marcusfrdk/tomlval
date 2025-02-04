""" Validator class for validating TOML data. """

import inspect
import re
from typing import Any, Callable

from tomlval.errors import TOMLHandlerError, TOMLSchemaError
from tomlval.types import Handler, ValidatedSchema
from tomlval.utils import flatten
from tomlval.utils.regex import key_pattern


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
            TypeError - If data is not a dictionary.
            tomlval.errors.TOMLSchemaError - If the schema is invalid.
        """

        # Data
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary.")

        # Schema
        if schema is not None:
            if not self._validate_schema(schema):
                raise TOMLSchemaError()

        self._data = data
        self._schema = schema
        self._handlers = {}

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

        return {k: _match_key(k) for k in flatten(self._data)}

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

    def _validate_schema(self, schema: dict = None) -> bool:
        """Method to validate a schema."""
        schema = schema or self._schema

        if not isinstance(schema, dict):
            return False

        def _check_schema(schema: dict) -> bool:
            for k, v in schema.items():
                if isinstance(v, dict):
                    return _check_schema(v)
                if not isinstance(v, type):
                    return False
            return True

        return _check_schema(schema)

    def _get_missing_keys(self) -> list[str]: ...

    def _get_invalid_types(self) -> list[tuple[str, Any]]: ...

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
            ValueError - If the key has an invalid format.
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

        # Key type
        if not isinstance(key, str):
            raise TypeError("Key must be a string.")

        # Invalid key
        if not key_pattern.match(key):
            raise ValueError(f"Invalid key '{key}'.")

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

    def validate(self) -> ValidatedSchema:
        """"""


if __name__ == "__main__":
    import pathlib
    import tomllib

    data_path = pathlib.Path("examples/full_spec.toml")

    with data_path.open("rb") as file:
        toml_data = tomllib.load(file)

    validator = TOMLValidator(toml_data, schema={"name": str, "age": "nice"})

    validator.add_handler("string*c", str)

    # for k, v in validator.validate().items():
    #     print(f"{k}: {v} ({type(v)})")
