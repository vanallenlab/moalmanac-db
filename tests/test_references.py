import warnings

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
        f"  - Indication documents: {indication['reportedIn']}"
        )
        assert all(
            document_id in statement['reportedIn']
            for document_id in indication['reportedIn']
        ), error_message

def test_status_active_document_has_approved_or_accelerated_indication(data):
    """
    Ensures that every Active document has at least one Approved or Accelerated indication
    """
    for document in data['documents']:
        if document['status'] != 'Active':
            continue
        indications = [
            indication
            for indication in data['indications']
            if document['id'] in indication['reportedIn']
        ]
        if not any(i['status'] in ('Approved', 'Accelerated') for i in indications):
            error_message = (
            f"Active document has no Approved or Accelerated indication.\n"
            f"  - Document ID: {document['id']}\n"
            f"  - Indication statuses: {[i['status'] for i in indications]}"
            )
            pytest.fail(error_message)

def test_status_deprecated_document_has_only_withdrawn_or_superseded_indications(data):
    """
    Ensures that every indication associated with a Deprecated document is Withdrawn or Superseded
    """
    for document in data['documents']:
        if document['status'] != 'Deprecated':
            continue
        indications = [
            indication
            for indication in data['indications']
            if document['id'] in indication['reportedIn']
        ]
        for indication in indications:
            error_message = (
            f"Indication associated with a Deprecated document is not Withdrawn or Superseded.\n"
            f"  - Document ID: {document['id']}\n"
            f"  - Indication ID: {indication['id']}\n"
            f"  - Indication status: {indication['status']}"
            )
            assert indication['status'] in ('Withdrawn', 'Superseded'), error_message

def test_status_deprecated_document_has_only_deprecated_statements(data):
    """
    Ensures that every statement reporting a Deprecated document is Deprecated
    """
    deprecated_document_ids = {
        document['id']
        for document in data['documents']
        if document['status'] == 'Deprecated'
    }
    for statement in data['statements']:
        reported_deprecated_documents = deprecated_document_ids.intersection(
            statement['reportedIn']
        )
        if not reported_deprecated_documents:
            continue
        error_message = (
        f"Statement reporting a Deprecated document is not Deprecated.\n"
        f"  - Statement ID: {statement['id']}\n"
        f"  - Statement status: {statement.get('status')}\n"
        f"  - Deprecated documents: {reported_deprecated_documents}"
        )
        assert statement.get('status') == 'Deprecated', error_message

def test_status_approved_or_accelerated_indication_has_active_statement(data):
    """
    Ensures that every Approved or Accelerated indication with linked statements has at
    least one Active statement. Indications with no linked statements at all (e.g. a
    regulatory approval that has not yet been curated into a knowledge claim) are outside
    the scope of this check; those are surfaced as a warning instead of a failure.
    """
    unlinked_indication_ids = []
    for indication in data['indications']:
        if indication['status'] not in ('Approved', 'Accelerated'):
            continue
        statements = json_utils.get_records_by_key_value(
            records=data['statements'],
            key='indication_id',
            value=indication['id']
        )
        if not statements:
            unlinked_indication_ids.append(indication['id'])
            continue
        if not any(s.get('status') == 'Active' for s in statements):
            error_message = (
            f"{indication['status']} indication has no Active statement.\n"
            f"  - Indication ID: {indication['id']}\n"
            f"  - Statement statuses: {[s.get('status') for s in statements]}"
            )
            pytest.fail(error_message)

    if unlinked_indication_ids:
        warnings.warn(
            f"{len(unlinked_indication_ids)} Approved/Accelerated indication(s) have no "
            f"linked statements: {unlinked_indication_ids}",
            stacklevel=1,
        )

def test_status_withdrawn_indication_has_only_deprecated_statements(data):
    """
    Ensures that every statement associated with a Withdrawn indication is Deprecated
    """
    for indication in data['indications']:
        if indication['status'] != 'Withdrawn':
            continue
        statements = json_utils.get_records_by_key_value(
            records=data['statements'],
            key='indication_id',
            value=indication['id']
        )
        for statement in statements:
            error_message = (
            f"Statement associated with a Withdrawn indication is not Deprecated.\n"
            f"  - Indication ID: {indication['id']}\n"
            f"  - Statement ID: {statement['id']}\n"
            f"  - Statement status: {statement.get('status')}"
            )
            assert statement.get('status') == 'Deprecated', error_message

def test_status_superseded_indication_has_only_superseded_statements(data):
    """
    Ensures that every statement associated with a Superseded indication is Superseded
    """
    for indication in data['indications']:
        if indication['status'] != 'Superseded':
            continue
        statements = json_utils.get_records_by_key_value(
            records=data['statements'],
            key='indication_id',
            value=indication['id']
        )
        for statement in statements:
            error_message = (
            f"Statement associated with a Superseded indication is not Superseded.\n"
            f"  - Indication ID: {indication['id']}\n"
            f"  - Statement ID: {statement['id']}\n"
            f"  - Statement status: {statement.get('status')}"
            )
            assert statement.get('status') == 'Superseded', error_message
