---
name: pull-request-notes
description: Draft human-readable pull request notes for a moalmanac-db branch, following .github/PULL_REQUEST_TEMPLATE.md. Use when the user wants to write, draft, or update PR notes, a PR description, or a summary of a branch for review (e.g. "write up this branch", "PR text for the Ibrance update"), especially for curation branches that add or revise indications and statements.
---

# Pull request notes

Draft pull request notes for the current branch, following `.github/PULL_REQUEST_TEMPLATE.md`. The reader is a curator or reviewer, not a parser: the notes should read as plain prose, and should tell the reviewer what changed and what to look at.

## Gather

1. Read `.github/PULL_REQUEST_TEMPLATE.md` for the current section order.
2. Compare the branch to `main`:
   - `git log --oneline main..HEAD`
   - `git diff --stat main...HEAD -- referenced/`
   - `git diff main...HEAD -- referenced/<file>.json` for each changed table.
3. From the diff, collect:
   - New, revised, and removed indications (`referenced/indications.json`). Read each one's `description`, `statement_description`, `raw_biomarkers`, `raw_cancer_types`, and `raw_therapeutics`.
   - New statements per indication (`stmt:{agent}:{drug}:{n}:{m}` belongs to `ind:{agent}:{drug}:{n}`), so you can give per-indication counts.
   - New propositions, therapy groups, therapies, biomarkers, and diseases, with their counts and first-to-last ID ranges.
   - Changed documents and URLs, for example an evergreen label moved to a newer date.
   - New contributions.
   - Existing records that the new statements reuse (propositions or therapy groups). These explain why the proposition count can be lower than the statement count.
4. If other local branches add records to the same tables, check whether they use the same new IDs (`git diff main...<branch> -- referenced/propositions.json`, and so on). Overlapping IDs go in Merge notes.
5. Do not run the tests just to tick the checklist. Tick only the items that were actually verified in this session or that the user confirms.

## Write

Write the notes to `{YYYY-MM-DD}-{application number}.md` at the repository root (for example `2026-10-13-NDA207103.md`), using the branch's date. If the branch is not tied to a single application, use the branch name. Do not open or edit the pull request on GitHub unless asked.

### Overview (no heading)

One to three sentences:

1. What was added, and from what source, with counts. For example: "Adds the two new indications from FDA's 2026-06-24 Ibrance (palbociclib, NDA207103) label, with 3 and 16 derived statements, respectively."
2. What happened to the document, for example: "The evergreen Ibrance document and its label URL now point to the 2026-06-24 label."
3. What happened to existing records, for example: "The two existing Ibrance indications were unchanged in the newer label."

Name the drug as `Brand (generic, application number)` the first time it appears.

### Database content updates

- Use `###` subheadings: `Added entries`, `Revised entries`, `Removed entries`. Omit any subheading that has no items. Do not write "None."
- Write one bullet per indication, not per statement.
- Bullet format: `({Source}) [{summary}](https://moalmanac.org/indications/{id}).` followed, if needed, by one or two sentences of context.
  - `{Source}` is the source organization's abbreviation: `FDA`, `EMA`, and so on.
  - `{summary}` follows the pattern `{biomarkers} and therapeutic response {sensitivity|resistance} to {therapy} for patients with {population and disease}`.
  - **Biomarkers.** Plain-language names, listed alphabetically: "HER2-negative, Hormone receptor positive, and PIK3CA oncogenic variants". Collapse ER-positive and PR-positive into "Hormone receptor positive" when the label says HR-positive.
  - **Therapy.** Name the primary drug first, then "in combination with" the other agents in alphabetical order, keeping the label's qualifiers such as "with or without pertuzumab".
  - **Population.** Take it from the label's wording. Drop "adult patients" and the "IBRANCE is a kinase inhibitor indicated…" boilerplate.
  - Do not put a period inside the link text. The sentence's period goes after the link.
  - Leave out ontology codes (NCIt and OncoTree). The link carries them.
- Add a context sentence when the statements needed a curation decision, for example when they were expanded from a class named in the label: "Statements were derived for anastrozole, exemestane, fulvestrant, and letrozole as endocrine therapies, per the agents used as endocrine therapy in the supporting clinical trial (PATINA, NCT02947685)."
- `Revised entries` is for changes to indications or statements. Updates to documents and URLs go under Implementation details.

### Feature updates

If there are no repository or schema changes, write exactly: "No repository or schema changes were made. This Pull Request only updated database content." Otherwise, describe the change in prose and link the relevant issues.

### Implementation details

Write short bullets, each one a complete sentence, ordered roughly as follows:

1. Changes to documents and URLs, for example: "[`doc:fda:ibrance`](https://moalmanac.org/documents/doc:fda:ibrance) and `url:fda:ibrance:label` updated to the 2026-06-24 label."
2. Contributions added.
3. Totals and ID ranges for the new records, for example: "A total of 19 new statements, 16 propositions ([`prop:vtxr:965`](https://moalmanac.org/propositions/prop:vtxr:965) through [`prop:vtxr:980`](https://moalmanac.org/propositions/prop:vtxr:980)) and 8 therapy groups ([`txgrp:214`](https://moalmanac.org/therapy-groups/txgrp:214) through [`txgrp:221`](https://moalmanac.org/therapy-groups/txgrp:221)) were added to the database."
4. Existing records that the new statements reuse, if any.

Links use `https://moalmanac.org/{indications|documents|propositions|therapy-groups}/{id}`, with the ID in backticks as the link text. Do not link URL records.

### Merge notes

Include this section only if something needs action, such as new IDs that collide with another open branch. Name the IDs and the other branches.

### Checklist

Copy the checklist from the template. Tick only verified items. After the tests item, add the result in parentheses, for example "(140 passed, 1 skipped, run after the `dereferenced/` files were regenerated.)"

## Style

- Write in plain prose. Leave out commit hashes, internal tool and analysis names, and file paths, except in the checklist.
- Do not repeat an item across sections.
- Follow APA style for numbers:
  - Spell out one through nine, and use numerals for 10 and above ("the two new indications", "19 new statements").
  - When numbers counting the same kind of thing appear together and any of them is 10 or more, use numerals for all of them ("3 and 16 derived statements"; "19 new statements, 16 propositions … and 8 therapy groups").
  - Never start a sentence with a numeral. Spell the number out or reword the sentence.
  - Always use numerals for dates, IDs, versions, and test counts ("140 passed, 1 skipped").
- Use the label's dates in ISO 8601 (`2026-06-24`).
- Check the spelling of drug names (for example, "exemestane").
- Keep it short. A reviewer should be able to read the whole thing in under a minute.

## Example

```markdown
Adds the two new indications from FDA's 2026-06-24 Ibrance (palbociclib, NDA207103) label, with 3 and 16 derived statements, respectively. The evergreen Ibrance document and its label URL now point to the 2026-06-24 label. The two existing Ibrance indications were unchanged in the newer label.

## Database content updates

### Added entries

- (FDA) [HER2-negative, Hormone receptor positive, and PIK3CA oncogenic variants and therapeutic response sensitivity to palbociclib in combination with fulvestrant and inavolisib for patients with endocrine-resistant, locally advanced or metastatic breast cancer following recurrence on or after completing adjuvant endocrine therapy](https://moalmanac.org/indications/ind:fda:ibrance:2).
- (FDA) [HER2-positive and Hormone receptor positive and therapeutic response sensitivity to palbociclib in combination with endocrine therapy and trastuzumab, with or without pertuzumab for patients with locally advanced or metastatic breast cancer following induction treatment](https://moalmanac.org/indications/ind:fda:ibrance:3). Statements were derived for anastrozole, exemestane, fulvestrant, and letrozole as endocrine therapies, per the agents used as endocrine therapy in the supporting clinical trial (PATINA, NCT02947685).

## Feature updates

No repository or schema changes were made. This pull request only updated database content.

## Implementation details

- [`doc:fda:ibrance`](https://moalmanac.org/documents/doc:fda:ibrance) and `url:fda:ibrance:label` updated to the 2026-06-24 label.
- Contributions for the initial traditional approvals and curation into moalmanac-db for the two Ibrance indications were added.
- A total of 19 new statements, 16 propositions ([`prop:vtxr:965`](https://moalmanac.org/propositions/prop:vtxr:965) through [`prop:vtxr:980`](https://moalmanac.org/propositions/prop:vtxr:980)) and 8 therapy groups ([`txgrp:214`](https://moalmanac.org/therapy-groups/txgrp:214) through [`txgrp:221`](https://moalmanac.org/therapy-groups/txgrp:221)) were added to the database.

## Checklist

- [ ] `referenced/about.json` and `referenced/agents.json` last updated dates were updated.
- [x] All files changed have been reviewed.
- [x] All relevant documentation has been updated.
- [x] All unit tests have passed. (140 passed, 1 skipped, run after the `dereferenced/` files were regenerated.)
```
