import json

def json_records(file: str) -> list[dict]:
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
