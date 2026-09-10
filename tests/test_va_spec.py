import pydantic
import pytest
from ga4gh.va_spec.base.core import Agent
from ga4gh.va_spec.base.core import Contribution
from ga4gh.va_spec.base.core import Document
from ga4gh.va_spec.base.core import InformationEntity


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
