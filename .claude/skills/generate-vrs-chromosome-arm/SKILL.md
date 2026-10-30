---
name: generate-vrs-chromosome-arm
description: Generate GA4GH VRS SequenceLocations spanning a chromosome arm (p or q) on GRCh38 and GRCh37, plus the chromosome's SequenceReferences if missing, and link them from the biomarker. Use when the user adds or curates an arm-level copy-number or structural biomarker (e.g. "5q deletion", "1p/19q codeletion", "add a 17p loss biomarker"), even if they don't mention VRS or centromeres.
compatibility: Run from the moalmanac-db repository root in the moalmanac-db conda env. Needs variation-normalizer at localhost:8001, the seqrepo REST service at localhost:5001, and internet access to NCBI eutils and the UCSC REST API.
---

# Generate VRS chromosome-arm locations

Builds a SequenceLocation spanning a chromosome arm using `utils.vrs.chromosome_arm`. The p arm is `[0, centromere_start)` and the q arm is `[centromere_end, chromosome_length)`.

## Progress

- [ ] 1. As of 2026-09, every chromosome (1–22, X, Y) on both builds already has a SequenceReference. Only if `referenced/sequence_references.json` has no record with `name` equal to the accession, create one. Accessions are in `CHROMOSOME_ACCESSIONS` in `utils/vrs/chromosome_arm.py`, as `{chromosome: (GRCh38, GRCh37)}`.
  ```bash
  python -m utils.vrs.sequence_reference NC_000005.10 --build GRCh38 --chromosome 5
  python -m utils.vrs.sequence_reference NC_000005.9 --build GRCh37 --chromosome 5
  ```
- [ ] 2. Generate and review the arm location for each build:
  ```bash
  python -m utils.vrs.chromosome_arm --chromosome 5 --arm q --build GRCh38
  python -m utils.vrs.chromosome_arm --chromosome 5 --arm q --build GRCh37
  ```
- [ ] 3. Re-run the commands with `--upsert-dir referenced` to write the records.
- [ ] 4. Add the location ids to the biomarker's `location` list.
- [ ] 5. Validate: run `pytest tests/`. If anything fails, fix it and re-run before
  finishing.

## Gotchas

- **Service unreachable (exit code 3).** Stop and tell the user which service to start. Never build a record by hand.
- **GRCh38 centromere.** UCSC's hg38 `centromeres` track (dated 2014) gives only a rough window. The script confirms the boundary against NCBI's live RefSeq `centromere` feature and uses NCBI's. If the two disagree by more than 50 kb, it prints a warning on stderr. Mention any such warning to the user in your summary (chr17 is a known case: UCSC is about 270 kb short at the 3' end).
- **GRCh37 centromere.** There is no modeled centromere feature, only the `centromere` gap in UCSC's hg19 `gap` track, so no NCBI cross-check is possible.
- **NCBI 500 errors.** NCBI eutils intermittently returns 500 on the ~4 Mb feature-table window. The script retries automatically. If it still fails, it exits with code 3; try again later.
- **Chromosome accessions have no `ensembl:` alias.** The script omits it when absent.
