""" A schema with custom handlers. """

import re

from tomlval import TOMLSchema

schema = TOMLSchema(
    {
        "*_name": str,
        "id": lambda value: re.match(r"^[A-Za-z-]+$", value),
        "age": lambda value: 0 < value,
        "*": lambda: "invalid-key",
    }
)
