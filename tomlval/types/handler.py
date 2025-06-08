"""Typing for validation handlers."""

from typing import Any, Callable, Optional, Union

Handler = Union[
    type,
    Callable[[], Any],
    Callable[[str], Any],
    Callable[[str, Optional[str]], Any],
]
