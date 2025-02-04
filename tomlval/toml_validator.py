""" Validator class for validating TOML data. """

# pylint: disable=C0103,R1702

import inspect
import re
from typing import Any, Callable, List, Tuple, Union

from tomlval.errors import TOMLHandlerError
from tomlval.types import Handler, ValidatedSchema
from tomlval.utils import flatten
from tomlval.utils.regex import key_pattern

from .toml_schema import TOMLSchema

TypeList = Union[type, list[type]]


class TOMLValidator:
    """Class to validate TOML data."""

    def __init__(self, data: dict, schema: TOMLSchema = None):
        """
        Initialize the TOML validator.

        Args:
            data: dict - The TOML data to validate.
            schema: dict - The TOML schema to validate against.
        Returns:
            None
        Raises:
            TypeError - If data is not a dictionary or
            schema is not a TOMLSchema.
        """

        # Data
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary.")

        # Schema
        if schema is not None:
            if not isinstance(schema, TOMLSchema):
                raise TypeError("Schema must be a TOMLSchema.")

        self._data = flatten(data)
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

    def _inspect_function(self, fn: Callable) -> List[str]:
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

    def _get_missing_keys(self) -> list[str]:
        """Get a list of keys missing in the data."""
        # return [k for k in self._schema if k not in self._data]
        if not isinstance(self._schema, TOMLSchema):
            return []

        return [
            k
            for k in self._schema
            if k not in self._data and not k.endswith("?")
        ]

    def _get_invalid_types(
        self,
    ) -> List[Tuple[str, Tuple[Any, TypeList, TypeList]]]:
        """Get a list of keys with invalid types."""
        invalid_types = []

        if not isinstance(self._schema, TOMLSchema):
            return invalid_types

        for key, value in self._data.items():
            if key in self._schema:
                # List of types
                if isinstance(self._schema[key], list):

                    # Check if any of the types are valid
                    if isinstance(value, list):
                        invalid_list_types = set()
                        for t in value:
                            if type(t) not in self._schema[key]:
                                invalid_list_types.add(type(t))
                        invalid_list_types = list(invalid_list_types)
                    else:
                        invalid_list_types = type(value)

                    if invalid_list_types:
                        invalid_types.append(
                            (
                                key,
                                (value, self._schema[key], invalid_list_types),
                            )
                        )

                # Single type
                elif not isinstance(value, self._schema[key]):
                    types = (
                        self._schema[key]
                        if isinstance(self._schema[key], type)
                        else type(value)
                    )
                    invalid_types.append(
                        (key, (value, self._schema[key], types))
                    )

        return invalid_types

    def _get_handler_results(self) -> dict[str, Any]:
        """Runs the handlers and gets the results."""
        results = {}

        for k, h in self._map_handlers().items():
            if h is None:
                continue

            # Built in type
            if isinstance(h, type):
                value = self._data[k]
                if not isinstance(value, h):
                    results[k] = ("invalid-type", (value, h, type(value)))
                continue

            # List of build in types
            if isinstance(h, (list, tuple)):
                _value = self._data[k]
                _type = type(_value)

                if not any(isinstance(_value, t) for t in h):
                    results[k] = ("invalid-type", (_value, h, _type))

                continue

            # Custom handler
            fn_args = self._inspect_function(h)

            # No arguments
            if len(fn_args) == 0:
                results[k] = h()
            elif len(fn_args) == 1:
                if fn_args[0] == "key":
                    results[k] = h(k)
                elif fn_args[0] == "value":
                    results[k] = h(self._data[k])
            elif len(fn_args) == 2:
                results[k] = h(k, self._data[k])

        return results

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

        # Iterable of types
        if isinstance(handler, (list, tuple)) and all(
            isinstance(h, type) for h in handler
        ):
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
        fn_args = self._inspect_function(handler)

        ## No arguments
        if len(fn_args) == 0:
            self._handlers[key] = handler

        ## One argument
        elif len(fn_args) == 1:
            if fn_args[0] not in ["key", "value"]:
                raise TOMLHandlerError(
                    f"Handler must accept 'key' or 'value', got '{fn_args[0]}'"
                )
            self._handlers[key] = handler

        ## Two arguments
        elif len(fn_args) == 2:
            if fn_args != ["key", "value"]:
                raise TOMLHandlerError(
                    " ".join(
                        [
                            "Handler must accept 'key' and 'value', got",
                            f"'{fn_args[0]}' and '{fn_args[1]}'",
                        ]
                    )
                )
            self._handlers[key] = handler

        ## Too many arguments
        else:
            raise TOMLHandlerError("Handler must accept 0, 1, or 2 arguments.")

    def validate(self) -> ValidatedSchema:
        """Validates the TOML data."""
        handler_results = self._get_handler_results()
        missing_keys = self._get_missing_keys()
        invalid_types = self._get_invalid_types()

        errors = {
            **{k: ("missing", None) for k in missing_keys},
            **{k: ("invalid-type", v) for k, v in invalid_types},
            **{
                k: ("handler", v)
                for k, v in handler_results.items()
                if v is not None
            },
        }

        return errors


if __name__ == "__main__":
    val = TOMLValidator({"a_1_b": "1"})
    # val.add_handler("a_*_b", int)
    val.add_handler("a_*_b", (int, float))

    print(val.validate())
