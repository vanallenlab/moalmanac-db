import pydantic
import pytest
from ga4gh.cat_vrs.models import CategoricalVariant

# Biomarker types that are not yet expressible in Cat-VRS and are not validated
SKIP_BIOMARKER_TYPES = [
    "Rearrangement"
]


def biomarker_type(biomarker):
    """Return the value of the `biomarker_type` extension, or None if absent."""
    for extension in biomarker.get("extensions", []):
        if extension["name"] == "biomarker_type":
            return extension["value"]
    return None


def test_categorical_variants(dereferenced_records):
    """
    Assess if categorical variants are following Cat-VRS schema for Biomarkers
    """
    for biomarker in dereferenced_records["biomarkers"]:
        if biomarker_type(biomarker) in SKIP_BIOMARKER_TYPES:
            continue
        try:
            CategoricalVariant.model_validate(biomarker)
        except pydantic.ValidationError as e:
            error_message = (
                f"Biomarker failed to validate against Cat-VRS:\n"
                f"{biomarker}\n"
                f"Validation error:{e}"
            )
            pytest.fail(error_message)
