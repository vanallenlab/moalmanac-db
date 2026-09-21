import pydantic
import pytest
from ga4gh.cat_vrs.models import CategoricalVariant

# Constraint types that are not yet modeled in cat-vrs-python (ga4gh.cat-vrs==0.7.2). These are removed
# from biomarkers before validating, so the remaining constraints are still checked.
UNSUPPORTED_CONSTRAINT_TYPES = {"AdjacencyConstraint", "FunctionConstraint"}


def without_unsupported_constraints(biomarker):
    """Return a copy of the biomarker without constraints that Cat-VRS does not yet model."""
    return {
        **biomarker,
        "constraints": [
            constraint
            for constraint in biomarker.get("constraints", [])
            if constraint["type"] not in UNSUPPORTED_CONSTRAINT_TYPES
        ],
    }


def test_categorical_variants(dereferenced_records):
    """
    Assess if categorical variants are following Cat-VRS schema for Biomarkers
    """
    for biomarker in dereferenced_records["biomarkers"]:
        try:
            CategoricalVariant.model_validate(
                without_unsupported_constraints(biomarker)
            )
        except pydantic.ValidationError as e:
            error_message = (
                f"Biomarker failed to validate against Cat-VRS:\n"
                f"{biomarker}\n"
                f"Validation error:{e}"
            )
            pytest.fail(error_message)
