# Contributing to the Molecular Oncology Almanac database

Thank you for your interest in contributing to the Molecular Oncology Almanac (moalmanac) knowledge base. Contributions come in two broad forms: **database content** (new or revised records) and **repository development** (schemas, tests, utilities, documentation). Both are made through Pull Requests.

By contributing, you agree that database content you contribute is released under [CC BY 4.0](./LICENSE) and code under [GPL v2](./LICENSE-code), matching the rest of this repository.

## Table of contents

- [Ways to contribute](#ways-to-contribute)
- [Repository layout](#repository-layout)
- [Setting up](#setting-up)
- [Making a change](#making-a-change)
- [Contributing database content](#contributing-database-content)
- [Contributing code, schemas, and documentation](#contributing-code-schemas-and-documentation)
- [Checks before opening a pull request](#checks-before-opening-a-pull-request)
- [Pull requests](#pull-requests)
- [Releases](#releases)

## Ways to contribute

- **Report a problem or suggest a change** by opening an [Issue](https://github.com/vanallenlab/moalmanac-db/issues/new/choose). Templates exist for bug reports, content updates, feature requests, and development tasks.
- **Suggest content** (a new assertion, a correction, or a removal) by [opening a `content update` Issue](https://github.com/vanallenlab/moalmanac-db/issues/new?template=content_update.md), or by following the process in [Contributing database content](#contributing-database-content) and opening a Pull request.
- **Improve the repository** by fixing bugs, extending tests, or improving documentation.

If you are unsure whether a change is wanted, open an Issue first so it can be discussed before you invest time in it.

## Repository layout

| Path | Contents |
| --- | --- |
| `referenced/` | The source of truth for the relational schema: normalized JSON tables, one per entity type. **Edit these files** when changing content. See [referenced/README.md](./referenced/README.md). |
| `dereferenced/` | Per-entity files generated from `referenced/`. Do not edit by hand. |
| `schemas/` | JSON schemas for `referenced/` and `dereferenced/` records. See [schemas/README.md](./schemas/README.md). |
| `tests/` | The pytest suite. See [tests/README.md](./tests/README.md). |
| `utils/` | Scripts for dereferencing, reading, and writing the database, and for generating VRS records. See [utils/README.md](./utils/README.md). |
| `datasources/` | Third-party reference files (for example, OncoTree and NCI Thesaurus) used to build and check records. See [datasources/README.md](./datasources/README.md). |
| `docs/` | Documentation, including the curation [standard operating procedure](./docs/sop.md). |
| `moalmanac-draft.dereferenced.json` | Single dereferenced database file generated from `referenced/`. Do not edit by hand. |

The database is being migrated from the legacy schema to a relational schema aligned with [GA4GH VA-Spec](https://github.com/ga4gh/va-spec) and [Cat-VRS](https://github.com/ga4gh/cat-vrs). New work should target the relational schema in `referenced/`.

## Setting up

1. [Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) this repository.
2. Create the environment, which uses Python 3.14:

   ```bash
   conda env create -f environment.yaml
   conda activate moalmanac-db
   ```

   A standard virtual environment also works; see [Python dependencies](./README.md#python-dependencies) in the README.
3. Confirm that the tests pass before you begin:

   ```bash
   pytest tests/
   ```

## Making a change

1. Create a branch from `main`. Use a short, descriptive name, for example `2026-10-28-fda-ibrance` or `fix-url-formatting`.
2. Make your changes in small, reviewable commits.
3. Run the [checks](#checks-before-opening-a-pull-request) locally.
4. Push your branch and open a pull request against `main`.

Do not commit directly to `main`.

## Contributing database content

Content changes are made in the files under `referenced/`. Follow the conventions in the [curation standard operating procedure](./docs/sop.md) and the entity descriptions in [referenced/README.md](./referenced/README.md) and [docs/referenced-schema-draft-about.md](./docs/referenced-schema-draft-about.md).

Some principles to keep in mind:

- **Every statement is source-centric.** A statement must trace back to a document (an FDA label, guideline, journal article, or other source) through its proposition, indication, or evidence. Record the source's own wording where the schema calls for it, for example regulatory approval text is entered verbatim as an indication.
- **Records are never deleted.** If a record is no longer current, change its status rather than removing it: `Superseded` when the issuing agency has updated or replaced it, and `Deprecated` when the record was our error.
- **IDs are stable and unique.** Integer IDs are used for most entities, and string IDs follow existing conventions (for example `doc:{org}.{drug}`, `ind:{org}.{drug}:{n}`, `oncotree:BRCA`); copy the pattern of neighboring records. Take the next unused ID within each file. Never reuse or renumber an existing ID.
- **Reuse existing records.** Before adding a gene, disease, therapy, coding, or biomarker, check whether it already exists.
- **Mappings and codings** link concepts to external vocabularies (HGNC, OncoTree, NCI Thesaurus, RxNorm, and others). Use the terms in [datasources/](./datasources) where possible.
- **Keep the sort order.** Records within each file are expected to be ordered consistently; the test suite checks this.
- **Update dates.** Update the last-updated dates in `referenced/about.json` and `referenced/agents.json`.

After editing `referenced/`, regenerate the dereferenced outputs and commit them with your change:

```bash
python -m utils.dereference --clear
```

(Use `python utils/dereference.py --write-concepts --clear` if you also need the per-concept files written to `dereferenced/<entity>/`.)

## Contributing code, schemas, and documentation

- **Style.** Code is formatted and linted with [ruff](https://docs.astral.sh/ruff/), configured in [pyproject.toml](./pyproject.toml): 88-character lines, trailing commas, and one import per line. Match the conventions of the surrounding code.
- **Schemas.** If you change the shape of a record, update the matching JSON schema in `schemas/`, the dereference logic in [utils/dereference.py](./utils/dereference.py), the entity documentation in `referenced/README.md`, and the tests that cover it.
- **Tests.** Add or update tests in `tests/` for new conventions or checks. Tests operate on the raw `referenced/` files (loaded in [tests/conftest.py](./tests/conftest.py)), and some also read `dereferenced/`.
- **Documentation.** Update the README or the relevant sub-directory README whenever behavior, arguments, or conventions change.
- **Markdown.** Documentation is checked with markdownlint using [.markdownlint.json](./.markdownlint.json).

## Checks before opening a pull request

From the repository root, with the `moalmanac-db` environment active:

```bash
ruff check .
ruff format --check .
pytest tests/
```

The test suite covers record hygiene (unique IDs, duplicates, URL consistency), formatting, ordering, date validity, foreign-key integrity across tables, spelling and terminology, schema validation, and compliance with VA-Spec, Cat-VRS, and VRS. A pull request should not be merged with failing tests. If a test failure seems to be a false positive or the test itself needs to change, explain why in the pull request.

## Pull requests

Opening a pull request pre-fills the [pull request template](./.github/PULL_REQUEST_TEMPLATE.md). Please complete it:

- Start with one to three plain-language sentences saying what the pull request does and why.
- For content changes, list added, revised, and removed entries, linking each to its record on [moalmanac.org](https://moalmanac.org). These entries are reused for the content changelog.
- For repository changes, describe the change and link related issues.
- Under implementation details, list what changed in the database or repository so a reviewer knows what to look at.
- Complete the checklist.

Pull requests are reviewed by other members of the curation or development team before merging. Reviewers may ask for changes; please respond on the pull request thread. Keep each pull request focused on one source, one theme, or one fix so it is easy to review.

## Releases

Releases are made by the maintainers and are tagged by date as `v.{YYYY}-{MM}-{DD}`. Content changes are summarized in the [content changelog](https://docs.moalmanac.org/news/category/database/) using the [Release template](./.github/RELEASE_TEMPLATE.md). Contributors do not need to create tags or releases.

## Questions

If something here is unclear, open an issue or [contact us](https://docs.moalmanac.org/about/contact/).
