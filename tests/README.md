# Testing
This directory contains tests for this repository, using [pytest](https://docs.pytest.org/en/stable/). 

### Structure
Tests are organized by type data being tested. The files are:
- [`conftest.py`](conftest.py) - shared fixtures to be used by all tests, such as loading data files.
- [`helpers.py](helpers.py) - helper functions for tests.
- [`test_dates.py`](test_dates.py) - checks that date fields are logically consistent.
- [`test_formatting.py`](test_formatting.py) - checks for formatting conventions in strings.
- [`test_hygiene.py`](test_hygiene.py) - checks that field values within a single dataset are entered as expected.
- [`test_ordering.py`](test_ordering.py) - checks that list values are ordered as expected (alphabetically).
- [`test_reference.py`](test_references.py) - checks that foreign keys or cross-file references are valid.
- [`test_validation.py`](test_validation.py) - checks that schemas are followed.

Pytest settings can be configured from [pytest.ini](../pytest.ini).

### Running tests
Run all tests from the repository's root directory:
```bash
pytest tests/
```
