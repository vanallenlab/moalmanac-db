The `description` key included for each record in referenced/indications.json is the `description` text for Statements derived from a given Indication. While the `indication` reproduces approval text verbatim from a cited Document, we attempt to do a few things with the Statement's descriptions:

1. Standardize terminology across agencies and time.  
2. Make each description self-contained and readable in isolation.
3. Clarify ambiguity present within the Indication.
4. Follow phrasing guidance from [ASCO's The Language of Respect](https://cdn.bfldr.com/KOIHB2Q3/as/jk8k5wtvq8h6vvw6xnfjtx3/2022-ASCO-Language-Of-Respect). This includes person-first phrasing, such as rephrasing "postmenopausal women" to "patients who are postmenopausal women".

## Conventions

1. **Begin by stating the agency's name associated with the approval** to serve as a citation within the description text. For example, "The U.S. Food and Drug Administration granted approval to..." or "The European Medicines Agency (EMA) has authorized...". Each source agency has a canonical opening clause; see [Per-agency opening clauses](#per-agency-opening-clauses) below.
2. **State the approval status of the indication** to provide the agency's confidence in an approval. For example, "The U.S. Food and Drug Administration granted accelerated approval to..." or "The U.S. Food and Drug Administration granted approval to...". The non-traditional status is also reflected in the opening verb for other agencies; for example, an EMA conditional marketing authorization is written as "The European Medicines Agency (EMA) has conditionally authorized...".
3. **Use generic drug names** to not endorse any specific therapy brand names. For example, writing "pembrolizumab" instead of "Keytruda". 
4. **For drug combinations, state the primary drug first, and then "in combination with"**. For example, "...approved afatinib for the treatment of..." or "...approved dabrafenib in combination with trametinib for the first-line treatment of...". 
5. **State that a treatment regimen is approved "for the treatment of (patient population) patients with (cancer type)" instead of "for the treatment of (cancer type)"** because therapies treat patients, not cancers. For example, rephrasing "...for the treatment of B-cell precursor acute lymphoblastic leukemia... in adult and pediatric patients 1 year and older" to "...for the treatment of adult and pediatric patients aged 1 year and older with B-cell precursor acute lymphoblastic leukemia...". 
6. **Cite underlying clinical trials for ambiguous combination therapies and biomarkers** to clarify ambiguity in the approval. This is most common when an approval involves a combination therapy with class of treatment. In these cases, the clinical trial supporting an approval should be cited for the treatment options available to treating physicians. For example, "... in combination with platinum-based chemotherapy". An approval's treatment eligibility may also be defined using an ambiguous biomarker. For example, "...homologous recombination repair (HRR) gene-mutated..." or "...wild type NRAS or KRAS". The approval document will often clarify what the agencies defines as relevant biomarkers. 
7. **Un-abbreviate abbreviations** because indications are presented in aggregate in the cited documents but individually in MOAlmanac. For example, "... adult patients with advanced NSCLC..." should be written as "...adult patients with advanced non-small cell lung cancer (NSCLC)...". Likewise, writing "hormone receptor (HR)-positive" instead of only "HR-positive".
8. **Include agency-specific warning text for non-traditional approvals**, which are included in the approval Document. For example, the US FDA will label indications currently approved as Accelerated approvals with the following warning text, "Continued approval for this indication may be contingent upon verification and description of clinical benefit in confirmatory trials". This text should be present in **both** the indication and Statement description. 
9. **Preserve single-agent use when the indication specifies it.** When the approval states a therapy is given "as monotherapy" or "monotherapy", carry this into the description as "as a monotherapy". For example, "Health Canada approved trastuzumab deruxtecan as a monotherapy for the treatment of...". For HSE reimbursement approvals this is folded into the opening clause as "...has approved asciminib for reimbursement as a monotherapy treatment option for...".
10. **Reorder parenthetical qualifiers for readability** so the description reads naturally in isolation. For example, rephrasing "...locally advanced (not amenable to curative therapy) or metastatic non-small cell lung cancer (NSCLC)..." to "...locally advanced or metastatic non-small cell lung cancer (NSCLC) that is not amenable to curative therapy...".

## Per-agency opening clauses

Each source agency has a canonical opening clause. `(drug)` is the generic drug name (convention #3); `[monotherapy]` is included only when the indication specifies single-agent use (convention #9).

| Agency | Standard opening clause | Non-traditional variant |
| --- | --- | --- |
| U.S. Food and Drug Administration (FDA) | "The U.S. Food and Drug Administration granted approval to (drug)..." | Accelerated: "...granted accelerated approval to (drug)..." |
| European Medicines Agency (EMA) | "The European Medicines Agency (EMA) has authorized (drug)..." | Conditional: "...has conditionally authorized (drug)..." |
| Health Canada | "Health Canada approved (drug)..." | — |
| Health Service Executive (HSE) | "The Republic of Ireland's Health Service Executive (HSE) has approved (drug) for reimbursement as a [monotherapy] treatment option for..." | — |
| Health Products Regulatory Authority (HPRA) | "The Republic of Ireland's Health Products Regulatory Authority (HPRA) has authorized (drug)..." | — |

The FDA opener omits the "(FDA)" abbreviation; spell out the agency name in full. EMA, HSE, and HPRA introduce their abbreviation parenthetically on first mention.

## Source-specific notes

- **The Health Service Executive (HSE) is a reimbursement body, not a market-authorization regulator.** Its descriptions state that the agency "has approved (drug) for reimbursement as a [monotherapy] treatment option for...". HSE reimbursement documents also commonly carry context not present in other agencies' approvals, which should be reproduced in the description when present: required test methods (for example, "as demonstrated by a validated test method" or "This indication is specifically for patients whose tumors have been historically confirmed..."), and exclusion criteria (for example, "The therapy regimen further states that... are exclusion criteria.").

## Style-specific preferences that are currently not consistently applied

- **Always specify that approvals are for patients**. For example, regulatory language often approves indications for "adults" instead of "adult patients". 
- **The oxford comma should always be included**. This will most commonly occur when listing combination therapies.
- **Use the word "variant" instead of "mutation"** per [HGVS guidance](https://hgvs-nomenclature.org/stable/background/basics/?h=mutation#mutation-and-polymorphism). For example, writing "EGFR activating variants" instead of "EGFR activating mutations".
- **Always use HGVS prefixes for variant types**. For example, writing "BRAF p.V600E" instead of "BRAF V600E". 
- We tend to write Statement descriptions in American English, as opposed to British English. We are exploring reporting our descriptions in [other languages](https://github.com/vanallenlab/moalmanac-db/blob/reference-descriptions/referenced/descriptions.json), and can also re-localize descriptions and indication text. 
- **Un-abbreviation (convention #7) is frequently skipped for well-known gene and biomarker abbreviations.** Many descriptions leave "EGFR", "ALK", "HER2", and similar abbreviated even when the source indication spelled them out. These should be expanded on first use per convention #7.
- **EMA conditional approval phrasing varies.** Both "...has conditionally authorized (drug)..." and "...has given (drug) conditional market authorization..." appear; the former is preferred for consistency.
- **The FDA agency abbreviation "(FDA)" is applied inconsistently.** The canonical opener omits it ("The U.S. Food and Drug Administration granted approval to..."), but roughly 15% of FDA descriptions still introduce "(FDA)"; these should be normalized to the omit form.

## Examples

### No ambiguity present

[ind:fda.cyramza:0](https://dev.moalmanac.org/indications/ind:fda.cyramza:0)

| Field                 | Text                                                                                                                                                                                                                                                                                          |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Indication            | CYRAMZA is a human vascular endothelial growth factor receptor 2 (VEGFR2) antagonist indicated in combination with erlotinib, for first-line treatment of metastatic non-small cell lung cancer with epidermal growth factor receptor (EGFR) exon 19 deletions or exon 21 (p.L858R) variants. |
| Statement description | The U.S. Food and Drug Administration granted approval to ramucirumab in combination with erlotinib for the first-line treatment of patients with metastatic non-small cell lung cancer with epidermal growth factor receptor (EGFR) exon 19 deletions or exon 21 (L858R) mutations.          |

### Adding specific treatment regimens for ambiguous combination therapies

[ind:fda.yervoy:2](https://dev.moalmanac.org/indications/ind:fda.yervoy:2)

| Field | Text |
|---|---|
| Indication | YERVOY is a human cytotoxic T-lymphocyte antigen 4 (CTLA-4)-blocking antibody indicated for treatment of adult patients with metastatic or recurrent non-small cell lung cancer with no EGFR or ALK genomic tumor aberrations as first-line treatment, in combination with nivolumab and 2 cycles of platinum-doublet chemotherapy. |
| Statement description | The U.S. Food and Drug Administration granted approval to ipilimumab in combination with nivolumab and 2 cycles of platinum-doublet chemotherapy for the treatment of adult patients with metastatic or recurrent non-small cell lung cancer (NSCLC) with no EGFR or ALK genomic tumor aberrations. This indication is based on CHECKMATE-9LA (NCT03215706), a phase 3, randomized, and open-label study in which the platinum-based chemotherapy was either carboplatin and pemetrexed or cisplatin and pemetrexed for non-squamous NSCLC, or carboplatin and paclitaxel for squamous NSCLC. |

### Clarifying biomarker

[ind:fda.revuforj:1](https://dev.moalmanac.org/indications/ind:fda.revuforj:1)

| Field                 | Text                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Indication            | REVUFORJ is a menin inhibitor indicated for the treatment of relapsed or refractory acute myeloid leukemia (AML) with a susceptible nucleophosmin 1 (NPM1) mutation in adult and pediatric patients 1 year and older who have no satisfactory alternative treatment options.                                                                                                                                                                                                                                                                                                                                                                  |
| Statement description | The U.S. Food and Drug Administration granted approval to revumenib for the treatment of adult and pediatric patients 1 year and older with relapsed or refractory acute myeloid leukemia and a susceptible nucleophosmin 1 (NPM1) variant. The approval defines susceptible NPM1 mutations as those that result in a loss of the nucleolar localization signal and the insertion of a new nuclear export signal leading to the accumulation of mutant NPM1 in the cytoplasm of AML cells; the most common of such NPM1 variants in patients with AML being Types A (c.860_863dupTCTG), B (c.863_864insCATG), and D (c.863_864insCCTG). |

### Accelerated approval

[ind:fda.augtyro:1](https://dev.moalmanac.org/indications/ind:fda.augtyro:1)

| Field                 | Text                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Indication            | AUGTYRO is a kinase inhibitor indicated for the treatment of adult and pediatric patients 12 years of age and older with solid tumors that (i) have a neurotrophic tyrosine receptor kinase (NTRK) gene fusion and (ii) are locally advanced or metastatic or where surgical resection is likely to result in severe morbidity, and (iii) have progressed following treatment or have no satisfactory alternative therapy. This indication is approved under accelerated approval based on overall response rate and duration of response. Continued approval for this indication may be contingent upon verification and description of clinical benefit in confirmatory trials.                                                                                  |
| Statement description | The U.S. Food and Drug Administration granted accelerated approval to repotrectinib for the treatment of adult and pediatric patients 12 years of age and older with solid tumors that (i) have a neurotrophic tyrosine receptor kinase (NTRK) gene fusion and (ii) are locally advanced or metastatic or where surgical resection is likely to result in severe morbidity, and (iii) have progressed following treatment or have no satisfactory alternative therapy. The product label notes that this indication is approved under accelerated approval based on overall response rate and duration of response and that continued approval for this indication may be contingent upon verification and description of clinical benefit in confirmatory trials. |
