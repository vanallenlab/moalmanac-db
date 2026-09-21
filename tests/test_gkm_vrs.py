import pydantic
import pytest
from ga4gh.vrs.models import Allele
from ga4gh.vrs.models import SequenceLocation
from ga4gh.vrs.models import SequenceReference


def test_alleles(dereferenced_records):
    """
    Assess if alleles are following VRS schema for Alleles
    """
    for allele in dereferenced_records["alleles"]:
        try:
            Allele.model_validate(allele)
        except pydantic.ValidationError as e:
            error_message = (
                f"Allele failed to validate against VRS:\n"
                f"{allele}\n"
                f"Validation error:{e}"
            )
            pytest.fail(error_message)


def test_sequence_locations(dereferenced_records):
    """
    Assess if sequence locations are following VRS schema for Sequence Locations
    """
    for sequence_location in dereferenced_records["sequence_locations"]:
        try:
            SequenceLocation.model_validate(sequence_location)
        except pydantic.ValidationError as e:
            error_message = (
                f"Sequence Location failed to validate against VRS:\n"
                f"{sequence_location}\n"
                f"Validation error:{e}"
            )
            pytest.fail(error_message)


def test_sequence_references(dereferenced_records):
    """
    Assess if sequence references are following VRS schema for Sequence References
    """
    for sequence_reference in dereferenced_records["sequence_references"]:
        try:
            SequenceReference.model_validate(sequence_reference)
        except pydantic.ValidationError as e:
            error_message = (
                f"Sequence Reference failed to validate against VRS:\n"
                f"{sequence_reference}\n"
                f"Validation error:{e}"
            )
            pytest.fail(error_message)
