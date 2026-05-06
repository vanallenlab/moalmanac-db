import json

from tests import helpers


def test_unique_ids_per_file(data):
    """
    Ensures that all id values per file are unique.
    """
    for file, records in data.items():
        seen = set()
        duplicates = []
        for record in records:
            record_id = record.get("id")
            if record_id in seen:
                duplicates.append(record_id)
            else:
                seen.add(record_id)

        assert not duplicates, (
            f"Duplicate `id` values found in table '{file}': {duplicates}"
        )


def test_unique_records_per_file(data):
    """
    Ensures that all records per file are unique.
    """
    for file, records in data.items():
        seen = {}
        duplicates = []
        for record in records:
            record_copy = {k: v for k, v in record.items() if k != "id"}
            normalized = helpers.sort_data_structure_elements(record_copy)
            serialized = json.dumps(normalized, sort_keys=True)

            if serialized in seen:
                duplicates.append((seen[serialized], record.get("id")))
            else:
                seen[serialized] = record.get("id")
        assert not duplicates, (
            f"Duplicate records found in file {file} (ignoring `id`): "
            f"{[f'{a} and {b}' for a, b in duplicates]}"
        )
