import json
import typing


def fetch_records_by_key_value(records: list[dict], value: typing.Any, key: str = "id", warn: bool = True) -> list[dict]:
    """
    Retrieves records where a specific field matches a given value.

    Args:
        records (list[dict]): A list of dictionaries to search.
        value (any): The value to match.
        key (str): The field to check (default: "id").
        warn (bool): Whether to warn and exit if the number of results is not 1 (default: True).

    Returns:
        list[dict]: A list of matching records.

    Raises:
        ValueError: If the number of results is not exactly 1 and warnings are enabled.
    """
    results = [record for record in records if record.get(key) == value]

    if warn and len(results) != 1:
        ValueError(f"Warning: Expected 1 result for {key} == {value}, found {len(results)}.")

    return results


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


def load(file: str) -> list[dict]:
    """
    Loads and parses a JSON file.

    Args:
        file (str): Path to the JSON file.

    Returns:
        list[dict]: Parsed data from the JSON file.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    try:
        with open(file, "r") as fp:
            data = json.load(fp)
        return data
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {file}") from e
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in file: {file}", e.doc, e.pos)


def write_dict(data: dict, keys_list: list[str], file:str) -> None:
    """
    Write json from input object of dictionary

    Args:
        data (dict): A object of type dictionary, though one key value should be a list of dictionaries (records).
        keys_list (list[str]): A list of keys that are of type list[dict] (records).
        file (str): The output file path.

    Raises:
        TypeError: If the keys provided with keys_list are not a list of dictionaries.
        ValueError: If the JSON serialization fails.
    """

    if not isinstance(data, dict):
        raise TypeError("The input data must be of type dict")

    for key in keys_list:
        if not all(isinstance(item, dict) for item in data[key]):
            raise TypeError(f"All elements in the list must be dictionaries for key {key}.")

    try:
        # Serialize python object (data) to a JSON formatted string
        json_object = json.dumps(data, indent=4)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize the object to JSON: {e}")

    try:
        # Write json string to the specified file
        with open(file, "w") as outfile:
            outfile.write(json_object)
        print(f"JSON successfully written to {file}")
    except IOError as e:
        raise IOError(f"Failed to write to file {file}: {e}")


def write_records(data: list[dict], file:str) -> None:
    """
    Writes json from input object of list[dict]

    Args:
        data (list[dict]): A object of type list with elements as dictionaries.
        file (str): The output file path.

    Raises:
        TypeError: If the input is not a list of dictionaries.
        ValueError: If the JSON serialization fails.
    """
    if not isinstance(data, list):
        raise TypeError("The input data must be of type list")

    if not all(isinstance(item, dict) for item in data):
        raise TypeError("All elements in the list must be dictionaries.")

    try:
        # Serialize python object (data) to a JSON formatted string
        json_object = json.dumps(data, indent=4)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize the object to JSON: {e}")

    try:
        # Write json string to the specified file
        with open(file, "w") as outfile:
            outfile.write(json_object)
        print(f"JSON successfully written to {file}")
    except IOError as e:
        raise IOError(f"Failed to write to file {file}: {e}")
