""" A module for defining a TOML schema structure. """

import json
import re
from typing import Any, List, Tuple, Union

from tomlval.errors import TOMLSchemaError
from tomlval.utils import flatten, key_pattern

index_pattern = re.compile(r"\.\[\d+\]$")


class JSONEncoder(json.JSONEncoder):
    """A JSON encoder that can handle sets."""

    def default(self, o):
        if isinstance(o, type):
            return o.__name__
        return super().default(o)


class TOMLSchema:
    """A class for defining a TOML schema structure."""

    def __init__(self, schema: dict):
        """
        Initialize a new TOML schema.

        A schema is a dictionary with keys as strings and values as types.
        This is used to define an outline of how the validator should interpret
        the data and handle certain errors.

        Example:
            {
                "string": str,
                "number": (int, float),
                "boolean": bool,
                "string_list": [str],
                "number_list": [int, float],
                "mixed_list": [str, int, float],
                "nested": {
                    "key": str,
                    "value": int
                }
            }

        Optional values can be added by suffixing the key with a question mark.

        Example:
            {
                "string?": str,
                "number": (int, float)
            }

        In this case, string is an optional value, while number is required.

        Args:
            schema: dict - The TOML schema.
        Returns:
            None
        Raises:
            tomlval.errors.TOMLSchemaError - If the schema is invalid.
        """

        self._validate(schema)
        self._nested_schema = schema
        self._flat_schema = flatten(schema)

    def _validate(self, schema: dict) -> None:
        """Validate a TOML schema."""
        if not isinstance(schema, dict):
            raise TOMLSchemaError("Schema must be a dictionary.")

        def _raise_exception(value: Any) -> None:
            message = " ".join(
                [
                    "Found type",
                    f"'{type(value).__name__}'",
                    "in schema, only use built-in types",
                    "such as str, int, float, etc.",
                ]
            )

            if isinstance(value, str):
                message = (
                    "Found string literal in schema, use type 'str' instead."
                )

            raise TOMLSchemaError(message)

        def _check_schema(schema: dict) -> bool:
            """Check the schema recursively."""
            for k, v in schema.items():
                # Keys
                if not isinstance(k, str):
                    raise TOMLSchemaError(
                        f"Invalid key type '{str(k)}' in schema."
                    )

                if not key_pattern.match(k):
                    raise TOMLSchemaError(f"Invalid key '{k}' in schema.")

                # Values
                if isinstance(v, dict):
                    return _check_schema(v)

                ## Tuple/List
                if isinstance(v, (tuple, list)):
                    for t in v:
                        if not isinstance(t, type):
                            _raise_exception(t)

                ## Simple type
                elif not isinstance(v, type):
                    _raise_exception(v)

            return None

        _check_schema(schema)

    def __str__(self) -> str:
        return json.dumps(self._nested_schema, cls=JSONEncoder, indent=2)

    def __repr__(self) -> str:
        return f"<TOMLSchema keys={len(self)}>"

    def __len__(self) -> int:
        return len(self.keys())

    def __getitem__(self, key: str) -> Union[type, Tuple[type]]:
        """Get an item from a TOML schema."""
        if self.get(f"{key}?") is not None:
            key = f"{key}?"
        return self._flat_schema[key]

    def __contains__(self, key: str) -> bool:
        """Check if a key is in a TOML schema."""
        return key in self._flat_schema

    def __iter__(self):
        return iter(self._flat_schema)

    def get(self, key: str, default=None) -> Union[type, Tuple[type]]:
        """Get an item from a TOML schema."""
        if (value := self._flat_schema.get(key)) is None:
            value = self._flat_schema.get(f"{key}?")
        return value

    def keys(self) -> list[str]:
        """Get the keys from a TOML schema."""
        return sorted(self._flat_schema.keys())

    def values(self) -> List[Union[type, Tuple[type]]]:
        """Get the values from a TOML schema."""
        return list(self._flat_schema.values())

    def items(self) -> List[Tuple[str, Union[type, Tuple[type]]]]:
        """Get the items from a TOML schema."""
        return list(self._flat_schema.items())


if __name__ == "__main__":
    s = TOMLSchema({"string?": str, "number": (int, float)})
    print(s.get("string"))
