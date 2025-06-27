import json

from tests import helpers

def test_document_url_matches_citation(data):
    """
    Assess if `url` field matches the url contained in the `citation` for documents where the url should be
    contained within the citation. Currently, this is relevant for documents where the subtype is one of the
    following values:
        - Regulatory approval

    For example, the citation for the FDA's package insert for Keytruda is,
    "Merck Sharp & Dohme Corp. Keytruda (pembrolizumab) [package insert]. U.S. Food and Drug Administration website.
    https://www.accessdata.fda.gov/drugsatfda_docs/label/2025/125514s174lbl.pdf. Revised April 2025.
    Accessed April 30, 2025."

    We want to make sure that the url, added to the `url` field of the document's record, matches the
    one contained within the citation string.
    """
    relevant_subtypes = ['Regulatory approval']
    relevant_records = [r for r in data['documents'] if r['subtype'] in relevant_subtypes]
    failed_records = [r for r in relevant_records if r['url'] not in r['citation']]
    error_message = f"Provided url not contained in citation for documents: {[r['id'] for r in failed_records]}"
    assert not failed_records, error_message

def test_unique_ids_per_file(data):
    """
    Ensures that all id values per file are unique.
    """
    for file, records in data.items():
        seen = set()
        duplicates = []
        for record in records:
            record_id = record.get('id')
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
                duplicates.append((seen[serialized], record.get('id')))
            else:
                seen[serialized] = record.get('id')
        assert not duplicates, (
            f"Duplicate records found in file {file} (ignoring `id`): "
            f"{[f'{a} and {b}' for a, b in duplicates]}"
        )
