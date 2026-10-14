<!--
Start with one to three plain-language sentences, without a heading, that say what this pull request does and why.
For example: "Adds the two new indications from FDA's 2026-06-24 Ibrance (palbociclib, NDA207103) label, with 3 and 16 derived statements, respectively."

Write for a human reader first. Leave out commit hashes and internal tooling names. Omit any section or subsection that does not apply, other than the checklist.
-->

## Database content updates

<!--
Describe changes to the database content. These entries are also used for the content changelog (https://news.moalmanac.org/category/database).
Sort items by descending evidence level, then alphabetically by molecular feature.
Each entry links to the record on moalmanac.org. The linked text is a plain-language summary:
  ({Source abbreviation, e.g. FDA, EMA}) [{biomarker(s)} and therapeutic response {sensitivity|resistance} to {therapy} for patients with {disease context}](https://moalmanac.org/indications/{indication id}). {Optional context, e.g. how statements were derived}.
-->

### Added entries

- ({Source}) [{biomarker(s)} and therapeutic response {sensitivity|resistance} to {therapy} for patients with {disease context}](https://moalmanac.org/indications/{id}).

### Revised entries

- ({Source}) [{summary}](https://moalmanac.org/indications/{id}). {Description of change}.

### Removed entries

- ({Source}) {summary}. {Rationale for removal}.

## Feature updates

<!--
Describe changes to this repository, such as schema updates or repository enhancements, and link relevant GitHub issues. If there are none, write: "No repository or schema changes were made. This pull request only updated database content."
-->

## Implementation details

<!--
List what changed in the database or repository so a reviewer knows what to look at. Link records on moalmanac.org where possible, for example:
- [`doc:fda:ibrance`](https://moalmanac.org/documents/doc:fda:ibrance) and `url:fda:ibrance:label` updated to the 2026-06-24 label.
- A total of 19 new statements, 16 propositions ([`prop:vtxr:965`](https://moalmanac.org/propositions/prop:vtxr:965) through [`prop:vtxr:980`](https://moalmanac.org/propositions/prop:vtxr:980)) and 8 therapy groups were added to the database.
Updates to documents and URLs go here, not under Revised entries.
-->

## Merge notes

<!--
Optional. Note anything a reviewer or merger must act on, such as new IDs also used by another open branch that will need renumbering. Delete this section if there is nothing to note.
-->

## Checklist

- [ ] `referenced/about.json` and `referenced/agents.json` last updated dates were updated.
- [ ] All files changed have been reviewed.
- [ ] All relevant documentation has been updated.
- [ ] All unit tests have passed.
