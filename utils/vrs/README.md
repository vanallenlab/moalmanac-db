# utils/vrs

Generators for [GA4GH VRS](https://github.com/ga4gh/vrs) objects, shaped as `referenced/`
records, for adding **new** records to the database. Each script takes explicit inputs
(an accession, coordinates, a protein change), prints the generated record(s) as JSON, and
optionally upserts them (by `id`, overwriting in place) into a `referenced/` table. They
never walk the database or edit genes/biomarkers — linking a new record from a gene or
biomarker is left to the caller (see the `generate-vrs-*` skills in `.claude/skills/`).

Run from the repository root with the `moalmanac-db` environment.

## Services

| Service | Default URL | Used by |
|---|---|---|
| [variation-normalizer](https://github.com/cancervariants/variation-normalization) | `http://localhost:8001/variation` (env `VARIATION_NORMALIZER_URL`) | all scripts (refget accessions, `/to_vrs`) |
| [seqrepo REST service](https://github.com/biocommons/biocommons.seqrepo-rest-service) | `http://localhost:5001/seqrepo/1` (env `SEQREPO_URL`) | `sequence_location --full-length`, `chromosome_arm` |
| NCBI eutils, UCSC API | public | `exons`, `chromosome_arm` |

## Scripts

Every script supports `--output FILE` (instead of stdout) and `--help`.

### sequence_reference

`SequenceReference` for a RefSeq `NM_`, `NP_`, or `NC_` accession.

```bash
python -m utils.vrs.sequence_reference NM_005228.5 --gene EGFR
python -m utils.vrs.sequence_reference NP_005219.2 --gene EGFR --transcript NM_005228.5
python -m utils.vrs.sequence_reference NC_000005.10 --build GRCh38 --chromosome 5 \
    --upsert referenced/sequence_references.json
```

### sequence_location

`SequenceLocation` on a RefSeq sequence, either full-length or an explicit span.

```bash
python -m utils.vrs.sequence_location NM_005228.5 --full-length --gene EGFR
python -m utils.vrs.sequence_location NP_005219.2 --full-length --gene EGFR \
    --transcript NM_005228.5 --upsert referenced/sequence_locations.json
python -m utils.vrs.sequence_location NP_005219.2 --start 857 --end 858 --description "..."
```

### chromosome_arm

`SequenceLocation` spanning a chromosome arm on GRCh38 or GRCh37.

```bash
python -m utils.vrs.chromosome_arm --chromosome 5 --arm q --build GRCh38
```

### exons

Per-exon transcript and protein `SequenceLocation`s, `cds_start`, the protein's RefSeq
`Coding`, and the transcript→protein `Mapping`, from the transcript's GenBank record
(cached in `datasources/refseq/`).

```bash
python -m utils.vrs.exons --transcript NM_005228.5 --gene EGFR
python -m utils.vrs.exons --transcript NM_005228.5 --gene EGFR --upsert-dir referenced
```

### allele

`Allele` and its `SequenceLocation` for a protein change.

```bash
python -m utils.vrs.allele --protein NP_005219.2 --change p.L858R --gene EGFR \
    --transcript NM_005228.5
python -m utils.vrs.allele --protein NP_005219.2 --change p.L858R --gene EGFR \
    --transcript NM_005228.5 --upsert-dir referenced
```

## Python use

Each script's `build(...)` function returns the same records without printing, e.g.

```python
from utils.vrs import sequence_location

record = sequence_location.build(accession="NP_005219.2", start=857, end=858)
```

Offline tests in `tests/test_vrs_utils.py` check the generators reproduce the committed
`referenced/` records.
