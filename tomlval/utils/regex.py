""" Regex patterns for parsing TOML files. """

import re

key_pattern = re.compile(r"^(?:\*|\w+)(?:\.(?:\*|\w+))*\*?\??$")
