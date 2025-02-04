""" Typing for validation handlers. """

from typing import Callable, Optional, Union

Handler = Union[
    Callable[[], None],
    Callable[[str], None],
    Callable[[str, Optional[str]], None],
]
