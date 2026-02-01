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
