Schemas for the per-concept files in [dereferenced/](../../dereferenced/), [referenced](../../referenced/) records with foreign keys resolved to embedded objects by [utils/dereference.py](../../utils/dereference.py). One schema per entity, matching the directory names there — note `therapy_groups.schema.json`, not `therapy_group`.

Foreign keys are `$ref`s to the embedded entity's schema instead of ids. Several entities also change shape on dereference and are worth knowing before editing:

- `documents`: publisher, company, drug names, dates, and status move into `extensions`; `urls` become plain strings.
- `genes`: `cds_start`, `location`, and sequence locations move into `extensions` — but a gene embedded in a `biomarkers` constraint has `extensions` stripped (see `genes.schema.json`'s `$defs/Gene`).
- `alleles`: the referenced `hgvs.*` keys fold into `expressions`, and `state_*` folds into `state`.
- `propositions`: `subjectVariant` is a fixed placeholder until [Cat-VRS supports sets of biomarkers](https://github.com/ga4gh/cat-vrs/pull/248); the actual biomarkers live in a `biomarkers` extension (each item a `biomarker_criteria` record).
- `statements`: `status` and the full `indication` record move into `extensions`.

See [schemas/README.md](../README.md) for shared conventions and inheritance patterns.
