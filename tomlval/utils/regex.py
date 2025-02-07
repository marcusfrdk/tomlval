""" Regex patterns for parsing TOML files. """

import re

key_pattern = re.compile(
    r"^(?!.*\*\?)"
    r"(?!.*\*{2,})"
    r"(?:(?:\*?[\w*]+(?:\?)?(?:\[\])?\.)+)?"
    r"\*?[\w*]+(?:\?)?(?!\[\])(?:\*|\?)?$"
)

dict_key_pattern = re.compile(
    r"^(?!.*\*\*)" + r"(?:(?:\*?[\w*]+\.)+)?" + r"\*?[\w*]+(?:\*)?$"
)

nested_array_pattern = re.compile(r"\.\[(\d+)]\.")
