import warnings

import pytest

from utils import json_utils


def test_associated_indication_ids_are_valid(data):
    """
    Ensures that the indication_id associated with each statement is valid
    """
    for statement in data["statements"]:
        matched_indications = json_utils.get_records_by_key_value(
            records=data["indications"], key="id", value=statement["indication_id"]
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
    for statement in data["statements"]:
        statement_docs = statement["reportedIn"]
        matched_indications = json_utils.get_records_by_key_value(
            records=data["indications"], key="id", value=statement["indication_id"]
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
            document_id in statement["reportedIn"]
            for document_id in indication["reportedIn"]
        ), error_message


def test_status_active_document_has_approved_or_accelerated_indication(data):
    """
    Ensures that every Active document has at least one Approved or Accelerated indication
    """
    for document in data["documents"]:
        if document["status"] != "Active":
            continue
        indications = [
            indication
            for indication in data["indications"]
            if document["id"] in indication["reportedIn"]
        ]
        if not any(i["status"] in ("Approved", "Accelerated") for i in indications):
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
    for document in data["documents"]:
        if document["status"] != "Deprecated":
            continue
        indications = [
            indication
            for indication in data["indications"]
            if document["id"] in indication["reportedIn"]
        ]
        for indication in indications:
            error_message = (
                f"Indication associated with a Deprecated document is not Withdrawn or Superseded.\n"
                f"  - Document ID: {document['id']}\n"
                f"  - Indication ID: {indication['id']}\n"
                f"  - Indication status: {indication['status']}"
            )
            assert indication["status"] in ("Withdrawn", "Superseded"), error_message


def test_status_deprecated_document_has_only_deprecated_statements(data):
    """
    Ensures that every statement reporting a Deprecated document is Deprecated
    """
    deprecated_document_ids = {
        document["id"]
        for document in data["documents"]
        if document["status"] == "Deprecated"
    }
    for statement in data["statements"]:
        reported_deprecated_documents = deprecated_document_ids.intersection(
            statement["reportedIn"]
        )
        if not reported_deprecated_documents:
            continue
        error_message = (
            f"Statement reporting a Deprecated document is not Deprecated.\n"
            f"  - Statement ID: {statement['id']}\n"
            f"  - Statement status: {statement.get('status')}\n"
            f"  - Deprecated documents: {reported_deprecated_documents}"
        )
        assert statement.get("status") == "Deprecated", error_message


def test_status_approved_or_accelerated_indication_has_active_statement(data):
    """
    Ensures that every Approved or Accelerated indication with linked statements has at
    least one Active statement. Indications with no linked statements at all (e.g. a
    regulatory approval that has not yet been curated into a knowledge claim) are outside
    the scope of this check; those are surfaced as a warning instead of a failure.
    """
    unlinked_indication_ids = []
    for indication in data["indications"]:
        if indication["status"] not in ("Approved", "Accelerated"):
            continue
        statements = json_utils.get_records_by_key_value(
            records=data["statements"], key="indication_id", value=indication["id"]
        )
        if not statements:
            unlinked_indication_ids.append(indication["id"])
            continue
        if not any(s.get("status") == "Active" for s in statements):
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
    for indication in data["indications"]:
        if indication["status"] != "Withdrawn":
            continue
        statements = json_utils.get_records_by_key_value(
            records=data["statements"], key="indication_id", value=indication["id"]
        )
        for statement in statements:
            error_message = (
                f"Statement associated with a Withdrawn indication is not Deprecated.\n"
                f"  - Indication ID: {indication['id']}\n"
                f"  - Statement ID: {statement['id']}\n"
                f"  - Statement status: {statement.get('status')}"
            )
            assert statement.get("status") == "Deprecated", error_message


def test_status_superseded_indication_has_only_superseded_statements(data):
    """
    Ensures that every statement associated with a Superseded indication is Superseded
    """
    for indication in data["indications"]:
        if indication["status"] != "Superseded":
            continue
        statements = json_utils.get_records_by_key_value(
            records=data["statements"], key="indication_id", value=indication["id"]
        )
        for statement in statements:
            error_message = (
                f"Statement associated with a Superseded indication is not Superseded.\n"
                f"  - Indication ID: {indication['id']}\n"
                f"  - Statement ID: {statement['id']}\n"
                f"  - Statement status: {statement.get('status')}"
            )
            assert statement.get("status") == "Superseded", error_message


def test_biomarker_gene_ids_resolve(data):
    """
    Ensures every id in a biomarker's `genes` resolves to a record in genes.json
    """
    for biomarker in data["biomarkers"]:
        for gene_id in biomarker["genes"]:
            matched = json_utils.get_records_by_key_value(
                records=data["genes"], key="id", value=gene_id
            )
            error_message = (
                f"Biomarker gene id does not resolve to a gene record.\n"
                f"  - Biomarker ID: {biomarker['id']}\n"
                f"  - Gene ID: {gene_id}"
            )
            assert len(matched) == 1, error_message


def test_biomarker_copy_change_ids_resolve(data):
    """
    Ensures every non-null biomarker `copyChange` resolves to a record in copy_changes.json
    """
    for biomarker in data["biomarkers"]:
        copy_change_id = biomarker["copyChange"]
        if copy_change_id is None:
            continue
        matched = json_utils.get_records_by_key_value(
            records=data["copy_change"], key="id", value=copy_change_id
        )
        error_message = (
            f"Biomarker copyChange id does not resolve to a copy_change record.\n"
            f"  - Biomarker ID: {biomarker['id']}\n"
            f"  - CopyChange ID: {copy_change_id}"
        )
        assert len(matched) == 1, error_message


def test_biomarker_function_ids_resolve(data):
    """
    Ensures every non-null biomarker `function` resolves to a record in function_consequences.json
    """
    for biomarker in data["biomarkers"]:
        function_id = biomarker["function"]
        if function_id is None:
            continue
        matched = json_utils.get_records_by_key_value(
            records=data["function_consequences"], key="id", value=function_id
        )
        error_message = (
            f"Biomarker function id does not resolve to a function_consequences record.\n"
            f"  - Biomarker ID: {biomarker['id']}\n"
            f"  - Function ID: {function_id}"
        )
        assert len(matched) == 1, error_message


def test_function_consequence_primary_coding_ids_resolve(data):
    """
    Ensures every function consequence `primary_coding_id` resolves to a record in codings.json
    """
    for function_consequence in data["function_consequences"]:
        coding_id = function_consequence["primary_coding_id"]
        matched = json_utils.get_records_by_key_value(
            records=data["codings"], key="id", value=coding_id
        )
        error_message = (
            f"Function consequence primary_coding_id does not resolve to a coding record.\n"
            f"  - Function consequence ID: {function_consequence['id']}\n"
            f"  - Coding ID: {coding_id}"
        )
        assert len(matched) == 1, error_message


def test_biomarker_allele_ids_resolve(data):
    """
    Ensures every non-null biomarker `allele` resolves to a record in alleles.json
    """
    for biomarker in data["biomarkers"]:
        allele_id = biomarker["allele"]
        if allele_id is None:
            continue
        matched = json_utils.get_records_by_key_value(
            records=data["alleles"], key="id", value=allele_id
        )
        error_message = (
            f"Biomarker allele id does not resolve to an allele record.\n"
            f"  - Biomarker ID: {biomarker['id']}\n"
            f"  - Allele ID: {allele_id}"
        )
        assert len(matched) == 1, error_message


def test_biomarker_location_ids_resolve(data):
    """
    Ensures every non-null biomarker `location` resolves to a record in sequence_locations.json
    """
    for biomarker in data["biomarkers"]:
        location_id = biomarker["location"]
        if location_id is None:
            continue
        matched = json_utils.get_records_by_key_value(
            records=data["sequence_locations"], key="id", value=location_id
        )
        error_message = (
            f"Biomarker location id does not resolve to a sequence_location record.\n"
            f"  - Biomarker ID: {biomarker['id']}\n"
            f"  - Location ID: {location_id}"
        )
        assert len(matched) == 1, error_message


def test_allele_location_ids_resolve(data):
    """
    Ensures every allele's `location` resolves to a record in sequence_locations.json
    """
    for allele in data["alleles"]:
        matched = json_utils.get_records_by_key_value(
            records=data["sequence_locations"], key="id", value=allele["location"]
        )
        error_message = (
            f"Allele location id does not resolve to a sequence_location record.\n"
            f"  - Allele ID: {allele['id']}\n"
            f"  - Location ID: {allele['location']}"
        )
        assert len(matched) == 1, error_message


def test_sequence_location_reference_ids_resolve(data):
    """
    Ensures every sequence_location's `sequenceReference` resolves to a record in sequence_references.json
    """
    for sequence_location in data["sequence_locations"]:
        matched = json_utils.get_records_by_key_value(
            records=data["sequence_references"],
            key="id",
            value=sequence_location["sequenceReference"],
        )
        error_message = (
            f"SequenceLocation sequenceReference id does not resolve to a sequence_reference record.\n"
            f"  - SequenceLocation ID: {sequence_location['id']}\n"
            f"  - SequenceReference ID: {sequence_location['sequenceReference']}"
        )
        assert len(matched) == 1, error_message


def test_gene_transcript_exon_ids_resolve(data):
    """
    Ensures every gene's `transcript_exons` ids resolve to records in sequence_locations.json
    """
    for gene in data["genes"]:
        for exon_id in gene["transcript_exons"]:
            matched = json_utils.get_records_by_key_value(
                records=data["sequence_locations"], key="id", value=exon_id
            )
            error_message = (
                f"Gene transcript_exons id does not resolve to a sequence_location record.\n"
                f"  - Gene ID: {gene['id']}\n"
                f"  - SequenceLocation ID: {exon_id}"
            )
            assert len(matched) == 1, error_message


def test_gene_protein_product_exon_ids_resolve(data):
    """
    Ensures every gene's `protein_product_exons` ids resolve to records in sequence_locations.json
    """
    for gene in data["genes"]:
        for exon_id in gene["protein_product_exons"]:
            matched = json_utils.get_records_by_key_value(
                records=data["sequence_locations"], key="id", value=exon_id
            )
            error_message = (
                f"Gene protein_product_exons id does not resolve to a sequence_location record.\n"
                f"  - Gene ID: {gene['id']}\n"
                f"  - SequenceLocation ID: {exon_id}"
            )
            assert len(matched) == 1, error_message
