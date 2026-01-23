import json


def dictionary(
    data: dict,
    keys_list: list[str],
    file: str,
    quiet: bool = False,
) -> None:
    """
    Write JSON from an input object of dictionary

    Args:
        data (dict): An object of type dictionary, though one key value should be a list of dictionaries (records).
        keys_list (list[str]): A list of keys that are of type list[dict] (records).
        file (str): The output file path.
        quiet (bool): Suppress print statement if True

    Raises:
        TypeError: If the keys provided with keys_list are not a list of dictionaries.
        ValueError: If the JSON serialization fails.
    """

    if not isinstance(data, dict):
        raise TypeError("The input data must be of type dict")

    for key in keys_list:
        if not all(isinstance(item, dict) for item in data[key]):
            raise TypeError(
                f"All elements in the list must be dictionaries for key {key}."
            )

    try:
        # Serialize the python object (data) to a JSON formatted string
        json_object = json.dumps(data, indent=2)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize the object to JSON: {e}")

    try:
        # Write the JSON string to the specified file
        with open(file, "w") as outfile:
            outfile.write(json_object)
        if not quiet:
            print(f"JSON successfully written to {file}")
    except IOError as e:
        raise IOError(f"Failed to write to file {file}: {e}")


def records(data: list[dict], file: str) -> None:
    """
    Writes JSON from the input object of list[dict]

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
        # Serialize the python object (data) to a JSON formatted string
        json_object = json.dumps(data, indent=2)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize the object to JSON: {e}")

    try:
        # Write JSON string to the specified file
        with open(file, "w") as outfile:
            outfile.write(json_object)
        print(f"JSON successfully written to {file}")
    except IOError as e:
        raise IOError(f"Failed to write to file {file}: {e}")
