def find_trailing_spaces(records, key):
    """
    Identifies if any value associated with `key` contains trailing spaces for each record in `records`.

    Args:
        records (list[dict]): list of dictionaries.
        key (str): The key to look for trailing spaces, required for each record in records.

    Returns:
        failed_records (list[dict]): list of failed records, returning only the `id` and `key` that failed.
    """
    failed_records = []
    for record in records:
        if has_trailing_spaces(record[key]):
            failed_records.append(record['id'])
    return failed_records

def has_trailing_spaces(string: str) -> bool:
    """
    Checks if a string has trailing spaces.

    Args:
        string (str): The string to check.

    Returns:
        bool: True if the string has trailing spaces, False otherwise.
    """
    return string != string.rstrip()

def sort_data_structure_elements(obj):
    """
    Recursively sorts data structure elements:
    - dictionary keys if the type is a dictionary.
    - list elements if the type is a list.
    """
    if isinstance(obj, dict):
        return {k: sort_data_structure_elements(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        # Normalize each item in the list
        normalized_items = [sort_data_structure_elements(item) for item in obj]
        # Sort if the list is sortable (e.g., list of scalars or dicts with stable order)
        try:
            return sorted(normalized_items)
        except TypeError:
            # If not sortable (e.g., mix of dicts and lists), keep order
            return normalized_items
    else:
        return obj
