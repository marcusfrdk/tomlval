""" A module to unflatten a flattened dictionary into a nested dictionary. """

# pylint: disable=R0912


def unflatten(dictionary: dict) -> dict:
    """
    A function to unflatten a single level dictionary into a nested dictionary.

    Args:
        dictionary: dict - The single level dictionary to unflatten.
    Returns:
        dict - The nested dictionary.
    Raises:
        ValueError - If the dictionary is not a single level dictionary.
    """

    def is_list_index(segment: str) -> bool:
        return (
            segment.startswith("[")
            and segment.endswith("]")
            and segment[1:-1].isdigit()
        )

    result = {}
    for flat_key, value in dictionary.items():
        segments = flat_key.split(".")
        current = result
        for i, segment in enumerate(segments):
            is_last = i == len(segments) - 1
            if is_list_index(segment):
                index = int(segment[1:-1])
                if not isinstance(current, list):
                    raise ValueError(
                        " ".join(
                            [
                                "Expected list at segment",
                                f"'{segment}' in key '{flat_key}'",
                            ]
                        )
                    )
                while len(current) <= index:
                    current.append(None)
                if is_last:
                    current[index] = value
                else:
                    if current[index] is None:
                        next_seg = segments[i + 1]
                        current[index] = [] if is_list_index(next_seg) else {}
                    current = current[index]
            else:
                if not isinstance(current, dict):
                    raise ValueError(
                        " ".join(
                            [
                                "Expected dict at segment",
                                f"'{segment}' in key '{flat_key}'",
                            ]
                        )
                    )
                if is_last:
                    current[segment] = value
                else:
                    if segment not in current:
                        next_seg = segments[i + 1]
                        current[segment] = [] if is_list_index(next_seg) else {}
                    current = current[segment]
    return result
