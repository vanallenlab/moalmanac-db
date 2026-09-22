import copy
import json
import pathlib

import jsonschema
import pytest
from referencing import Registry
from referencing import Resource
from referencing.jsonschema import DRAFT202012

SCHEMA_ROOT = pathlib.Path("schemas")
REFERENCED_ROOT = pathlib.Path("referenced")
DEREFERENCED_ROOT = pathlib.Path("dereferenced")


def extension_value(record, name):
    return next(e["value"] for e in record["extensions"] if e["name"] == name)


def failures(validator_, records):
    """Returns `id: message` for each record that fails validation."""
    out = []
    for record in records:
        error = jsonschema.exceptions.best_match(validator_.iter_errors(record))
        if error is not None:
            path = "/".join(str(p) for p in error.absolute_path)
            out.append(f"{record.get('id')}: {error.message[:200]} (at {path})")
    return out


def first_record(data, key, predicate):
    return copy.deepcopy(next(r for r in data[key] if predicate(r)))


def load_schema(path):
    return json.loads(path.read_text())


@pytest.fixture(scope="module")
def registry():
    """
    Registry of every schema under schemas/, keyed by `$id`, so relative `$ref`s
    resolve locally.
    """
    resources = [
        (schema["$id"], Resource(schema, DRAFT202012))
        for schema in (
            load_schema(path)
            for tree in ("referenced", "dereferenced")
            for path in schema_paths(tree)
        )
    ]
    return Registry().with_resources(resources)


def schema_paths(tree):
    return sorted((SCHEMA_ROOT / tree).glob("*.schema.json"))


def assert_required_shape(schema, record):
    """
    Asserts a record has every required top-level key and every expected extension name,
    without validating the contents of `$ref`-based fields or extension values.
    """
    missing_keys = set(schema["required"]) - record.keys()
    assert not missing_keys, f"{record.get('id')} missing keys: {missing_keys}"
    expected_extensions = {
        branch["properties"]["name"]["const"]
        for branch in schema["properties"]["extensions"]["items"]["anyOf"]
    }
    extension_names = {e["name"] for e in record["extensions"]}
    missing_extensions = expected_extensions - extension_names
    assert not missing_extensions, (
        f"{record.get('id')} missing extensions: {missing_extensions}"
    )


def test_allele_length_fields_follow_state_type(data, registry):
    """
    Ensures referenced allele length fields are set only for a ReferenceLengthExpression.
    """
    check = validator("referenced", "alleles", registry)
    literal = first_record(
        data, "alleles", lambda r: r["state_type"] == "LiteralSequenceExpression"
    )
    literal["state_length"] = 3
    assert failures(check, [literal])

    repeat = first_record(
        data, "alleles", lambda r: r["state_type"] == "ReferenceLengthExpression"
    )
    assert not failures(check, [repeat])
    repeat["state_length"] = None
    assert failures(check, [repeat])


def test_biomarker_extensions_must_match_type(data, registry):
    """
    Ensures a biomarker missing a required extension for its type, or carrying an extension
    belonging to another type, fails.
    """
    check = validator("referenced", "biomarkers", registry)
    somatic = first_record(
        data,
        "biomarkers",
        lambda r: r["biomarker_type"] == "Somatic variant",
    )
    missing = copy.deepcopy(somatic)
    missing["extensions"] = [e for e in missing["extensions"] if e["name"] != "exon"]
    assert failures(check, [missing])

    extra = copy.deepcopy(somatic)
    extra["extensions"].append({"name": "marker", "value": "PD-L1"})
    assert failures(check, [extra])


def test_dereferenced_allele_state_matches_its_type(registry):
    """
    Ensures a dereferenced allele state carries exactly the fields of its state type.
    """
    check = validator("dereferenced", "alleles", registry)
    records = [
        json.loads(path.read_text())
        for path in (DEREFERENCED_ROOT / "alleles").glob("*.json")
    ]
    literal = copy.deepcopy(
        next(r for r in records if r["state"]["type"] == "LiteralSequenceExpression")
    )
    literal["state"]["length"] = 3
    assert failures(check, [literal])

    repeat = copy.deepcopy(
        next(r for r in records if r["state"]["type"] == "ReferenceLengthExpression")
    )
    assert not failures(check, [repeat])
    del repeat["state"]["length"]
    assert failures(check, [repeat])


def test_dereferenced_propositions():
    """
    Ensures dereferenced propositions have their required keys and a `biomarkers`
    extension, without revalidating nested biomarkers/diseases/therapies — those are
    covered by their own dereferenced schemas and by test_references.py's foreign-key
    checks.
    """
    schema = load_schema(SCHEMA_ROOT / "dereferenced" / "propositions.schema.json")
    files = sorted((DEREFERENCED_ROOT / "propositions").glob("*.json"))
    assert files, "No dereferenced files found for propositions"
    for path in files:
        assert_required_shape(schema, json.loads(path.read_text()))


@pytest.mark.parametrize(
    "name",
    sorted(
        p.stem.removesuffix(".schema")
        for p in schema_paths("dereferenced")
        if p.stem
        not in ("extension.schema", "propositions.schema", "statements.schema")
    ),
)
def test_dereferenced_records_match_schema(name, registry):
    """
    Ensures every file in a dereferenced/<entity>/ directory validates against its schema.
    """
    files = sorted((DEREFERENCED_ROOT / name).glob("*.json"))
    assert files, f"No dereferenced files found for {name}"
    records = [json.loads(path.read_text()) for path in files]
    bad = failures(validator("dereferenced", name, registry), records)
    assert not bad, f"{len(bad)} invalid {name} records, e.g. {bad[:3]}"


def test_dereferenced_statements():
    """
    Ensures dereferenced statements have their required keys and `status`/`indication`
    extensions, without revalidating nested contributions/documents/proposition/strength
    or the indication's contents — those are covered by their own dereferenced schemas
    and by test_references.py's foreign-key checks.
    """
    schema = load_schema(SCHEMA_ROOT / "dereferenced" / "statements.schema.json")
    files = sorted((DEREFERENCED_ROOT / "statements").glob("*.json"))
    assert files, "No dereferenced files found for statements"
    for path in files:
        assert_required_shape(schema, json.loads(path.read_text()))


def test_document_dates_must_be_iso_dates_or_null(data, registry):
    """
    Ensures document dates are ISO 8601 dates or null, in both referenced and dereferenced form.
    """
    check = validator("referenced", "documents", registry)
    record = first_record(data, "documents", lambda r: True)
    for value in ("2023-03-03", None):
        record["first_publication_date"] = value
        assert not failures(check, [record])
    for value in ("March 2023", "2023-13-45"):
        record["first_publication_date"] = value
        assert failures(check, [record])

    check = validator("dereferenced", "documents", registry)
    path = next((DEREFERENCED_ROOT / "documents").glob("*.json"))
    document = json.loads(path.read_text())
    assert not failures(check, [document])
    for extension in document["extensions"]:
        if extension["name"] == "publication_date":
            extension["value"] = "March 2023"
    assert failures(check, [document])


def test_every_entity_has_a_schema(input_paths):
    """
    Ensures every referenced file and every dereferenced directory has a schema.
    """
    referenced = {p.stem.removesuffix(".schema") for p in schema_paths("referenced")}
    dereferenced = {
        p.stem.removesuffix(".schema") for p in schema_paths("dereferenced")
    }
    expected_referenced = set(input_paths) | {"about", "extension"}
    expected_dereferenced = {
        p.name for p in DEREFERENCED_ROOT.iterdir() if p.is_dir()
    } | {"extension"}
    assert expected_referenced <= referenced, expected_referenced - referenced
    assert expected_dereferenced <= dereferenced, expected_dereferenced - dereferenced


def test_gene_fusion_requires_partner_gene(data, registry):
    """
    Ensures a fusion biomarker with no genes fails, while other rearrangements may have none.
    """
    check = validator("referenced", "biomarkers", registry)
    fusion = first_record(
        data,
        "biomarkers",
        lambda r: (
            r["biomarker_type"] == "Rearrangement"
            and extension_value(r, "rearrangement_type") == "Fusion"
        ),
    )
    fusion["genes"] = []
    assert failures(check, [fusion])

    other = first_record(
        data,
        "biomarkers",
        lambda r: (
            r["biomarker_type"] == "Rearrangement"
            and extension_value(r, "rearrangement_type") != "Fusion"
            and not r["genes"]
        ),
    )
    assert not failures(check, [other])


def test_hse_indication_requires_reimbursement_fields(data, registry):
    """
    Ensures only HSE indications carry, and must carry, reimbursement fields.
    """
    check = validator("referenced", "indications", registry)
    hse = first_record(data, "indications", lambda r: r["id"].startswith("ind:hse:"))
    del hse["reimbursement_scheme"]
    assert failures(check, [hse])

    fda = first_record(data, "indications", lambda r: r["id"].startswith("ind:fda:"))
    fda["reimbursement_scheme"] = "CDS"
    fda["reimbursement_comment"] = None
    assert failures(check, [fda])


def test_referenced_about_matches_schema(registry):
    """
    Ensures referenced/about.json validates against its schema.
    """
    about = json.loads((REFERENCED_ROOT / "about.json").read_text())
    assert not failures(validator("referenced", "about", registry), [about])


@pytest.mark.parametrize(
    "key",
    [
        "agents",
        "alleles",
        "biomarker_criteria",
        "biomarkers",
        "codings",
        "contributions",
        "copy_changes",
        "diseases",
        "documents",
        "function_consequences",
        "genes",
        "indications",
        "mappings",
        "propositions",
        "sequence_locations",
        "sequence_references",
        "statements",
        "strengths",
        "therapies",
        "therapy_groups",
        "urls",
    ],
)
def test_referenced_records_match_schema(key, data, registry):
    """
    Ensures every record in a referenced file validates against its schema.
    """
    bad = failures(validator("referenced", key, registry), data[key])
    assert not bad, f"{len(bad)} invalid {key} records, e.g. {bad[:3]}"


@pytest.mark.parametrize(
    "path",
    schema_paths("referenced") + schema_paths("dereferenced"),
    ids=lambda p: f"{p.parent.name}/{p.name}",
)
def test_schema_is_valid(path):
    """
    Ensures each schema is itself valid draft 2020-12, and that its `$id` matches its path.
    """
    schema = load_schema(path)
    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema["$id"].endswith(f"/schemas/{path.parent.name}/{path.name}")


def test_unknown_indication_organization_is_rejected(data, registry):
    """
    Ensures an indication id with an unrecognized organization fails.
    """
    check = validator("referenced", "indications", registry)
    record = first_record(data, "indications", lambda r: True)
    record["id"] = "ind:xyz:0"
    assert failures(check, [record])


def validator(tree, name, registry):
    schema = load_schema(SCHEMA_ROOT / tree / f"{name}.schema.json")
    # `format` (e.g. "date") is only asserted when a format checker is supplied.
    return jsonschema.Draft202012Validator(
        schema,
        registry=registry,
        format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER,
    )
