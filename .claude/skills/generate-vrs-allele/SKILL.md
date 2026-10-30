---
name: generate-vrs-allele
description: Generate a GA4GH VRS Allele and its SequenceLocation for a somatic protein-level variant, and link it from the biomarker so it dereferences as a DefiningAlleleConstraint. Use when the user adds or curates a protein-change biomarker (e.g. "add EGFR L858R", "KRAS G12C needs an allele", a new referenced/biomarkers.json record of biomarker_type "Somatic variant" named like "BRAF p.V600E"), even if they don't mention VRS.
compatibility: Run from the moalmanac-db repository root in the moalmanac-db conda env. Needs variation-normalizer at localhost:8001.
---

# Generate a VRS Allele

Builds a `referenced/alleles.json` record and its `referenced/sequence_locations.json` record for a protein change, using `utils.vrs.allele`. You then point the biomarker's `allele` field at it, so `Biomarkers.wrap_constraints()` (in `utils/dereference.py`) wraps it into a `DefiningAlleleConstraint` on dereference.

## Inputs

- **Which biomarkers qualify:** only those with root `biomarker_type == "Somatic variant"` and `" p."` in their `name`.
- **Gene and change:** split the biomarker `name` on the first space, so `"EGFR p.L858R"` → gene `EGFR`, change `p.L858R`.
- **Transcript:** find the gene by `name` in `referenced/genes.json` and take its `mappings` entry containing `"::refseq:"`.
- **Protein accession:** the `name` of the SequenceReference behind the gene's `protein_product` location (`protein_product` → `referenced/sequence_locations.json` → `sequenceReference` → `referenced/sequence_references.json` → `name`), e.g. `NP_005219.2`.
- **If the gene isn't in `genes.json`:** run `generate-vrs-gene` first.

## Progress

- [ ] 1. If no record in `referenced/sequence_references.json` has `name` equal to the protein accession, create it. The location nests it by id.
  ```bash
  python -m utils.vrs.sequence_reference NP_005219.2 --gene EGFR --transcript NM_005228.5
  ```
- [ ] 2. Generate and review the allele and its location:
  ```bash
  python -m utils.vrs.allele --protein NP_005219.2 --change p.L858R --gene EGFR \
      --transcript NM_005228.5
  ```
- [ ] 3. Re-run steps 1–2 with `--upsert-dir referenced` to write the records.
- [ ] 4. Set the biomarker's `allele` to the allele `id`. A biomarker has at most one defining allele; non-qualifying biomarkers keep `allele: null`. Preserve the biomarker key order `id, type, name, allele, copyChange, function, genes, location, biomarker_type, extensions`.
- [ ] 5. Validate: run `pytest tests/`. If anything fails, fix it and re-run before finishing.

## Gotchas

- **Service unreachable (exit code 3).** Stop and tell the user to start variation-normalizer. Never build a record by hand.
- **Change can't be resolved (exit code 1).** `/to_vrs` couldn't resolve the change. Flag the biomarker for manual follow-up rather than guessing.
- **`hgvs.p` is only set for simple substitutions.** It is the 3-letter form (`NP_005219.2:p.Leu858Arg`). Deletions, insertions, and frameshifts (`p.I836del`, `p.W288Cfs*12`) get `hgvs.p: null`, and `name` falls back to the query (`NP_…:p.I836del`).
- **`state_length`/`state_repeat_subunit_length` are often `null`.** They are set only for a `ReferenceLengthExpression` state (e.g. a deletion), and are `null` for a `LiteralSequenceExpression`.
- **Generate the location with the allele.** A variant's location comes from the same `/to_vrs` call as the allele, so don't generate it separately. For a location on an arbitrary span with no allele, use:
  ```bash
  python -m utils.vrs.sequence_location NP_005219.2 --start 857 --end 858 \
      --description "..."
  ```
