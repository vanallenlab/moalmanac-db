import pydantic
import pytest
from ga4gh.core.models import Coding
from ga4gh.core.models import ConceptMapping
from ga4gh.core.models import MappableConcept


def test_codings(dereferenced_records):
    """
    Assess if codings are following GKM Core schema for Codings
    """
    for coding in dereferenced_records["codings"]:
        try:
            Coding.model_validate(coding)
        except pydantic.ValidationError as e:
            error_message = (
                f"Coding failed to validate against GKM Core:\n"
                f"{coding}\n"
                f"Validation error:{e}"
            )
            pytest.fail(error_message)


def test_diseases(dereferenced_records):
    """
    Assess if diseases are following GKM Core schema for Mappable Concepts
    """
    for disease in dereferenced_records["diseases"]:
        try:
            MappableConcept.model_validate(disease)
        except pydantic.ValidationError as e:
            error_message = (
                f"Disease failed to validate against GKM Core:\n"
                f"{disease}\n"
                f"Validation error:{e}"
            )
            pytest.fail(error_message)

def test_genes(dereferenced_records):
    """
    Assess if genes are following GKM Core schema for Mappable Concepts
    """
    for gene in dereferenced_records["genes"]:
        try:
            MappableConcept.model_validate(gene)
        except pydantic.ValidationError as e:
            error_message = (
                f"Gene failed to validate against GKM Core:\n"
                f"{gene}\n"
                f"Validation error:{e}"
            )
            pytest.fail(error_message)


def test_mappings(dereferenced_records):
    """
    Assess if mappings are following GKM Core schema for Concept Mappings
    """
    for mapping in dereferenced_records["mappings"]:
        # primary_coding_id is the join table's foreign key, not part of the GKM schema
        record = {k: v for k, v in mapping.items() if k != "primary_coding_id"}
        try:
            ConceptMapping.model_validate(record)
        except pydantic.ValidationError as e:
            error_message = (
                f"Mapping failed to validate against GKM Core:\n"
                f"{mapping}\n"
                f"Validation error:{e}"
            )
            pytest.fail(error_message)


def test_therapies(dereferenced_records):
    """
    Assess if therapies are following GKM Core schema for Mappable Concepts
    """
    for therapy in dereferenced_records["therapies"]:
        try:
            MappableConcept.model_validate(therapy)
        except pydantic.ValidationError as e:
            error_message = (
                f"Therapy failed to validate against GKM Core:\n"
                f"{therapy}\n"
                f"Validation error:{e}"
            )
            pytest.fail(error_message)
