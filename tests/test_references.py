import pytest

from utils import json_utils

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
