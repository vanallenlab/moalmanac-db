# Molecular Oncology Almanac - Database curation Standard Operating Procedure (SOP)

## Table of Contents
* [About the Molecular Oncology Almanac](#about-the-molecular-oncology-almanac)
* [Access](#access)
    * [Github](#github)
    * [Molecular Oncology Almanac - Browser](#molecular-oncology-almanac---browser)
    * [Application Program Interface (API)](#application-program-interface-api)
* [Versioning and release information](#versioning-and-release-information)
* [Cataloging assertions](#cataloging-relationships)
    * [Evidence](#evidence-sources)
      * [FDA approvals](#fda-approvals)
      * [Guidelines](#guidelines)
      * [Abstracts and journal articles](#abstracts-and-journal-articles)
    * [Molecular features](#molecular-features)
    * [Assertions](#assertions)

## About the Molecular Oncology Almanac
Molecular Oncology Almanac (MOAlmanac) is a clinical interpretation algorithm paired with an underlying knowledge base for precision oncology. The primary objective of MOAlmanac is to identify and associate molecular alterations with therapeutic sensitivity and resistance as well as disease prognosis. This is done for “first-order” genomic alterations -- individual events such as somatic variants, copy number alterations, fusions, and germline -- as well as “second-order” events -- those that are not associated with one single mutation, and may be descriptive of global processes in the tumor such as tumor mutational burden, microsatellite instability, mutational signatures, and whole-genome doubling.

The underlying database of this method is dependent on expert curation of the current body of knowledge on how molecular alterations affect clinical actionability. As the field of precision oncology grows, the quantity of research on how specific alterations affect therapeutic response and patient prognosis expands at an increasing rate. Curating the latest literature and presenting it in an accessible manner increases the abilities of clinicians and researchers alike to rapidly assess the importance of a molecular feature.

[Return to Table of Contents](#table-of-contents)

## Access
Content catalogued by the Molecular Oncology Almanac can be accessed through Github, the web portal, or the API.

### Github
The Molecular Oncology Almanac Database is maintained through [Github](https://github.com/vanallenlab/moalmanac-db). Releases are created for each version of the database, documented with content release notes.  

This content is then converted into an SQL database for use with the [browser](#molecular-oncology-almanac---browser) and into a document based format for use with the [method](https://github.com/vanallenlab/moalmanac), with code from their respective Github repositories.

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

Content changes should be summarized as a new entry in the [content changelog](/docs/content-changelog.md), following the [template for changes](/docs/template-content-changelog.md). The contents of the changelog entry should also be posted within the pull request and to describe the release, when created. 

[Return to Table of Contents](#table-of-contents)

## Cataloging relationships
Molecular Oncology Almanac catalogues relationships which assert a connection between molecular features and clinical information or action. These are organized by [feature type](#molecular-features) within the [content](/content/) folder of this repository as tab delimited files. 

### Evidence sources

Molecular Oncology Almanac is a _source centric_ knowledge base, all items must be tied to a line of evidence. Sources should be filled out with the following information unless specified as optional: 

#### Fields
- `description`, a free text description of the source and assertion.
- `source_type`, the type of source. As of this writing, four exist: Abstract, Clinical trial, FDA, Guideline, and Journal. 
- `citation`, the citation for the source.
- `url`, a URL at which the source was accessed.
- `doi` (optional), if the source is an abstract or journal article, please include the [DOI](https://www.doi.org/).
- `pmid` (optional), if a [PubMed ID (pmid)](https://www.ncbi.nlm.nih.gov/pmc/pmctopmid/) exists for the source, please include it. 
- `nct` (optional), if the source is a clinical trial, please include the [NCT code](https://clinicaltrials.gov/ct2/help/glossary/ct-identifier-nct#:~:text=A%20unique%20identification%20code%20given,known%20as%20the%20NCT%20Number.).  
- `last_updated`, the date in which the entry was last updated. 

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
- [FDA Hematology/Oncology (Cancer) Approvals & Safety Notifications](https://www.fda.gov/drugs/resources-information-approved-drugs/hematologyoncology-cancer-approvals-safety-notifications), a summary list of all approvals by year.
- [FDA Oncology on Twitter (@FDAOncology)](https://twitter.com/FDAOncology)
- [American Association of Cancer Research (AACR) alerts]()

###### Populating fields
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

###### Populating fields
Guidelines will complete fields as follows,
- `description`, see below 
- `source_type` with `Guideline`
- `citation`, see below
- `url`, is a URL to access the PDF containing the cliniacl guideline
- `last_updated`, with the last updated time
- `doi`, `pmid`, and `nct` will be left blank

The description for guidelines should brief readers on the assertion(s) made in the publication. For example, 
> Translocations predict sensitivity to tyrosine kinase inhibitors such as imatinib, dasatinib, and nilotinib. Secondary mutations can cause resistance to these agents. Dasatinib or Bosutinib are second-line and subsequent therapies for cytogenetic or hematologic resistance to TKIs.

The citation for guidelines should follow the [American Medical Association (AMA)](https://mdanderson.libanswers.com/faq/26180) style format:
> {Source}. {Tumor type} (Version {version number}.{year}). {URL}. Accessed {month date} {day date}, {year date}.

For example,
> National Comprehensive Cancer Network. Chronic Myelogenous Leukemia (Version 1.2016). https://www.nccn.org/professionals/physician_gls/pdf/cml.pdf. Accessed November 5, 2016.

[Return to Table of Contents](#table-of-contents)

##### Abstracts and Journal articles
PDFs should be saved as `{publication year}-{first author last name}.pdf` in the `database/papers` folder. In the event that another paper is already named by this convention, a modifier may be added to the filename, such as adding a main idea after another dash; for example, `2014-VanAllen-ERCC2.pdf`.

###### Populating fields
Abstracts and journal articles will complete fields as follows,
- `description`, see below 
- `source_type` with `Journal`
- `citation`, see below
- `url`, is formatted based on the DOI; for example, `https://doi.org/{doi}`
- `last_updated`, with the last updated time
- `doi`, contains the Digital Object Identifier (DOI) assigned to the article. All articles will have an associated DOI.
- `pmid`, with the PubMed ID for the article, if it exists
- `nct`, with the National Clinical Trial code if the article is related to a clinical trial. Otherwise this field may be left blank.

The description for abstracts or journal articles should contain a few sentences briefing readers of the assertion(s) made in the publication. These will be displayed in the clinical actionability reports produced by the method. For example, 
> BRAF V600E mutations were associated with sensitivity to the BRAF inhibitor PLX-4032 in a study of 109 microdissected pancreatic ductal adenocarcinoma patients.

The citation for abstracts or journal articles should follow the [American Medical Association (AMA)](https://owl.purdue.edu/owl/research_and_citation/ama_style/index.html) style format. [Online tools](https://citation.crosscite.org/) exist to generate such citations from PubMed IDs, URLs, or DOIs, but please double check the entries. 

For example, 
> Witkiewicz AK, Mcmillan EA, Balaji U, et al. Whole-exome sequencing of pancreatic cancer defines genetic diversity and therapeutic targets. Nat Commun. 2015;6:6744.

[Return to Table of Contents](#table-of-contents)

### Molecular features
Molecular Oncology Almanac catalogues several feature types that are associated with clinical relevance. Each catalogued relationship is associated with at least one molecular feature. Fields associated with each type of molecular feature (feature type) are defined in the database/feature_definitions.tsv file. For example, copy number alterations are defined by a gene, direction, and cytoband. Relationships are entered into the appropriate feature type file present in the [content](/content/) folder of this repository. Molecular Oncology Almanac currently catalogues the following feature types:
- [Aneuploidy](/content/copy_number.tsv)
- [Copy number alterations](/content/copy_number.tsv)
- [Germline variants](/content/gerlmine_variant.tsv)
- [Knockdowns](/content/knockdown.tsv)
- [Microsatellite stability](/content/microsatellite_stability.tsv)
- [Mutational burden](/content/mutational_burden.tsv)
- [Mutational signatures](/content/mutational_signature.tsv)
- [Neoantigen burden](/content/neoantigen_burden.tsv)
- [Rearrangements](/content/rearrangement.tsv)
- [Silencing](/content/silencing.tsv)
- [Somatic variants](/content/somatic_variant.tsv)

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
- `therapy_sensitivity` (optional, int), `1` if the relationship asserts sensitive to a therapy, `0` if the relationship asserts not sensitive to a therapy, and blank otherwise.
- `therapy_resistance` (optional, int), `1` if the relationship asserts resistance to a therapy, `0` if the relationship asserts not resistive to a therapy, and blank otherwise.
- `favorable_prognosis` (optional, int), `1` if the relationship asserts a disease prognosis that is favorable, `0` if the relationship asserts a disease prognosis that is not favorable, and blank otherwise

[Return to Table of Contents](#table-of-contents)
