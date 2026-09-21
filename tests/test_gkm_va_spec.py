import pydantic
import pytest
from ga4gh.va_spec.base.core import Agent
from ga4gh.va_spec.base.core import Contribution
from ga4gh.va_spec.base.core import Document
from ga4gh.va_spec.base.core import InformationEntity
from ga4gh.va_spec.base.core import Statement
from ga4gh.va_spec.base.core import VariantTherapeuticResponseProposition
from ga4gh.va_spec.base.domain_entities import TherapyGroup


def with_valid_subject_variant(proposition):
    """
    Return a copy of a proposition with its placeholder subjectVariant replaced.
    This is a place holder until Cat-VRS supports sets of categorical variants
    """
    return {
        **proposition,
        "subjectVariant": {
            "type": "CategoricalVariant",
            "name": "placeholder",
        },
    }


def test_agents(dereferenced_records):
    """
    Assess if agents are following VA-Spec schema for Agents
    """
    for agent in dereferenced_records["agents"]:
        try:
            Agent.model_validate(agent)
        except pydantic.ValidationError as e:
            error_message = (
                f"Agent failed to validate against VA-Spec:\n"
                f"{agent}\n"
                f"Validation error:{e}"
            )
            pytest.fail(error_message)


def test_contributions(dereferenced_records):
    """
    Assess if contributions are following VA-Spec schema for Contributions
    """
    for contribution in dereferenced_records["contributions"]:
        try:
            Contribution.model_validate(contribution)
        except pydantic.ValidationError as e:
            error_message = (
                f"Contribution failed to validate against VA-Spec:\n"
                f"{contribution}\n"
                f"Validation error: {e}"
            )
            pytest.fail(error_message)


def test_documents(dereferenced_records):
    """
    Assess if documents are following VA-Spec schema for Documents
    """
    for document in dereferenced_records["documents"]:
        try:
            Document.model_validate(document)
        except pydantic.ValidationError as e:
            error_message = (
                f"Document failed to validate against VA-Spec:\n"
                f"{document}\n"
                f"Validation error: {e}"
            )
            pytest.fail(error_message)


def test_indications(dereferenced_records):
    """
    Assess if indications are following the VA-Spec schema for Information Entity
    """
    for indication in dereferenced_records["indications"]:
        try:
            InformationEntity.model_validate(indication)
        except pydantic.ValidationError as e:
            error_message = (
                f"Indication failed to validate against VA-Spec:\n"
                f"{indication}\n"
                f"Validation error: {e}"
            )
            pytest.fail(error_message)


def test_therapeutic_response_propositions(dereferenced_records):
    """
    Assess if therapy response propositions are following VA-Spec schema for Therapeutic Response Proposition
    """
    for proposition in dereferenced_records["propositions"]:
        try:
            VariantTherapeuticResponseProposition.model_validate(
                with_valid_subject_variant(proposition)
            )
        except pydantic.ValidationError as e:
            error_message = (
                f"Proposition failed to validate against VA-Spec:\n"
                f"{proposition}\n"
                f"Validation error: {e}"
            )
            pytest.fail(error_message)


def test_statements(dereferenced_records):
    """
    Assess if statements are following the VA-Spec schema for Statements
    """
    for statement in dereferenced_records["statements"]:
        record = {
            **statement,
            "proposition": with_valid_subject_variant(statement["proposition"]),
        }
        try:
            Statement.model_validate(record)
        except pydantic.ValidationError as e:
            error_message = (
                f"Statement failed to validate against VA-Spec:\n"
                f"{statement}\n"
                f"Validation error: {e}"
            )
            pytest.fail(error_message)


def test_therapy_groups(dereferenced_records):
    """
    Assess if therapy groups are following the VA-Spec schema for Therapy Groups
    """
    for therapy_group in dereferenced_records["therapy_groups"]:
        try:
            TherapyGroup.model_validate(therapy_group)
        except pydantic.ValidationError as e:
            error_message = (
                f"Therapy Group failed to validate against VA-Spec:\n"
                f"{therapy_group}\n"
                f"Validation error: {e}"
            )
            pytest.fail(error_message)
