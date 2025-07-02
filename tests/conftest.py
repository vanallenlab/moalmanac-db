import pytest
from utils import read

@pytest.fixture(scope="session")
def input_paths():
    return {
        'agents': 'referenced/agents.json',
        'biomarkers': 'referenced/biomarkers.json',
        'contributions': 'referenced/contributions.json',
        'diseases': 'referenced/diseases.json',
        'documents': 'referenced/documents.json',
        'genes': 'referenced/genes.json',
        'indications': 'referenced/indications.json',
        'organizations': 'referenced/organizations.json',
        'propositions': 'referenced/propositions.json',
        'statements': 'referenced/statements.json',
        'therapies': 'referenced/therapies.json'
    }

@pytest.fixture(scope="session")
def data(input_paths):
    return {key: read.json_records(file=value) for key, value in input_paths.items()}
