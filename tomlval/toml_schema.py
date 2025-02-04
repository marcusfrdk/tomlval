""" A module for defining a TOML schema structure. """

import json
import re
from collections import defaultdict
from typing import List, Tuple, Union

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

        Args:
            schema: dict - The TOML schema.
        Returns:
            None
        Raises:
            tomlval.errors.TOMLSchemaError - If the schema is invalid.
        """

        self._validate(schema)
        self._nested_schema = schema
        self._flat_schema = self._flatten(schema)

    def _validate(self, schema: dict) -> None:
        """Validate a TOML schema."""
        if not isinstance(schema, dict):
            raise TOMLSchemaError("Schema must be a dictionary.")

        def _check_schema(schema: dict) -> bool:
            """Check the schema recursively."""
            for k, v in schema.items():
                # Keys
                if not isinstance(k, str):
                    raise TOMLSchemaError(
                        f"Invalid key type '{str(k)}' in schema."
                    )
                elif not key_pattern.match(k):
                    raise TOMLSchemaError(f"Invalid key '{k}' in schema.")

                # Values
                if isinstance(v, dict):
                    return _check_schema(v)

                ## Tuple/List
                if isinstance(v, (tuple, list)):
                    for t in v:
                        if not isinstance(t, type):
                            raise TOMLSchemaError(
                                " ".join(
                                    [
                                        "Invalid type",
                                        f"'{type(t).__name__}'",
                                        "found in schema.",
                                    ]
                                )
                            )

                ## Simple type
                elif not isinstance(v, type):
                    raise TOMLSchemaError(
                        f"Invalid type '{type(v).__name__}' found in schema."
                    )

            return None

        _check_schema(schema)

    def _flatten(self, schema: dict) -> dict:
        """A custom version of the flatten function to combine lists."""

        pattern = re.compile(r"^(.*)\.\[(\d+)\]$")
        result = {}
        temp = defaultdict(list)

        for key, value in flatten(schema).items():
            match = pattern.match(key)

            if match:
                base_key, index = match.groups()
                index = int(index)
                temp[base_key].append((index, value))
            else:
                result[key] = value

        for base_key, items in temp.items():
            sorted_values = [
                val for _, val in sorted(items, key=lambda x: x[0])
            ]
            result[base_key] = sorted_values

        return result

    def __str__(self) -> str:
        return json.dumps(self._nested_schema, cls=JSONEncoder, indent=2)

    def __repr__(self) -> str:
        return f"<TOMLSchema keys={len(self)}>"

    def __len__(self) -> int:
        return len(self.keys())

    def __getitem__(self, key: str) -> Union[type, Tuple[type]]:
        """Get an item from a TOML schema."""
        return self._flat_schema[key]

    def __contains__(self, key: str) -> bool:
        """Check if a key is in a TOML schema."""
        return key in self._flat_schema

    def __iter__(self):
        return iter(self._flat_schema)

    def get(self, key: str, default=None) -> Union[type, Tuple[type]]:
        """Get an item from a TOML schema."""
        return self._flat_schema.get(key, default)

    def keys(self) -> list[str]:
        """Get the keys from a TOML schema."""
        return sorted(self._flat_schema.keys())

    def values(self) -> List[Union[type, Tuple[type]]]:
        """Get the values from a TOML schema."""
        return list(self._flat_schema.values())

    def items(self) -> List[Tuple[str, Union[type, Tuple[type]]]]:
        """Get the items from a TOML schema."""
        return list(self._flat_schema.items())
