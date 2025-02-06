""" A module for defining a TOML schema structure. """

from typing import Any

from tomlval.errors import TOMLSchemaError
from tomlval.utils import flatten, is_handler, key_pattern, stringify_schema


class TOMLSchema:
    """A class for defining and validating a TOML schema."""

    def __init__(self, schema: dict):
        self._raw_schema = schema
        self._schema = flatten(self._raw_schema)
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

            ## Simple type
            elif message := is_handler(v, k):
                raise TOMLSchemaError(message)

        return None

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


if __name__ == "__main__":

    def my_fn(key):
        """My function"""

    _schema = {
        "string": str,
        "multi_typed": (str, int, float, lambda key: None),
        "fn1": lambda: None,
        "fn2": lambda key: None,
        "fn3": lambda key, value: None,
        "my_fn": my_fn,
        "multi_fn": [str, lambda key: None],
        "nested_list": [
            {"key": str},
            {
                "key": int,
                "nested_list": [{"key": str}, {"key": int}],
            },
        ],
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
    # print(s.to_dict())
    print(s)
