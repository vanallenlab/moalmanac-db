# Testing
This directory contains tests for this repository, using [pytest](https://docs.pytest.org/en/stable/). 

### Structure
Tests are organized by type data being tested. The files are:
- [`conftest.py`](conftest.py) - shared fixtures to be used by all tests, such as loading data files.
- [`test_dates.py`](test_dates.py) - checks involving date consistency.
- [`test_integrity.py`](test_fields.py) - checks that field values within a single dataset are entered as expected.
- [`test_reference.py`](test_references.py) - checks references between different files.

Pytest settings can be configured from [pytest.ini](../pytest.ini).

### Running tests
Run all tests from the repository's root directory:
```bash
pytest tests/
```
