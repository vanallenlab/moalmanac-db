import pydantic
import pytest

from ga4gh.va_spec.base.core import Agent


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


def test_organizations(dereferenced_records):
    """
    Assess if organizations are following VA-Spec schema
    """
    for organization in dereferenced_records["organizations"]:
        try:
            Agent.model_validate(organization)
        except pydantic.ValidationError as e:
            error_message = (
                f"Organization failed to validate against VA-Spec:\n"
                f"{organization}\n"
                f"Validation error:{e}"
            )
            pytest.fail(error_message)
