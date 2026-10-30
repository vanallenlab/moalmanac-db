Agent skills for the Molecular Oncology Almanac database.

These skills follow the [Agent Skills specification](https://agentskills.io/specification). They live in `.claude/skills/`, the folder Claude Code discovers project skills from; other skill-compatible agents may need them copied or symlinked to their own skills folder. They are project skills: each declares in its `compatibility` field that it must run from this repository with the `moalmanac-db` conda environment and any local services it needs.

## Skills

The `generate-vrs-*` skills create [GA4GH VRS](https://vrs.ga4gh.org/) records for the `referenced/` tables. Each one is a single checklist that ends by running the tests. A biomarker's allele needs its gene's records, so run `generate-vrs-gene` before `generate-vrs-allele` for a new gene.

| Skill | Description |
| ----- | ----------- |
| [generate-vrs-gene](./generate-vrs-gene/) | Add a gene's VRS records: SequenceReferences and full-length SequenceLocations for its MANE Select transcript and protein, per-exon locations, the protein's RefSeq coding, and an NM-to-NP mapping. |
| [generate-vrs-allele](./generate-vrs-allele/) | Add a VRS Allele and its SequenceLocation for a somatic protein-level variant biomarker (e.g. `EGFR p.L858R`), creating the protein's SequenceReference if missing, and link it from the biomarker. |
| [generate-vrs-chromosome-arm](./generate-vrs-chromosome-arm/) | Add SequenceLocations spanning a chromosome arm (e.g. `5q`) on GRCh38 and GRCh37, creating the chromosome's SequenceReferences if missing, and link them from the biomarker. |
| [pull-request-notes](./pull-request-notes/) | Draft human-readable pull request notes using `.github/PULL_REQUEST_TEMPLATE.md`. Particularly used for curation branches that add or revise indications and statements. |

The skills drive the command line tools in [`utils/vrs/`](../../utils/vrs/README.md), which can also be used directly, for example:

```bash
python -m utils.vrs.allele \
    --protein NP_005219.2 \
    --change p.L858R \
    --gene EGFR \
    --transcript NM_005228.5 \
    --upsert-dir referenced
```

## Usage

Claude Code discovers skills in `.claude/skills/` automatically when run from this repository. Invoke one by name (e.g. `/generate-vrs-allele`) or describe the task and let the agent select it.

Use the `moalmanac-db` conda environment for any Python commands, and run `pytest tests/` after modifying the `referenced/` tables.

## References

- [Claude's official Skills documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [GA4GH VRS](https://vrs.ga4gh.org/)
- [agent skills](https://agentskills.io)
