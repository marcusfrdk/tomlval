""" Regex patterns for parsing TOML files. """

import re

key_pattern = re.compile(
    r"^(?!.*\*\?)"
    r"(?!.*\*{2,})"
    r"(?:(?:\*?[\w*]+(?:\?)?(?:\[\])?\.)+)?"
    r"\*?[\w*]+(?:\?)?(?!\[\])(?:\*|\?)?$"
)
