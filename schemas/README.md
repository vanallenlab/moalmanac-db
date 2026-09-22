[JSON Schema](https://json-schema.org/) (draft 2020-12) definitions for moalmanac-db records.

- [referenced/](referenced/): schemas for [referenced/](../referenced/) records, with foreign keys to other tables.
- [dereferenced/](dereferenced/): schemas for [dereferenced/](../dereferenced/), with foreign keys resolved.

## Conventions

- Each schema describes one record, not the whole array. `referenced/*.json` files are arrays, so validate each item. `referenced/about.json` is a single object.
- Schemas reference each other with relative `$ref`s, resolved through each schema's `$id`. The `$id`s are identifiers; nothing is fetched over the network.
- Foreign keys in `referenced/` are strings with an id-prefix `pattern` and a description naming the target table. Whether the target exists is checked by [tests/test_references.py](../tests/test_references.py).
- `id` values begin with the data type and a semi-colon delineated; for example, "bmkr:" for [biomarkers](referenced/biomarkers.schema.json).
- `extension.schema.json` is the shared `{name, value, description?}` shape. Entity schemas constrain which extension names and value types are allowed, and which are required, with `contains` (order-independent).

## Inheritance

`indications` and `biomarkers` have a root type in `$defs` and subtypes that `allOf` the root. The top-level schema:

1. `$ref`s the root,
2. dispatches to a subtype with `if`/`then` on a discriminator, and
3. sets `unevaluatedProperties: false`, so unknown keys are rejected once the matching subtype has been applied.

`indications` — discriminator: organization in the id (`ind:{org}:`)

- `EMA Indication`
- `FDA Indication`
- `HC Indication`
- `HPRA Indication`
- `HSE Indication`

`biomarkers` — discriminator: `biomarker_type` extension

- `Copy number`
- `Copy number (arm level)`
- `Germline variant`
- `Haplotype genotype`
- `Homologous recombination`
- `Microsatellite stability`
- `Mismatch repair`
- `Protein expression`
- `Rearrangement`
- `Somatic variant`
- `Tumor mutational burden`
- `Wild type`

Only HSE indications carry reimbursement fields (a `reimbursement_scheme` and `reimbursement_comment` key when referenced, extensions when dereferenced).

`GeneFusion` extends `Rearrangement` and is selected by `rearrangement_type` = `Fusion`.

## Validation

[tests/test_schemas.py](../tests/test_schemas.py) validates every record in `referenced/` and every file in `dereferenced/` against these schemas.
