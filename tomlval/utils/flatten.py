""" A function to flatten a dictionary into a single level dictionary. """


def flatten(dictionary: dict) -> dict:
    """
    A function to flatten a dictionary into a single level dictionary.

    Args:
        dictionary: dict - The dictionary to flatten.
    Returns:
        dict - The flattened dictionary
    Raises:
        None
    """

    def _flatten(data: dict, parent_key: str = "") -> dict:
        """A recursive function to flatten a dictionary."""
        _data = {}
        for key, value in data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):
                _data.update(_flatten(value, full_key))
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    list_key = f"{full_key}.[{idx}]"
                    if isinstance(item, (dict, list)):
                        _data.update(_flatten(item, list_key))
                    else:
                        _data[list_key] = item
            else:
                _data[full_key] = value
        return _data

    return _flatten(dictionary)
