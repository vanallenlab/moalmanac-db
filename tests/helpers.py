def has_trailing_spaces(string: str) -> bool:
    """
    Checks if a string has trailing spaces.

    Args:
        string (str): The string to check.

    Returns:
        bool: True if the string has trailing spaces, False otherwise.
    """
    return string != string.rstrip()

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
