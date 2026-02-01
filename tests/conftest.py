import pathlib
import pytest
from utils import read


@pytest.fixture(scope="session")
def input_paths():
    return {
        "agents": "referenced/agents.json",
        "biomarkers": "referenced/biomarkers.json",
        "codings": "referenced/codings.json",
        "contributions": "referenced/contributions.json",
        "diseases": "referenced/diseases.json",
        "documents": "referenced/documents.json",
        "genes": "referenced/genes.json",
        "indications": "referenced/indications.json",
        "mappings": "referenced/mappings.json",
        "propositions": "referenced/propositions.json",
        "statements": "referenced/statements.json",
        "strengths": "referenced/strengths.json",
        "therapies": "referenced/therapies.json",
        "therapy_groups": "referenced/therapy_groups.json",
    }


@pytest.fixture(scope="session")
def data(input_paths):
    return {key: read.json_records(file=value) for key, value in input_paths.items()}


@pytest.fixture(scope="session")
def dereferenced_paths():
    root = pathlib.Path("dereferenced")
    return {
        "agents": root / "agents",
        "codings": root / "codings",
    }


@pytest.fixture(scope="session")
def dereferenced_records(dereferenced_paths):
    data = {}
    for entity, base in dereferenced_paths.items():
        records = []
        for path in sorted(base.glob("*.json")):
            record = read.json_records(file=str(path))
            records.append(record)
        data[entity] = records
    return data
