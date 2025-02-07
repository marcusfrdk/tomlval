""" Module for creating a TOML validator. """

# pylint: disable=C0103

import inspect
import re
from typing import Any, Callable, Tuple, Union

from tomlval.errors import TOMLHandlerError
from tomlval.types import Handler
from tomlval.utils import (
    dict_key_pattern,
    flatten,
    is_handler,
    stringify_schema,
)

from .toml_schema import TOMLSchema

TypeList = Union[type, Tuple[type, ...]]


class TOMLValidator:
    """A class for creating a TOML validator."""

    def __init__(
        self,
        schema: TOMLSchema = None,
        handlers: dict = None,
        on_missing: Callable[[str], Any] = lambda key: "missing",
        on_type_mismatch: Callable[
            [str, TypeList, TypeList], Any
        ] = lambda key, expected, got: "incorrect-type",
    ):
        """
        Initialize a new TOML validator.

        Types:
            TypeList - Either a single type or a tuple of types.
        Args:
            schema?: TOMLSchema - The TOML schema to validate against.
            handlers?: dict - The custom handlers to use.
            on_missing?: Callable[[str], Any] - A callback function that runs
            when a key is missing in the data, the parameter must be 'key'.
            on_type_mismatch?: Callable[[str, TypeList, TypeList], Any] - A callback
            function that runs when a key has a type does not match the
            type in the schema.
        Returns:
            None
        Raises:
            TypeError - If the schema- or handlers dictionary are invalid.
            TOMLHandlerError - If any of the handlers are invalid.
        """
        # Schema
        if schema is not None and not isinstance(schema, TOMLSchema):
            raise TypeError("Schema must be a TOMLSchema.")

        # Handlers
        if handlers is not None:
            # Not a dictionary
            if not isinstance(handlers, dict):
                raise TypeError("Handlers must be a dictionary.")

            for k, v in handlers.items():
                # Invalid key
                if not dict_key_pattern.match(k):
                    raise TOMLHandlerError(f"Invalid handler key '{k}'.")

                # Invalid handler
                if (error := is_handler(v, k)) != "":
                    raise TOMLHandlerError(error)

        # Callbacks

        ## Missing callback
        if not inspect.isfunction(on_missing):
            raise TypeError("on_missing must be a function.")

        _mp_params = set(inspect.signature(on_missing).parameters)
        if not {"key"}.issubset(_mp_params):
            raise TypeError("on_missing must accept parameter 'key'.")

        ## Type mismatch callback
        if not inspect.isfunction(on_type_mismatch):
            raise TypeError("on_type_mismatch must be a function.")

        _otm_params = set(inspect.signature(on_type_mismatch).parameters)
        if not {"key", "expected", "got"}.issubset(_otm_params):
            raise TypeError(
                "on_type_mismatch must accept parameters 'expected' and 'got'."
            )

        self._schema = schema or TOMLSchema({})
        self._handlers = handlers or {}
        self._on_missing = on_missing
        self._on_type_mismatch = on_type_mismatch

    def __str__(self) -> str:
        return stringify_schema(self.handlers)

    def _map_handlers(self, data: dict) -> dict[str, Handler]:
        """A method to map each key to a handler."""

        _handlers = flatten(self.handlers, method="schema")

        def _match_key(key: str) -> Handler:
            """The method that finds the most appropriate handler for a key."""

            key = re.sub(r"\.\[\d+]\.", "[].", key)

            if key in _handlers:
                return _handlers[key]

            best_specificity = -1
            best_wildcard_count = float("inf")
            matched_handler = None

            for pattern, handler in _handlers.items():
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

        return {k: _match_key(k) for k in data}

    def add_handler(self, key: str, fn: Handler) -> None:
        """
        Add a new handler to the validator.
        This operation will overwrite any existing handler with the same key.

        Args:
            key: str - The handler key.
            fn: Handler - The handler function.
        Returns:
            None
        Raises:
            TOMLHandlerError - If the handler function or key is invalid
        """
        # Invalid types
        if not isinstance(key, str) or not dict_key_pattern.match(key):
            raise TOMLHandlerError(f"Invalid handler key '{key}'.")

        if (error := is_handler(fn, key)) != "":
            raise TOMLHandlerError(error)

        self._handlers[key] = fn

    def validate(self, data: dict) -> dict:
        """
        Validates the TOML data.

        Args:
            data: dict - The TOML data to validate.
        Returns:
            dict - The errors in the data.
        Raises:
            TypeError - If data is not a dictionary.
            TOMLHandlerError - If any of the handlers are invalid.
        """

        # Invalid type
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary.")

        # Map handlers
        _data = flatten(data)
        _handlers = self._map_handlers(_data)

        # Run handlers
        def _run_handler(key: str, value: Any) -> Any:
            """Run a handler and return the result."""
            _handler = _handlers[key]

            # Built-in type
            if isinstance(_handler, type) and not isinstance(value, _handler):
                return self._on_type_mismatch(
                    expected=_handler, got=type(value)
                )

            # Function
            if inspect.isfunction(_handler):
                _params = list(inspect.signature(_handler).parameters)

                # No parameters
                if len(_params) == 0:
                    return _handler()

                # One parameter
                if len(_params) == 1:
                    # Key
                    if _params[0] == "key":
                        return _handler(key)
                    # Value
                    if _params[0] == "value":
                        return _handler(value)
                    # Unexpected parameter
                    raise TOMLHandlerError("Got unexpected parameter.")

                # Two parameters
                if len(_params) == 2:
                    return _handler(key, value)

                # More than two parameters
                raise TOMLHandlerError("Handler must have 0-2 parameters.")

            return False

        _results = {}
        for k, v in _data.items():
            if k in _handlers:
                _results[k] = _run_handler(k, v)

        # Missing keys
        _missing_keys = self._schema.compare_keys(_data)
        _results.update({k: self._on_missing(k) for k in _missing_keys})

        # Remove valid keys
        _results = {k: v for k, v in _results.items() if v}

        return _results

    @property
    def handlers(self) -> dict:
        """Return the handlers as a dictionary"""
        return {**self._schema.to_dict(), **self._handlers}


if __name__ == "__main__":
    import os
    import tomllib

    # Data
    path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "full_spec",
            "schema.toml",
        )
    )

    with open(path, "rb") as f:
        _dfs = tomllib.load(f)

    _dd = {}

    _d = _dd

    # Schema
    # _s = TOMLSchema({"array_of_tables[].name": str})
    _s = TOMLSchema(
        {
            # "array_of_tables": [
            #     {
            #         "name": lambda value: (
            #             "invalid-str" if len(value) <= 0 else None
            #         ),
            #         "value": int,
            #     }
            # ],
            # "nested_array": [{"inner?": [{"name": str}]}],
            # "nested?": {"key": str},
            "nested?[].key": str
        }
    )

    # Handlers
    _h = {}

    _v = TOMLValidator(_s, _h)
    # _v.add_handler("*", float)

    # Validate
    errors = _v.validate(_d)

    # print(errors)
    print()
    print(_v)
    print(errors)
