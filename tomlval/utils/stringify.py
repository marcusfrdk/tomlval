""" Module with utilities to print a schema. """

import inspect
import json

from .flatten import flatten


class SchemaEncoder(json.JSONEncoder):
    """JSON encoder for the TOML schema."""

    def default(self, o):
        print(o)

        return super().default(o)


def stringify_schema(schema: dict) -> str:
    """
    Stringify a TOML schema.

    Args:
        schema: dict - The TOML schema.
    Returns:
        str - The stringified schema.
    Raises:
        TypeError - If schema is not a dictionary.
        JSONEncodeError - If the schema cannot be encoded.
    """

    def _get_name(o):
        """Get the name of a type, function or lambda."""
        if isinstance(o, type):
            return o.__name__

        # Function
        if inspect.isfunction(o):
            # Params
            params = inspect.signature(o).parameters

            # Lambda
            if o.__name__ == "<lambda>":
                if len(params) == 0:
                    return "lambda"
                return f"lambda {', '.join(params.keys())}"

            # Named function
            return f"{o.__name__}({', '.join(params.keys())})"

    if not isinstance(schema, dict):
        raise TypeError("Schema must be a dictionary.")

    rows = []
    for k, v in flatten(schema).items():
        if isinstance(v, tuple):
            rows.append(f"{k} = ({', '.join(map(_get_name, v))})")
        elif isinstance(v, list):
            rows.append(f"{k} = [{', '.join(map(_get_name, v))}]")
        else:
            rows.append(f"{k} = {_get_name(v)}")

    return "\n".join(rows)
