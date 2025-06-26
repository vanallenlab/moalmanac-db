import json
import typing


def fetch_records_by_key_value(records: list[dict], value: typing.Any, key: str = "id", warn: bool = True) -> typing.Optional[dict]:
    """
    Retrieves records where a specific key matches a given value.

    Args:
        records (list[dict]): A list of dictionaries to search.
        value (any): The value to match.
        key (str): The key to check (default: "id").
        warn (bool): Whether to warn and exit if the number of results is not 1 (default: True).

    Returns:
        dict or None: A list of matching records, or None if no matches are found.

    Raises:
        ValueError: If the number of results is not exactly 1 and warnings are enabled.
    """
    results = [record for record in records if record.get(key) == value]

    if warn and len(results) != 1:
        ValueError(f"Warning: Expected 1 result for {key} == {value}, found {len(results)}.")

    return next(iter(results), None)


def rename_key(dictionary: dict, old_key: str, new_key: str) -> None:
    """
    Renames a key in a dictionary.

    Args:
        dictionary (dict): The dictionary to modify.
        old_key (str): The key to rename.
        new_key (str): The new key name.

    Raises:
        KeyError: If the old_key does not exist in the dictionary.
        ValueError: If the new_key already exists in the dictionary.
    """
    if old_key not in dictionary:
        raise KeyError(f"Key '{old_key}' not found in the dictionary.")

    if new_key in dictionary:
        raise ValueError(f"Key '{new_key}' already exists in the dictionary.")

    dictionary[new_key] = dictionary.pop(old_key)
