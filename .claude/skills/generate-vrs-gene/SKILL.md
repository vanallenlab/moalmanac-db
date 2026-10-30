---
name: generate-vrs-gene
description: Generate the GA4GH VRS records a gene in referenced/genes.json points at — SequenceReferences and full-length SequenceLocations for its MANE Select transcript (NM_) and protein (NP_), per-exon locations, the protein's RefSeq coding, and an NM-to-NP mapping. Use when the user wants to add a new gene to the database (e.g. "add MET", "we need ERBB3 for a new indication"), or when a gene is missing its transcript, protein product, or exon locations.
compatibility: Run from the moalmanac-db repository root in the moalmanac-db conda env. Needs variation-normalizer at localhost:8001, the seqrepo REST service at localhost:5001, and internet access to NCBI eutils.
---

# Generate VRS records for a gene

Every step uses a `python -m utils.vrs.*` script. Each script prints the record(s) it generates. Re-running it with `--upsert-dir referenced` writes them and reports `created`/`updated`/`unchanged` per id, so a re-run is harmless. Later steps nest earlier records by id, so run the steps in order.

## Inputs

- **Transcript (`NM_`):** the gene's MANE Select transcript. For a gene already in `referenced/genes.json`, use its `mappings` entry containing `"::refseq:"` (`"map:hgnc:3236::refseq:NM_005228.5"` → `NM_005228.5`). For a new gene, look it up on NCBI.
- **Protein (`NP_`):** the `/protein_id` of the transcript's GenBank CDS. For an existing gene, it is also the `name` of the SequenceReference behind its `protein_product` location.

## Progress

- [ ] 1. SequenceReferences. First search `referenced/sequence_references.json` for `name == accession` and generate only the missing ones:
  ```bash
  python -m utils.vrs.sequence_reference NM_005228.5 --gene EGFR
  python -m utils.vrs.sequence_reference NP_005219.2 --gene EGFR --transcript NM_005228.5
  ```
- [ ] 2. Full-length SequenceLocations, `[0, length)`:
  ```bash
  python -m utils.vrs.sequence_location NM_005228.5 --full-length --gene EGFR
  python -m utils.vrs.sequence_location NP_005219.2 --full-length --gene EGFR \
      --transcript NM_005228.5
  ```
- [ ] 3. Per-exon locations, the protein coding, and the NM→NP mapping:
  ```bash
  python -m utils.vrs.exons --transcript NM_005228.5 --gene EGFR
  ```
  `--protein` defaults to the GenBank CDS `/protein_id`. Pass it explicitly to have the script check that it matches.
- [ ] 4. Review the output of steps 1–3, then re-run each command with
  `--upsert-dir referenced`.
- [ ] 5. In `referenced/genes.json`, keep the existing key order and set:
  - `transcript` to the NM location's `id`;
  - `protein_product` to the NP location's `id`;
  - `cds_start`;
  - `transcript_exons` and `protein_product_exons`, using the ordered ids from the exons output.
- [ ] 6. Add a `coding:refseq:{NM}` record for the transcript to `referenced/codings.json` if one doesn't exist yet. The new mapping's `primary_coding_id` points at it.
- [ ] 7. Validate: run `pytest tests/`. If anything fails, fix it and re-run before finishing.

## Gotchas

- **Service unreachable (exit code 3).** Stop and tell the user which service to start. Never build a record by hand.
- **No exon features (exit code 1).** Flag the gene for manual review. Don't derive exon boundaries from the CDS `join(...)`: that misses or misplaces UTR-only exons.
- **No `ensembl:` alias is normal.** It is included only when SeqRepo cross-references one, and about half of RefSeq transcripts have none (e.g. `BRAF NM_004333.6`). This is expected, not an error.
- **Protein exons may overlap on purpose.** Protein coordinates round outward, so a codon split across an exon-exon junction belongs to both exons. Adjacent protein locations may overlap by up to 2 residues, and the affected descriptions say so. Don't "fix" it.
- **Protein exons exclude the stop codon.** They are clipped at `cds_start + 3 * protein_length`. The script checks that the first starts at 0 and the last ends at the protein length.
- **The NM→NP mapping isn't the gene's.** It is keyed on the transcript coding, not the gene's HGNC coding, so it does **not** go in the gene's own `mappings` list.
- **Location ids are deterministic.** A SequenceLocation's `id` depends only on `start`, `end`, and the refget accession, so the same span always yields the same `id` and upsert dedups on it.
- **`sequence` is explicitly `null`.** `sequenceReference` is a string id into `referenced/sequence_references.json`. If `sequence` is missing, `SequenceLocations.dereference()` raises `KeyError`.
- **NCBI responses are cached** as provenance in `datasources/refseq/{NM}.gb` and `{NP}.esummary.json`. Pass `--refetch` to refresh them.
