This directory contains tests for this repository, using [pytest](https://docs.pytest.org/en/stable/).

### Structure

Tests are organized by type data being tested. The files are:

- [`conftest.py`](conftest.py) - shared fixtures to be used by all tests, such as loading data files.
- [`helpers.py`](helpers.py) - helper functions for tests.
- [`test_dates.py`](test_dates.py) - checks that date fields are logically consistent.
- [`test_formatting.py`](test_formatting.py) - checks for formatting conventions in strings.
- [`test_gkm_cat_vrs.py`](test_gkm_cat_vrs.py) - checks biomarkers for compliance with [Categorical Variant Representation Specification](https://github.com/ga4gh/cat-vrs).
- [`test_gkm_core.py`](test_gkm_core.py) - checks primitives for compliance with [Genomic Knowledge Model Core](https://github.com/ga4gh/gkm-core).
- [`test_gkm_va_spec.py`](test_gkm_va_spec.py) - checks primitives for compliance with [Variant Annotation Specification](https://github.com/ga4gh/va-spec).
- [`test_gkm_vrs.py`](test_gkm_vrs.py) - checks biomarkers for compliance with [Variant Representation Specification](https://github.com/ga4gh/vrs).
- [`test_hygiene.py`](test_hygiene.py) - checks that field values within a single dataset are entered as expected.
- [`test_ordering.py`](test_ordering.py) - checks that list values are ordered as expected.
- [`test_reference.py`](test_references.py) - checks that foreign keys or cross-file references are valid.
- [`test_validation.py`](test_validation.py) - checks that schemas are followed.

Pytest settings can be configured from [pytest.ini](../pytest.ini).

### Running tests

Run all tests from the repository's root directory:

```bash
pytest tests/
```
