import pytest

from utils import json_utils

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

def test_associated_indication_ids_are_valid(data):
    """
    Ensures that the indication_id associated with each statement is valid
    """
    for statement in data['statements']:
        matched_indications = json_utils.get_records_by_key_value(
            records=data['indications'],
            key='id',
            value=statement['indication_id']
        )
        if len(matched_indications) != 1:
            error_message = (
            f"Indication id associated with statement does not exist.\n"
            f"  - Statement ID: {statement['id']}"
            )
            pytest.fail(error_message)

def test_no_mismatch_between_document_for_indication_and_statement(data):
    """
    Assess if document associated with indications and associated statements differ
    """
    for statement in data['statements']:
        statement_docs = statement['reportedIn']
        matched_indications = json_utils.get_records_by_key_value(
            records=data['indications'],
            key='id',
            value=statement['indication_id']
        )
        indication = matched_indications[0]
        error_message = (
        f"Document mismatch between statement and indication:\n"
        f"  - Statement ID: {statement['id']}\n"
        f"  - Indication ID: {indication['id']}\n"
        f"  - Statement documents: {statement_docs}\n"
        f"  - Indication document: {indication['document_id']}"
        )
        assert indication['document_id'] in statement['reportedIn'], error_message
