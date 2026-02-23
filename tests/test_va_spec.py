import pydantic
import pytest

from ga4gh.va_spec.base.core import Agent, Document


def test_agents(dereferenced_records):
    """
    Assess if agents are following VA-Spec schema
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

def test_documents(dereferenced_records):
    """
    Assess if documents are following VA-Spec schema
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
