import collections
import functools
import json
import pathlib
import urllib.parse

DATASOURCES = pathlib.Path("datasources")
NCIT_EVS_EXPLORE_IRI = (
    "https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/{code}"
)
NCIT_PREFIX = "coding:ncit:"
ONCOTREE_PREFIX = "coding:oncotree:"


def build_oncotree_iri(record):
    """
    Builds the expected OncoTree iri for a coding, which searches by name for the coding's system version.

    Args:
        record (dict): an OncoTree coding record.

    Returns:
        str: the OncoTree iri, e.g. for AML in oncotree_2025_10_03,
            https://oncotree.mskcc.org/?version=oncotree_2025_10_03&field=NAME&search=Acute+Myeloid+Leukemia+%28AML%29
    """
    search = urllib.parse.quote_plus(f"{record['name']} ({record['code']})")
    return (
        f"https://oncotree.mskcc.org/?version={record['systemVersion']}"
        f"&field=NAME&search={search}"
    )


def codings_with_prefix(data, prefix):
    return [r for r in data["codings"] if r["id"].startswith(prefix)]


@functools.cache
def load_ncit_thesaurus(version):
    """
    Loads the NCI Thesaurus flat file for a given version, as downloaded by
    datasources/scripts/download_nci_thesaurus.py.

    Args:
        version (str): NCI Thesaurus version, e.g. "26.08e".

    Returns:
        dict[str, str] | None: preferred name keyed by NCIt code, or None if the file is not present.
    """
    path = DATASOURCES / f"Thesaurus_{version}.txt"
    if not path.exists():
        return None
    terms = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            columns = line.rstrip("\n").split("\t")
            terms[columns[0]] = columns[3].split("|")[0]
    return terms


@functools.cache
def load_oncotree(version):
    """
    Loads the OncoTree flat file for a given version, as downloaded by
    datasources/scripts/download_oncotree.py.

    Args:
        version (str): OncoTree version, e.g. "oncotree_2025_10_03".

    Returns:
        dict[str, dict] | None: OncoTree records keyed by code, or None if the file is not present.
    """
    path = DATASOURCES / f"{version}_flat.json"
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as handle:
        return {r["code"]: r for r in json.load(handle)}


def compare_to_source(records, loader, name_of):
    """
    Compares coding records to their source terminology for the coding's system version.

    Args:
        records (list[dict]): coding records.
        loader (callable): returns a dict of terms keyed by code for a version, or None if unavailable.
        name_of (callable): returns the name of a term returned by `loader`.

    Returns:
        tuple[list[str], list[str], list[str]]: coding ids whose source file is missing, whose code is absent
            from the source, and whose name differs from the source.
    """
    missing_source, missing_code, mismatched_name = [], [], []
    for record in records:
        terms = loader(record["systemVersion"])
        if terms is None:
            missing_source.append(f"{record['id']} ({record['systemVersion']})")
        elif record["code"] not in terms:
            missing_code.append(record["id"])
        elif record.get("name") != name_of(terms[record["code"]]):
            mismatched_name.append(
                f"{record['id']}: {record.get('name')!r} != {name_of(terms[record['code']])!r}",
            )
    return missing_source, missing_code, mismatched_name


def test_disease_first_mapping_is_oncotree(data):
    """
    Diseases with an OncoTree mapping list it first.
    """
    mappings = {r["id"]: r for r in data["mappings"]}
    failed = []
    for disease in data["diseases"]:
        coding_ids = [
            mappings[m]["coding_id"] if m in mappings else None
            for m in disease["mappings"]
        ]
        is_oncotree = [
            c is not None and c.startswith(ONCOTREE_PREFIX) for c in coding_ids
        ]
        if any(is_oncotree) and not is_oncotree[0]:
            failed.append(f"{disease['id']}: {disease['mappings'][0]!r}")
    assert not failed, f"First mapping is not an OncoTree coding for diseases: {failed}"


def test_disease_name_matches_primary_coding_name(data):
    """
    A disease's name matches the name of its primary coding.
    """
    codings = {r["id"]: r for r in data["codings"]}
    failed = [
        f"{r['id']}: {r['name']!r} != {codings[r['primary_coding_id']]['name']!r}"
        for r in data["diseases"]
        if r["primary_coding_id"] in codings
        and r["name"] != codings[r["primary_coding_id"]]["name"]
    ]
    assert not failed, f"Disease name differs from primary coding name: {failed}"


def test_disease_primary_coding_is_ncit(data):
    """
    Diseases use NCIt as their primary coding.
    """
    failed = [
        r["id"]
        for r in data["diseases"]
        if not r["primary_coding_id"].startswith(NCIT_PREFIX)
    ]
    assert not failed, f"Diseases without an NCIt primary coding: {failed}"


def test_ncit_codes_exist_in_thesaurus(data):
    """
    NCIt codings exist in the NCI Thesaurus version given by their `systemVersion`.
    """
    records = codings_with_prefix(data, NCIT_PREFIX)
    missing_source, missing_code, _ = compare_to_source(
        records,
        load_ncit_thesaurus,
        lambda name: name,
    )
    assert not (missing_source or missing_code), (
        f"NCIt codes not found in the NCI Thesaurus: {missing_code}; "
        f"NCI Thesaurus file not found in datasources/ for: {missing_source}"
    )


def test_ncit_iris_match_evs_explore(data):
    """
    NCIt codings have a single iri pointing to the concept on EVS Explore.
    """
    failed = [
        r["id"]
        for r in codings_with_prefix(data, NCIT_PREFIX)
        if r.get("iris") != [NCIT_EVS_EXPLORE_IRI.format(code=r["code"])]
    ]
    assert not failed, f"NCIt codings with unexpected iris: {failed}"


def test_ncit_names_match_thesaurus_preferred_name(data):
    """
    NCIt coding names match the preferred name in the NCI Thesaurus version given by their `systemVersion`.
    """
    records = codings_with_prefix(data, NCIT_PREFIX)
    _, _, mismatched_name = compare_to_source(
        records,
        load_ncit_thesaurus,
        lambda name: name,
    )
    assert not mismatched_name, (
        f"NCIt coding names differ from the NCI Thesaurus: {mismatched_name}"
    )


def test_oncotree_codes_exist_in_system_version(data):
    """
    OncoTree codings exist in the OncoTree version given by their `systemVersion`.
    """
    records = codings_with_prefix(data, ONCOTREE_PREFIX)
    missing_source, missing_code, _ = compare_to_source(
        records,
        load_oncotree,
        lambda term: term["name"],
    )
    assert not (missing_source or missing_code), (
        f"OncoTree codes not found in their system version: {missing_code}; "
        f"OncoTree file not found in datasources/ for: {missing_source}"
    )


def test_oncotree_codings_are_referenced(data):
    """
    Every OncoTree coding is referenced by a mapping or used as a disease's primary coding.
    """
    referenced = {r["coding_id"] for r in data["mappings"]}
    referenced |= {r["primary_coding_id"] for r in data["diseases"]}
    failed = [
        r["id"]
        for r in codings_with_prefix(data, ONCOTREE_PREFIX)
        if r["id"] not in referenced
    ]
    assert not failed, f"Unreferenced OncoTree codings: {failed}"


def test_oncotree_iris_use_name_search(data):
    """
    OncoTree codings have a single iri that searches OncoTree by name for the coding's `systemVersion`.
    """
    failed = [
        r["id"]
        for r in codings_with_prefix(data, ONCOTREE_PREFIX)
        if r.get("iris") != [build_oncotree_iri(r)]
    ]
    assert not failed, f"OncoTree codings with unexpected iris: {failed}"


def test_oncotree_names_match_system_version(data):
    """
    OncoTree coding names match the OncoTree name in the version given by their `systemVersion`.
    """
    records = codings_with_prefix(data, ONCOTREE_PREFIX)
    _, _, mismatched_name = compare_to_source(
        records,
        load_oncotree,
        lambda term: term["name"],
    )
    assert not mismatched_name, (
        f"OncoTree coding names differ from OncoTree: {mismatched_name}"
    )


def test_one_to_many_mappings_not_exact_match(data):
    """
    When one primary coding maps to more than one OncoTree coding, none of those mappings are `exactMatch`.
    """
    oncotree_mappings = collections.defaultdict(list)
    for mapping in data["mappings"]:
        if mapping["coding_id"].startswith(ONCOTREE_PREFIX):
            oncotree_mappings[mapping["primary_coding_id"]].append(mapping)
    failed = [
        m["id"]
        for mappings in oncotree_mappings.values()
        if len(mappings) > 1
        for m in mappings
        if m["relation"] == "exactMatch"
    ]
    assert not failed, f"exactMatch used for one-to-many OncoTree mappings: {failed}"
