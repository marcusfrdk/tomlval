""" Custom path types and validation functions. """

import os
import pathlib

from tomlval.types import PathOrStr


def to_path(path_or_str: PathOrStr) -> pathlib.Path:
    """
    Convert a path or string to a Path object.

    Args:
        path_or_str: PathOrStr - A pathlib.Path object or
        string representation of a file path.
    Returns:
        Path - A pathlib.Path object.
    Raises:
        TypeError: If the input is not a string or pathlib.Path object.
    """
    if not isinstance(path_or_str, (str, pathlib.Path)):
        raise TypeError("Input must be a string or a pathlib.Path object")

    if isinstance(path_or_str, pathlib.Path):
        return path_or_str

    abs_path = os.path.abspath(os.path.expanduser(path_or_str))
    path_obj = pathlib.Path(abs_path)
    return path_obj if path_obj.is_symlink() else path_obj.resolve()
