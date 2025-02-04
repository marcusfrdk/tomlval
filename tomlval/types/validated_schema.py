""" A type for a validated schema. """

from typing import Any, Tuple, Union

# {"key": ("message", value)}
ValidatedSchema = dict[str, Union[Tuple[str, Any], "ValidatedSchema"]]
