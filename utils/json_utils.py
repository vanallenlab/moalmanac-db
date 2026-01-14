import json
import typing


def get_record_by_key_value(records: list[dict], value: typing.Any, key: str = "id", strict: bool = True) -> typing.Optional[dict] | None:
    """
    Retrieves a single record where a specified key matches the given value.
    Raises ValueError if zero or multiple matches are found, unless strict is False.

    Args:
        records (list[dict]): A list of dictionaries to search.
        value (any): The value to match.
        key (str): The key to check (default: "id").
        strict (bool): if True, raise a ValueError when not exactly one match is found.

    Returns:
        dict or None: A dictionary of the matching record, or None if no matches are found.

    Raises:
        ValueError: If the number of results is not exactly 1, and strict is enabled.
    """
    matches = get_records_by_key_value(records=records, key=key, value=value)
    if strict and len(matches) != 1:
        raise ValueError(f"Warning: Expected 1 result for {key} == {value}, found {len(matches)}.")
    return matches[0] if matches else None

def get_records_by_key_value(records: list[dict], value: typing.Any, key: str = "id") -> list[dict]:
    """
        Retrieves a records from a list where a specified key matches the given value.

        Args:
            records (list[dict]): A list of dictionaries to search.
            value (any): The value to match.
            key (str): The key to check (default: "id").

        Returns:
            list[dict]: A list of matching records.
    """
    return [record for record in records if record.get(key) == value]

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
