"""A module for defining a TOML schema structure."""

import fnmatch
import re
from typing import Any, List, Tuple

from tomlval.errors import TOMLSchemaError
from tomlval.utils import (
    flatten,
    is_handler,
    key_pattern,
    nested_array_pattern,
    stringify_schema,
)


class TOMLSchema:
    """A class for defining and validating a TOML schema."""

    def __init__(self, schema: dict):
        self._raw_schema = schema
        self._schema = flatten(self._raw_schema, method="schema")
        self._keys = {}
        self._validate_schema(self._schema)

    def __str__(self) -> str:
        return stringify_schema(self._schema)

    def __repr__(self) -> str:
        return f"<TOMLSchema keys={len(self)}>"

    def __len__(self) -> int:
        return len(self._schema)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TOMLSchema):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(str(self))

    def __contains__(self, key: str) -> bool:
        return key in self._schema or key in self._keys

    def __getitem__(self, key: str) -> Any:
        if key in self._schema:
            return self._schema[key]
        if key in self._keys:
            return self._schema[self._keys[key]]
        raise KeyError(f"Key '{key}' not found in schema.")

    def _validate_schema(self, schema: dict) -> None:
        if not isinstance(schema, dict):
            raise TOMLSchemaError("Schema must be a dictionary.")

        for k, v in (schema or self._schema).items():
            # Keys
            if not isinstance(k, str):
                raise TOMLSchemaError(f"Invalid key type '{str(k)}' in schema.")

            if not key_pattern.match(k):
                raise TOMLSchemaError(f"Invalid key '{k}' in schema.")

            # Values

            ## Nested dictionary
            if isinstance(v, dict):
                return self._validate_schema(v)

            ## Nested list
            if isinstance(v, list) and all(isinstance(i, dict) for i in v):
                return self._validate_schema(v[0])

            ## Tuple/List
            if isinstance(v, (tuple, list)):
                invalid_indexes = []
                for i, h in enumerate(v):
                    if is_handler(h, k):
                        invalid_indexes.append(i)
                if invalid_indexes:
                    invalid_indexes = ", ".join(map(str, invalid_indexes))
                    raise TOMLSchemaError(
                        " ".join(
                            [
                                "Invalid handler at position",
                                f"{invalid_indexes} in key '{k}'.",
                            ]
                        )
                    )

            ## Regex pattern
            if isinstance(v, re.Pattern):
                pass

            ## Simple type
            elif message := is_handler(v, k):
                raise TOMLSchemaError(message)

        # Remap keys
        for k in schema:
            old_key = k
            new_key = str(k).replace("[]", "").replace("?", "")
            self._keys[new_key] = old_key

        return None

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the schema.

        Args:
            key: str - The key to get the value for.
            default: Any - The default value to return
            if the key does not exist.
        Returns:
            Any - The value for the key.
        Raises:
            None
        """

        if key in self._schema:
            return self._schema[key]

        if key in self._keys:
            return self._schema[self._keys[key]]

        return default

    def keys(self) -> List[str]:
        """
        Returns the keys in the schema.

        Args:
            None
        Returns:
            list[str] - The keys in the schema.
        Raises:
            None
        """
        return list(self._schema.keys())

    def values(self) -> List[Any]:
        """
        Returns the values in the schema.

        Args:
            None
        Returns:
            list[str] - The values in the schema.
        Raises:
            None
        """
        return list(self._schema.values())

    def items(self) -> List[Tuple[str, Any]]:
        """
        Returns the items in the schema.

        Args:
            None
        Returns:
            list[str] - The items in the schema.
        Raises:
            None
        """
        return list(self._schema.items())

    def to_dict(self) -> dict:
        """
        Returns the schema as a dictionary.

        Args:
            None
        Returns:
            dict - The schema as a dictionary.
        Raises:
            None
        """
        return self._raw_schema

    def compare_keys(self, dictionary: dict) -> list[str]:
        """
        Compare the keys in the schema with a dictionary.

        If a key with a wildcard is present, it will cause
        the key to be considered as present if any key matches.

        Currently, nested arrays also consider the key as present
        for any match. This does not make sure ALL sub-arrays
        include the key.

        Args:
            dictionary: dict - The dictionary to compare.
        Returns:
            list[str] - The keys that are missing in the dictionary.
        Raises:
            None
        """

        # TODO:
        # - Implement a more thorough comparison.
        #   At the moment, this method only checks for existence.
        #   So it does not check if all nested keys are valid,
        #   only a single one.
        # - Better optional checking
        #   There are some edge cases that can occur when only
        #   checking for the existence of a ?-character.

        provided_keys = set(
            re.sub(nested_array_pattern, ".", k) for k in dictionary
        )

        # Remove characters and map keys
        required_keys = set()
        nested_arrays = {}

        for key in self.keys():
            if "*" not in key and "?" not in key:
                _key = key.replace("[]", "")
                if "[]" in key:
                    nested_arrays[_key] = key
                required_keys.add(_key)

        # Wildcard keys
        for key in self.keys():
            if "*" in key:
                pattern = key.replace("[]", "")
                if not any(
                    fnmatch.fnmatch(provided_key, pattern)
                    for provided_key in provided_keys
                ):
                    required_keys.add(pattern)

        # Re-substitute keys
        for k, v in nested_arrays.items():
            if k in required_keys:
                required_keys.remove(k)
                required_keys.add(v)

        return list(required_keys - provided_keys)


if __name__ == "__main__":

    def my_fn(key):
        """My function"""

    _schema = {
        # "string?": str,
        # "multi_typed": (str, int, float, lambda key: None),
        # "fn1": lambda: None,
        # "fn2": lambda key: None,
        # "fn3": lambda key, value: None,
        # "my_fn": my_fn,
        # "multi_fn": [str, lambda key: None],
        # "nested_list": [
        #     {"key": str},
        #     {
        #         "key": int,
        #         "nested_list": [{"key": str}, {"key": int}],
        #     },
        # ],
        "nested?": {
            "string": str,
            "fn1": lambda: None,
            "fn2": lambda key: None,
            "fn3": lambda key, value: None,
            "my_fn": my_fn,
            "multi_fn": [str, lambda key: None],
        },
    }

    s = TOMLSchema(_schema)
    print(s)
    # print(s.to_dict())
    # print(s.get("string"))
    # print(s["string"])
