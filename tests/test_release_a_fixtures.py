"""
Worked examples for schema release A: journal article documents, journal statements
without an indication, resistance, prognosis and a `disputes` statement.

The fixtures in `tests/fixtures/release-a/` hold new records only. They are laid over the
referenced tables in memory, validated against the referenced schemas, dereferenced, and
validated against the dereferenced schemas and the GA4GH models. Nothing is written to
`referenced/` or `dereferenced/`.

The resistance and prognosis examples are v1 records that the 2026-10-15 fact-check
judged supported. `stmt:pmid:21098728:1` is synthetic and exists only to exercise
`direction: disputes`.
"""

import copy
import dataclasses
import json
import pathlib

import pytest
from ga4gh.va_spec.base.core import Document
from ga4gh.va_spec.base.core import Statement
from referencing import Registry
from referencing import Resource
from referencing.jsonschema import DRAFT202012

from tests import test_gkm_va_spec
from tests import test_schemas
from utils import dereference

FIXTURE_ROOT = pathlib.Path("tests") / "fixtures" / "release-a"


def check(tree, name, records, registry):
    """Returns the validation failures of `records` against one schema."""
    return test_schemas.failures(test_schemas.validator(tree, name, registry), records)


def fixture_ids(fixtures, name):
    return {record["id"] for record in fixtures[name]}


@pytest.fixture(scope="module")
def fixtures():
    return {
        path.stem: json.loads(path.read_text())
        for path in sorted(FIXTURE_ROOT.glob("*.json"))
    }


@pytest.fixture(scope="module")
def registry():
    resources = [
        (schema["$id"], Resource(schema, DRAFT202012))
        for schema in (
            test_schemas.load_schema(path)
            for tree in ("referenced", "dereferenced")
            for path in test_schemas.schema_paths(tree)
        )
    ]
    return Registry().with_resources(resources)


@pytest.fixture(scope="module")
def dereferenced(data, fixtures):
    """
    The referenced tables with the fixtures laid over them, dereferenced in memory.
    Returns the Database, whose tables hold dereferenced records.
    """
    tables = {}
    for field in dataclasses.fields(dereference.Database):
        records = copy.deepcopy(data[field.name])
        records.extend(copy.deepcopy(fixtures.get(field.name, [])))
        tables[field.name] = getattr(dereference, field.type)(records=records)
    db = dereference.Database(**tables)
    for field in dataclasses.fields(dereference.Database):
        getattr(db, field.name).dereference(db)
    return db


def select(db, fixtures, name):
    ids = fixture_ids(fixtures, name)
    return [r for r in getattr(db, name).records if r["id"] in ids]


def test_fixture_ids_do_not_collide_with_referenced_records(data, fixtures):
    for name, records in fixtures.items():
        existing = {record["id"] for record in data[name]}
        clash = existing & {record["id"] for record in records}
        assert not clash, f"{name}: fixture ids already in referenced/: {clash}"


@pytest.mark.parametrize(
    "name",
    sorted(path.stem for path in FIXTURE_ROOT.glob("*.json")),
)
def test_fixtures_match_referenced_schema(name, fixtures, registry):
    bad = check("referenced", name, fixtures[name], registry)
    assert not bad, bad


@pytest.mark.parametrize("name", ["documents", "propositions", "statements"])
def test_fixtures_match_dereferenced_schema(name, dereferenced, fixtures, registry):
    records = select(dereferenced, fixtures, name)
    assert len(records) == len(fixtures[name])
    bad = check("dereferenced", name, records, registry)
    assert not bad, bad


def test_fixtures_match_va_spec(dereferenced, fixtures):
    for document in select(dereferenced, fixtures, "documents"):
        Document.model_validate(document)
    for proposition in select(dereferenced, fixtures, "propositions"):
        test_gkm_va_spec.PROPOSITION_MODELS[proposition["type"]].model_validate(
            test_gkm_va_spec.with_valid_subject_variant(proposition)
        )
    for statement in select(dereferenced, fixtures, "statements"):
        Statement.model_validate(
            {
                **statement,
                "proposition": test_gkm_va_spec.with_valid_subject_variant(
                    statement["proposition"]
                ),
            }
        )


def test_journal_article_has_no_regulatory_fields(dereferenced, fixtures, registry):
    """
    Ensures a journal article is rejected if it carries a regulatory-only key, and that
    its dereferenced form has only the `publication_date` and `status` extensions.
    """
    article = fixtures["documents"][0]
    for key in (
        "agent_id",
        "company",
        "drug_name_brand",
        "drug_name_generic",
        "first_publication_date",
        "regulatory_identifier",
    ):
        assert check("referenced", "documents", [{**article, key: None}], registry)
    for key, value in (("pmid", None), ("title", None), ("id", "doc:fda:21098728")):
        assert check("referenced", "documents", [{**article, key: value}], registry)

    for document in select(dereferenced, fixtures, "documents"):
        names = [extension["name"] for extension in document["extensions"]]
        assert names == ["publication_date", "status"], document["id"]


def test_journal_statement_has_no_indication(data, dereferenced, fixtures, registry):
    """
    Ensures a journal statement is rejected with an `indication_id`, a regulatory
    statement is rejected without one, and a dereferenced journal statement has no
    `indication` extension.
    """
    journal = fixtures["statements"][0]
    indication_id = data["statements"][0]["indication_id"]
    assert check(
        "referenced",
        "statements",
        [{**journal, "indication_id": indication_id}],
        registry,
    )
    regulatory = copy.deepcopy(data["statements"][0])
    del regulatory["indication_id"]
    assert check("referenced", "statements", [regulatory], registry)

    for statement in select(dereferenced, fixtures, "statements"):
        names = [extension["name"] for extension in statement["extensions"]]
        assert names == ["status"], statement["id"]


def test_proposition_keys_follow_type(fixtures, registry):
    """
    Ensures each proposition type carries only its own object and qualifier keys and
    its own predicates.
    """
    by_type = {record["type"]: record for record in fixtures["propositions"]}
    therapeutic = by_type["VariantTherapeuticResponseProposition"]
    prognostic = by_type["VariantPrognosticProposition"]

    def bad(record):
        return check("referenced", "propositions", [record], registry)

    assert bad({**prognostic, "therapy_id": therapeutic["therapy_id"]})
    assert bad({**prognostic, "conditionQualifier_id": "dis:ncit:C2919"})
    assert bad({**prognostic, "predicate": "predictsResistanceTo"})
    assert bad({**prognostic, "id": "prop:vtxr:9001"})
    assert not bad({**prognostic, "predicate": "associatedWithBetterOutcomeFor"})

    assert bad({**therapeutic, "objectCondition_id": "dis:ncit:C2919"})
    assert bad({**therapeutic, "predicate": "associatedWithWorseOutcomeFor"})
    assert bad({**therapeutic, "therapy_group_id": "txgrp:0"})
    assert not bad({**therapeutic, "predicate": "predictsSensitivityTo"})


def test_statement_directions(fixtures):
    directions = {record["direction"] for record in fixtures["statements"]}
    assert directions == {"supports", "disputes"}
