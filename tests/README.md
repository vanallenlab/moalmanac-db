# Testing

This directory contains tests for this repository, using [pytest](https://docs.pytest.org/en/stable/).

## Structure

Tests are organized by type data being tested. The files are:

- [conftest.py](./conftest.py) - shared fixtures to be used by all tests, such as loading data files.
- [helpers.py](./helpers.py) - helper functions for tests.
- [test_consistency.py](./test_consistency.py) - checks for internal inconsistencies within individual records, such as field values that conflict with one another.
- [test_dates.py](./test_dates.py) - checks that date fields are logically consistent.
- [test_duplicates.py](./test_duplicates.py) - checks that no duplicate records or `id`s are present in the database.
- [test_formatting.py](./test_formatting.py) - checks string formatting conventions are being followed.
- [test_ordering.py](./test_ordering.py) - checks that list values are ordered as expected (alphabetically).
- [test_references.py](./test_references.py) - checks cross-file and cross-record referential integrity, including foreign key validity and consistency between linked records.
- [test_va_spec.py](./test_va_spec.py) - checks that records conform to the [GA4GH Variant Annotation Specification (VA-Spec)](https://va-spec.ga4gh.org/en/latest/) schema.
- [test_validation.py](test_validation.py) - checks that records conform to internal schemas, including required keys and expected types.

Pytest settings can be configured from [pytest.ini](../pytest.ini).

### Running tests

Run all tests from the repository's root directory:

```bash
pytest tests/
```
