""" Function to check if a file is a TOML file. """

import tomllib

from tomlval.types import PathOrStr

from .to_path import to_path


def is_toml(path_or_str: PathOrStr) -> bool:
    """
    Check is a file is a valid TOML file.

    Args:
        path_or_str: PathOrStr - A pathlib.Path object or
        string representation of a file path.
    Returns:
        bool - True if the file is a valid TOML file, False otherwise.
    Raises:
        None
    """
    try:
        path = to_path(path_or_str)

        if not path.is_file():
            return False

        with path.open("rb") as file:
            tomllib.load(file)
            return True
    except tomllib.TOMLDecodeError:
        return False
