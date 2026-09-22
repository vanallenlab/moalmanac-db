Schemas for the normalized tables in [referenced/](../../referenced/). One schema per file, describing a single record (files are arrays, except `about.json`).

Foreign keys stay as ids here: a string with a pattern matching the target table's id prefix (for example, `agent_id` in `contributions.schema.json` matches `agents.schema.json`'s `id` pattern), plus a description naming the target table. References are checked by [tests/test_references.py](../../tests/test_references.py), not by these schemas.

See [schemas/README.md](../README.md) for shared conventions and inheritance patterns.
