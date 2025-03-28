# Molecular Oncology Almanac - Database curation Standard Operating Procedure (SOP)

## Table of Contents
* [About the Molecular Oncology Almanac](#about-the-molecular-oncology-almanac)
* [Access](#access)
    * [GitHub](#github)
    * [Molecular Oncology Almanac - Browser](#molecular-oncology-almanac---browser)
    * [Application Program Interface (API)](#application-program-interface-api)
* [Versioning and release information](#versioning-and-release-information)
* [Cataloging relationships](#cataloging-relationships)
    * [Evidence](#evidence-sources)
        * [FDA approvals](#fda-approvals)
        * [Guidelines](#guidelines)
        * [Journal articles](#journal-articles)
    * [Molecular features](#molecular-features)
        * [Aneuploidy](#aneuploidy)
        * [Copy number alterations](#copy-number-alterations)
        * [Germline variants](#germline-variants)
        * [Knockdowns](#knockdowns)
        * [Microsatellite stability](#microsatellite-stability)
        * [Mutational burden](#mutational-burden)
        * [Mutational signatures](#mutational-signatures)
        * [Rearrangements](#rearrangements)
        * [Somatic variants](#somatic-variants)
    * [Assertions](#assertions)

## About the Molecular Oncology Almanac
Molecular Oncology Almanac (MOAlmanac) is a clinical interpretation algorithm paired with an underlying knowledge base for precision oncology. The primary objective of MOAlmanac is to identify and associate molecular alterations with therapeutic sensitivity and resistance as well as disease prognosis. This is done for “first-order” genomic alterations -- individual events such as somatic variants, copy number alterations, fusions, and germline -- as well as “second-order” events -- those that are not associated with one single mutation, and may be descriptive of global processes in the tumor such as tumor mutational burden, microsatellite instability, mutational signatures, and whole-genome doubling.

The underlying database of this method is dependent on expert curation of the current body of knowledge on how molecular alterations affect clinical actionability. As the field of precision oncology grows, the quantity of research on how specific alterations affect therapeutic response and patient prognosis expands at an increasing rate. Curating the latest literature and presenting it in an accessible manner increases the abilities of clinicians and researchers alike to rapidly assess the importance of a molecular feature.

[Return to Table of Contents](#table-of-contents)

## Access
Content catalogued by the Molecular Oncology Almanac can be accessed through GitHub, the web portal, or the API.

### GitHub
The Molecular Oncology Almanac Database is maintained through [GitHub](https://github.com/vanallenlab/moalmanac-db). Releases are created for each version of the database, documented with content release notes.  

This content is then converted into an SQL database for use with the [browser](#molecular-oncology-almanac---browser) and into a document based format for use with the [method](https://github.com/vanallenlab/moalmanac), with code from their respective GitHub repositories.

### Molecular Oncology Almanac - Browser
A web based browser was created for browsing the knowledge base with Python, Flask, and SQLAlchemy and hosted on Google Compute Engine, herein referred to Molecular Oncology Almanac Browser or browser. The front page lists the total number of molecular features and assertions catalogued as well as the total number of cancer types, evidence levels, and therapies entered. A central search box allows for searching across multiple search terms such as evidence, gene, feature types, or feature type attributes (protein changes, genomic positions, etc.). The browser also features an about page, which contains a hyperlink to download the contents of the knowledge base. Users may submit entries for consideration into the database with a web form, accessible through the “Submit entry” menu item. 

The Molecular Oncology Almanac Browser is available at [https://moalmanac.org](https://moalmanac.org).

### Application Program Interface (API)
To interact with the knowledge base programmatically, an application program interface (API) was built using Python and Flask to interface with the browser’s underlying data structure. Several get requests are available to list therapies, evidence levels, or genes as well as the ability to get all or by id assertions, sources, feature definitions, features, feature attribute definitions, or feature attributes. A post request is available to suggest a new assertion to the database. 

This is available on [SwaggerHub](https://app.swaggerhub.com/apis-docs/vanallenlab/almanac-browser).

[Return to Table of Contents](#table-of-contents)

## Versioning and release information

Any changes to the Molecular Oncology Almanac database should be performed by creating a new branch within [the repository](https://github.com/vanallenlab/moalmanac-db) and performing a [pull request](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/about-pull-requests), which should be reviewed by other members of the curation team before merging and propagating.

Releases to database content are labeled based on date, in the format of `v.{Numeric year}-{Numeric month}-{Numeric day}`. 

Content changes should be summarized as a new entry in the [content changelog](CHANGELOG.md), following the [template for changes](/.github/RELEASE_TEMPLATE.md). The contents of the changelog entry should also be posted within the pull request and to describe the release, when created. 

[Return to Table of Contents](#table-of-contents)

## Cataloging relationships
Molecular Oncology Almanac catalogues relationships that assert a connection between molecular features and clinical information or action. These are organized by [feature type](#molecular-features) as [records](/molecular-oncology-almanac.json).

All records contained within the database consist of [evidence](#evidence-sources), [molecular features](#molecular-features), and the [clinical relevance](#assertions). 

### Evidence sources
Molecular Oncology Almanac is a _source centric_ knowledge base, all items must be tied to a line of evidence. Sources should be filled out with the following information unless specified as optional: 

#### Fields
- `description` (required, string), a free text description of the source and assertion.
- `source_type` (required, string), the type of source. As of this writing, four exist: Clinical trial, FDA, Guideline, and Journal. 
- `citation` (required, string), the citation for the source.
- `url` (required, string), a URL at which the source was accessed.
- `doi` (optional, string), if the source is a journal article, please include the [DOI](https://www.doi.org/).
- `pmid` (optional, integer), if a [PubMed ID (pmid)](https://www.ncbi.nlm.nih.gov/pmc/pmctopmid/) exists for the source, please include it. 
- `nct` (optional, string), if the source is a clinical trial, please include the [NCT code](https://clinicaltrials.gov/ct2/help/glossary/ct-identifier-nct#:~:text=A%20unique%20identification%20code%20given,known%20as%20the%20NCT%20Number.).  
- `publication_date` (required, date), the date in which the source was published in `YYYY-MM-DD` format
- `last_updated` (required, date), the date in which the entry was last updated in `YYYY-MM-DD` format

#### Types of sources
The Molecular Oncology Almanac database primarily cites FDA approvals, clinical guidelines, and journal articles. 

##### FDA approvals
FDA approvals are cataloged by their package insert, which can be searched for on the [Drugs @ FDA web page](https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm). Drugs are catalogued on this website by their brand name. When viewing a drug, click the `Labels for...` drop-down menu and select `Label (PDF)` under "Letters, Reviews, Labels, Patient Package Insert" for the latest date, or date of interest. 

Here, particular areas of note are 
- The brand and generic name
- INDICATIONS AND USAGE
- The revised date
- CLINICAL STUDIES
- MEDICATION GUIDE

The brand and generic name are needed to cite the source properly and the generic name should be catalogued in the database under `therapy_name`. The section titled INDICATION AND USAGE will specify the indication of approval as well as provide language which can be used in the description. 

The PDF should be saved as `{revised year}-{revised month}-{generic drug name}.pdf` in the `database/fda-labels` folder. 

You can stay up to date on FDA approvals by visiting or subscribing to:
- [FDA press announcements](https://www.fda.gov/news-events/fda-newsroom/press-announcements)
- [FDA Hematology/Oncology (Cancer) Approvals & Safety Notifications](https://www.fda.gov/drugs/resources-information-approved-drugs/hematologyoncology-cancer-approvals-safety-notifications), a summary list of all approvals by date.
- [FDA Oncology on Twitter (@FDAOncology)](https://twitter.com/FDAOncology)

###### Fields
FDA approvals will complete fields as follows,
- `description`, see below
- `source_type` with `FDA`
- `citation`, see below
- `url`, with the URL from the package insert
- `last_updated`, with the last updated time
- `doi`, `pmid`, and `nct` will be left blank

The description for an FDA assertion should follow this template, 
> The U.S. Food and Drug Administration (FDA) granted {accelerated, if applicable} to {generic name} {text from INDICATIONS AND USAGE}. 

For example,
> The U.S. Food and Drug Administration (FDA) granted accelerated approval to tazemetostat, an EZH2 inhibitor, for adult patients with relapsed or refactory (R/R) follicular lymphoma (FL) whose tumors are positive for an EZH2 mutation as detected by an FDA-approved test and who have received at least 2 prior systemic therapies, and for adult patients with R/R FL who have no satisfactory alternative treatment options.

The citation for an FDA package insert should be [described as](https://mdanderson.libanswers.com/faq/26246),
> {Manufacturer}. {Brand name of medicine} ({generic name of medicine}) [package insert]. U.S. Food and Drug Administration website. https://www.{URL of package insert}. Revised {month date} {year date}. Accessed {month date} {day date}, {year date}.

For example,
> Epizyme, Inc. Tazverik (tazemetostat) [package insert]. U.S. Food and Drug Administration website. https://www.accessdata.fda.gov/drugsatfda_docs/label/2020/213400s000lbl.pdf. Revised June 2020. Accessed November 4th, 2020.

[Return to Table of Contents](#table-of-contents)

##### Guidelines
PDFs should be saved as `{publication year}.{version}-{tumor type}.pdf` in the `database/guidelines` folder. 

###### Fields
Guidelines will complete fields as follows,
- `description`, see below 
- `source_type` with `Guideline`
- `citation`, see below
- `url`, is a URL to access the PDF containing the cliniacl guideline
- `last_updated`, with the last updated time
- `doi`, `pmid`, and `nct` will be left blank

The description for guidelines should brief readers on the relationship, following the [NCCN's referencing guidance](https://www.nccn.org/docs/default-source/business-policy/nccn-referencing-guidance.pdf), 
> [Generic name (brand name)] is recommended by the National Comprehensive Cancer Network® (NCCN®) as a treatment option for [setting and cancer type]

The citation for guidelines should follow the [NCCN's referencing guidance](https://www.nccn.org/docs/default-source/business-policy/nccn-referencing-guidance.pdf): 
> Referenced with permission from the NCCN Clinical Practice Guidelines in Oncology (NCCN Guidelines®) for Guideline Name V.X.202X. © National Comprehensive Cancer Network, Inc. 202X. All rights reserved. Accessed Month and Day, Year]. To view the most recent and complete version of the guideline, go online to NCCN.org.

For example,
> Referenced with permission from the NCCN Clinical Practice Guidelines in Oncology (NCCN Guidelines®) for Myelodysplastic Syndromes V.2.2023. © National Comprehensive Cancer Network, Inc. 2023. All rights reserved. Accessed November 2, 2023. To view the most recent and complete version of the guideline, go online to NCCN.org.

[Return to Table of Contents](#table-of-contents)

##### Journal articles
PDFs should be saved as `{publication year}-{first author last name}.pdf` in the `database/papers` folder. In the event that another paper is already named by this convention, a modifier may be added to the filename, such as adding a main idea after another dash; for example, `2014-VanAllen-ERCC2.pdf`.

###### Fields
Journal articles will complete fields as follows,
- `description`, see below 
- `source_type` with `Journal`
- `citation`, see below
- `url`, is formatted based on the DOI; for example, `https://doi.org/{doi}`
- `last_updated`, with the last updated time
- `doi`, contains the Digital Object Identifier (DOI) assigned to the article. All articles will have an associated DOI.
- `pmid`, with the PubMed ID for the article, if it exists
- `nct`, with the National Clinical Trial code if the article is related to a clinical trial. Otherwise this field may be left blank.

The description for journal articles should contain a few sentences briefing readers of the assertion(s) made in the publication. These will be displayed in the clinical actionability reports produced by the method. For example, 
> BRAF V600E mutations were associated with sensitivity to the BRAF inhibitor PLX-4032 in a study of 109 microdissected pancreatic ductal adenocarcinoma patients.

The citation for journal articles should follow the [American Medical Association (AMA)](https://owl.purdue.edu/owl/research_and_citation/ama_style/index.html) style format. [Online tools](https://citation.crosscite.org/) exist to generate such citations from PubMed IDs, URLs, or DOIs, but please double check the entries. 

For example, 
> Witkiewicz AK, Mcmillan EA, Balaji U, et al. Whole-exome sequencing of pancreatic cancer defines genetic diversity and therapeutic targets. Nat Commun. 2015;6:6744.

[Return to Table of Contents](#table-of-contents)

### Molecular features
Molecular Oncology Almanac catalogues several feature types that are associated with clinical relevance. Each catalogued relationship is associated with at least one molecular feature. Fields required are specific to each feature type, and are defined below. For example, copy number alterations are defined by a gene, direction, and cytoband. 

#### Types of molecular features
The following feature types are currently cataloged in our knowledge base: 
- [Aneuploidy](#aneuploidy)
- [Copy number alterations](#copy-number-alterations)
- [Germline variants](#germline-variants)
- [Knockdowns](#knockdowns)
- [Microsatellite stability](#microsatellite-stability)
- [Mutational burden](#mutational-burden)
- [Mutational signatures](#mutational-signatures)
- [Rearrangements](#rearrangements)
- [Somatic variants](#somatic-variants)

[Return to Table of Contents](#table-of-contents)

##### Aneuploidy
Aneuploidy captures genome-wide events such as whole-genome doubling. 

###### Fields
Molecular data for aneuploidy events should be captured in the following field,
- `event` (required, string), the type of aneuploidy event being described

For example, 
> {'event': 'Whole-genome doubling'}

[Return to Table of Contents](#table-of-contents)

##### Copy number alterations
Copy number alterations capture changes to the number of copies of a particular gene present in the genome of an individual. 

###### Fields
Molecular data for copy number alterations should be captured in the following fields,
- `gene` (required, string), Hugo gene symbol associated with the alteration
- `cytoband` (optional, string), cytoband associated with the alteration
- `direction` (optional, string), direction of the alteration; `Amplification` or `Deletion`

For example,
> {'gene': 'CCND1', 'cytoband': '11p13', 'direction': 'Amplification'}

[Return to Table of Contents](#table-of-contents)

##### Germline variants
Germline variants are mutations present within a patient's inherited genome. The fields are largely similar to those required for [somatic variants](#somatic-variants). MOAlmanac follows guidelines specificed by the [Sequence Variant Nomenclature](https://varnomen.hgvs.org/). 

###### Fields
Molecular data for germline variants should be captured in the following fields,
- `gene` (required, string), Hugo gene symbol associated with the variant
- `exon` (optional, integer), exon number within gene associated with the variant's genomic location
- `chromosome` (optional, integer), chromosome associated with the variant's genomic location
- `start_position` (optional, integer), lowest numeric position of variant on the genomic reference sequence
- `end_position` (optional, integer), highest numeric position of the variant on the genomic reference sequence
- `reference_allele` (optional, string), the plus strand reference allele at this position
- `alternate_allele` (optional, string), the discovery allele
- `cdna_change` (optional, string), relative positive of the base pair in the cDNA sequence as a fraction
- `protein_change` (optional, string), relative position of affected amino acid in the protein
- `variant_annotation` (optional, string), translational effect of the variant allele
- `rsid` (optional, string), the rs-ID from the dbSNP database
- `pathogenic` (optional, boolean), integer `1` if the citation reports the variant as pathogenic and otherwise left blank

For example,
> {'gene': 'POLE2', 'exon': '17', 'chromosome': '14', 'start_position': '50117073', 'end_position': '50117073', 'reference_allele': '-', 'alternate_allele': 'A', 'cdna_change': 'c.1406dup', 'protein_change', 'p.L469Ffs*17', 'variant_annotation': 'Frameshift', 'rsid': 'rs776517397', 'pathogenic': ''}

[Return to Table of Contents](#table-of-contents)

##### Knockdowns
Knockdowns are an experimental technique to reduce expression of a gene. 

###### Fields
Molecular data for knockdowns should be captured in the following fields,
- `gene` (required, string), Hugo gene symbol associated with the knockdown
- `technique` (required, string), specific protocol or technique reported by the source that was used to perform the experiment

For example,
> {'gene': 'ATM', 'technique': 'shRNA'}

[Return to Table of Contents](#table-of-contents)

##### Microsatellite stability
The number of repeated DNA bases within a microsatellite](https://www.cancer.gov/publications/dictionaries/cancer-terms/def/microsatellite-instability) may differ from the inherited genome in some cancers, and occurs when mismatch repair is malfunctioning. This phenomena is called microsatellite instability due to the not stable length of microsatellites. 

###### Fields
Molecular data for microsatellite events should be captured in the following fields,
- `status` (required, string), the test result from an MSI screening - MSI-High (MSI-H), MSI-Low (MSI-L), or MSI-Stable (MSS)

For example,
> {'status': 'MSI-High'} 

[Return to Table of Contents](#table-of-contents)

##### Mutational burden
The number of coding somatic variants per megabase is of interest due to reported response to immunotherapy. This metric is calculated by dividing the number of called nonsynonymous somatic variants by the number of bases that were evaluated for variant. The denominator should also reflect bases [that were sufficiently powered](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3833702/) to call variants at their location.  

Reporting of tumor mutational burden is [not standardized and is impacted by the sequencing modality](https://pubmed.ncbi.nlm.nih.gov/31832578/). While most sources report TMB categorically (e.g., High or Low), sources differ by how they categorize. Some may report a minimum number of mutations, others the mutations per megabase, or sometimes only share the categorical call. 

###### Fields
Molecular data for tumor mutational burden should be captured in the following fields,
- `classification` (required, string), `High` or `Low`
- `minimum_mutations` (optional, integer), an integer value of the minimum number of mutations required to be classified as tumor mutational burden high (TMB High) by the citation
- `mutations_per_mb` (optional, integer), an integer or float value of the minimum number of mutations per megabase required to be classified as tumor mutational burden high (TMB High) by the citation

For example,
> {'classification': 'High', 'mutations_per_mb': '10'}

[Return to Table of Contents](#table-of-contents)

##### Mutational signatures
Considering the type of substitution (e.g., C>A, C>T, T>G) along with the immediate neighboring bases results in 96 possible trinucleotide contexts for somatic variants. The patterns of somatic variation that occur within these trinucleotide contexts [has been shown to be associated with mutational processes in cancer](https://pubmed.ncbi.nlm.nih.gov/23945592/), and have been given the name mutational signatures. The Molecular Oncology Almanac utilizes mutational signatures [reported by COSMIC](https://cancer.sanger.ac.uk/signatures/), and currently supports single base substitutions (SBS) signatures from version 3.4. 

###### Fields
Molecular data for mutational signatures should be captured in the following fields,
- `cosmic_signature` (required, string), the string associated with the mutational signature based on [COSMIC's reporting](https://cancer.sanger.ac.uk/signatures/signatures/sbs/), either as reported by the citation or mapped from a prior version. 

[Return to Table of Contents](#table-of-contents)

##### Rearrangements
Rearrangements change the structure of chromosomes and can be accomplished through a variety of mechanisms such as deletions, duplications, inversions, and translocations, the last of which may result in a fusion if it is involves more than one gene.

###### Fields
Molecular data for rearrangements should be captured in the following fields,
- `gene1` (required, string), 5' gene involved in the rearrangement
- `gene2` (optional, string), 3' gene involved in the rearrangement
- `rearrangement_type` (optional, string), type of rearrangement - Fusion or Translocation
- `locus` (optional, string), genomic location of translocation

For example,
> {'gene1': 'BCR', 'gene2': 'ABL1', 'rearrangement_type': 'Fusion'}

[Return to Table of Contents](#table-of-contents)

##### Somatic variants
Somatic variants are mutations that are not present in a patient's inherited genome. The fields are largely similar to those required for [germline variants](#germline-variants). MOAlmanac follows guidelines specificed by the [Sequence Variant Nomenclature](https://varnomen.hgvs.org/). 

###### Fields
Molecular data for germline variants should be captured in the following fields,
- `gene` (required, string), Hugo gene symbol associated with the variant
- `exon` (optional, integer), exon number within gene associated with the variant's genomic location
- `chromosome` (optional, string), chromosome associated with the variant's genomic location
- `start_position` (optional, integer), lowest numeric position of variant on the genomic reference sequence
- `end_position` (optional, integer), highest numeric position of the variant on the genomic reference sequence
- `reference_allele` (optional, string), the plus strand reference allele at this position
- `alternate_allele` (optional, string), the discovery allele
- `cdna_change` (optional, string), relative positive of the base pair in the cDNA sequence as a fraction
- `protein_change` (optional, string), relative position of affected amino acid in the protein
- `variant_annotation` (optional, string), translational effect of the variant allele
- `rsid` (optional, string), the rs-ID from the dbSNP database

For example,
> {'gene': 'EGFR', 'exon': '20', 'chromosome': '7', 'start_position': '55249071', 'end_position': '55249071', 'reference_allele': 'C', 'alternate_allele': 'T', 'cdna_change': 'c.2369C>T', 'protein_change', 'p.T790M', 'variant_annotation': 'Missense', 'rsid': 'rs121434569'}

[Return to Table of Contents](#table-of-contents)

### Assertions
The assertion of a relationship describes the claim made by a source and connects the evidence to a molecular feature.

#### Fields
- `predictive_implication` (required, string), categorical value to describe the evidence source. As of this writing, six exist: FDA-Approval, Guideline, Clinical trial, Clinical evidence, Preclinical evidence, Inferential evidence. These are explained and described on the [moalmanac browser about page](https://moalmanac.org/about).
- `disease` (optional, string), related tumor type as written in the associated source
- `context` (optional, string), clinical context of the assertion as written in the associated source
- `oncotree_term` (optional, string), appropriate [Oncotree](http://oncotree.mskcc.org/#/home) term for a described `disease`
- `oncotree_code` (optional, string), appropriate [Oncotree](http://oncotree.mskcc.org/#/home) code for a described `disease`
- `therapy_name` (optional, string), associated with therapeutic sensitivity or resistance. The generic drug name should be used, if applicable, and catalogued as a proper noun. Required for assertions related to therapeutic sensitivity or resistance. In the case that an assertion contains two or more therapies, join them into a single string with ` + ` with both items capitalized; for example, `Dabrafenib + Trametinib`. Multiple therapies should be listed in alphabetical order.
- `therapy_strategy` (optional, string), associated therapeutic strategy or mechanism of action of the assertion. Required for assertions related to therapeutic sensitivity or resistance. In the case that an assertion contains two or more therapies or a utilized therapeutic strategy has multiple mechanisms, join them into a single string with ` + ` with both items capitalized; for example, `CDK4/6 inhibition + MEK inhibition`. Multiple strategies should correspond to the order of the listed therapies. Multiple strategies associated with a single therapy should be listed in alphabetical order.
- `therapy_type` (optional, string), categorical value for the therapy type of the associated therapy based on the categories presented by the [National Institute of Health](https://www.cancer.gov/about-cancer/treatment/types). As of this writing, we have catalogued: `Targeted therapy`, `Immunotherapy`, `Chemotherapy`, `Radiation therapy`, `Hormone therapy`. `Combination therapy` is entered for any therapies that utilize two or more therapy types; for example, `Dabrafenib + Trametinib` is catalogued as a `Targeted therapy` while `Ipilimumab + Vemurafenib` is catalogued as a `Combination therapy`. 
- `therapy_sensitivity` (optional, integer), `1` if the relationship asserts sensitive to a therapy, `0` if the relationship asserts not sensitive to a therapy, and blank otherwise.
- `therapy_resistance` (optional, integer), `1` if the relationship asserts resistance to a therapy, `0` if the relationship asserts not resistive to a therapy, and blank otherwise.
- `favorable_prognosis` (optional, integer), `1` if the relationship asserts a disease prognosis that is favorable, `0` if the relationship asserts a disease prognosis that is not favorable, and blank otherwise
- `_deprecated` (optional, boolean), `false` is the relationship is still active within the database, `true` if the relationship has been deprecated and will thus not show up on [https://moalmanac.org](https://moalmanac.org) or through the API.
- `assertion_id` (required, integer), integer value corresponding to the `assertion_id` from the `assertions` endpoint at [https://moalmanac.org/api/assertions](https://moalmanac.org/api/assertions).
- `feature_id` (required, integer), integer value corresponding to the `feature_id` from the `assertions` endpoint at [https://moalmanac.org/api/assertions](https://moalmanac.org/api/assertions).
- `source_id` (required, integer), integer value corresponding to the `source_id` from the `assertions` endpoint at [https://moalmanac.org/api/assertions](https://moalmanac.org/api/assertions).
- `therapy_name_mappings` (optional, list), mappings for `therapy_name` to the [NCI thesaurus](https://evsexplore.semantics.cancer.gov/evsexplore/), if possible. This field is _not_ included in the API or [https://moalmanac.org](https://moalmanac.org). Represented as a [ConceptMapping](https://va-ga4gh.readthedocs.io/en/latest/core-information-model/data-types.html#conceptmapping) from [GA4GH's Variant Annotation Specification](https://github.com/ga4gh/va-spec).

[Return to Table of Contents](#table-of-contents)
