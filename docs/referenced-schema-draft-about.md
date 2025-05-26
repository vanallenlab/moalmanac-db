# Molecular Oncology Almanac db 2.0.0 (draft)
We are in the process of refactoring and updating moalmanac db to align with [GA4GH's Variant Annotation Specification (va-spec)](https://github.com/ga4gh/va-spec) and [Categorical Variant Representation Specification (Cat-VRS)](https://github.com/ga4gh/cat-vrs). Both of these specifications are in development and are following the [GA4GH Genomic Knowledge Standards (GKS) Maturity Model](https://cat-vrs.readthedocs.io/en/latest/appendices/maturity_model.html). As components of each specification moves from draft to trial and to normative maturity we will update our schema to align with their recommendations. At the moment, this version of our data schema does _not_ comply with either format. 

![in progress relationships between referenced files](assets/moalmanac-db-schema-diagram.svg)

This version of the database is under active development and, if you have any thoughts, comments, concerns, or suggestions, please contact us!

Here, we'll start preliminary documentation of our interpretation of both of these specifications and how we are implementing them.
## Table of contents
- [Why are we making these changes?](#why-are-we-making-these-changes)
- [Using a relational schema](#using-a-relational-schema)
- [Our (in progress) interpretation of va-spec](#our-in-progress-interpretation-of-va-spec)
  - [about.json](#aboutjson)
  - [biomarkers.json](#biomarkersjson)
  - [codings.json](#codingsjson)
  - [contributions.json](#contributionsjson)
  - [diseases.json](#diseasesjson)
  - [documents.json](#documentsjson)
  - [genes.json](#genesjson)
  - [indications.json](#indicationsjson)
  - [mappings.json](#mappingsjson)
  - [organizations.json](#organizationsjson)
  - [propositions.json](#propositionsjson)
  - [statements.json](#statementsjson)
  - [strengths.json](#strengthsjson)
  - [therapies.json](#therapiesjson)
  - [therapy_groups.json](#therapy_groupsjson)
# Why are we making these changes?
Most importantly, we are making this change because our current schema is something that we "just made up" throughout our original development. There is now an increasing emphasis within the field on interoperability and data standards, and we want moalmanac to both communicate with other services as well as possible while providing the most value to our users. Representing our database content within a widely used specification will increase the utility of our service.

Pragmatically, there is also technical debt associated with the current format. While we use [a flat JSON schema](../docs/sop.md), this is converted into a SQLite table for use with the [moalmanac-browser](https://github.com/vanallenlab/moalmanac-browser/tree/master/db_versions). The representation of genomic information is particularly troublesome within this format, with nested tables to store attribute definitions and attributes of each biomarker type. Code to generate the browser's sqlite table easily results in ids of assertions, sources, or features changing between the database content releases. Over the years this has caused some hiccups with adoption by some users. To complicate matters further, we store database metadata in the version of the database [used by the algorithm](https://github.com/vanallenlab/moalmanac/tree/main/datasources/moalmanac) and as a result there are three slightly different versions of our database published: this repository, the one used by our browser and accessible through the API, and by the algorithm. We would really like to simplify this but do not want to cause further hiccups for our users. It has also made expanding our API endpoints difficult.

About a year ago in January 2024, we began curating knowledge for European precision oncology approvals (more on this soon!) in the format present that [GA4GH's genomic knowledge pilot](https://gk-pilot.readthedocs.io/en/stable/index.html) used for moalmanac. Afterwards, we went back and re-curated FDA approvals from scratch, additionally curating indications involving biomarkers that are of type protein expression, wild type, mismatch repair, and homologous recombination.
# Using a relational schema
We are using a relational schema that can be dereferenced to a single JSON file using [utils/dereference.py](../utils/dereference.py). The genomic knowledge pilot separated datasources into referenced and dereferenced sources, and so we are following their recommendations for this. We can thus have each element of the specification in its own referenced json file and these contents can be mirrored into the SQLite database that will be used by the API, or other database type chosen. There are two other additional benefits that we've noticed: testing the database content is much easier because each element can be independently evaluated and curation is _much_ faster by being able to reference the appropriate record within a data type, instead of typing or copying data. In short using a relational schema better follows [Don't repeat yourself (DRY)](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) principles.
# Our (in progress) interpretation of va-spec
VA-Spec supports a wide array of [proposition types](https://va-ga4gh.readthedocs.io/en/latest/base-profiles/statement-profiles.html) but at the moment we are only utilizing Variant Therapeutic Response Study Proposition. Our current draft schema does _not_ follow va-spec and we are continuing to work to align our specification to their framework. Here, we'll go through each json file within [referenced/](../referenced/) and describe each attribute. Two common data types from [gks-core](https://github.com/ga4gh/gks-core) that are used by several data types are [extensions](https://va-ga4gh.readthedocs.io/en/latest/core-information-model/data-types.html#extension) and [mappings](https://va-ga4gh.readthedocs.io/en/latest/core-information-model/data-types.html#conceptmapping). 

**Extensions** are a way to capture information that are not directly supported by their data model. They will always have the fields `name`, `value`, and `description`. For example, our model for [diseases](#diseasesjson) has an extension that specifies if the cancer type is categorized as a solid tumor or not. 
```
"extensions": [
  {
    "name": "solid_tumor",
	"value": true,
	"description": "Boolean value for if this tumor type is categorized as a solid tumor."
  }
]
```

**Mappings** are representations of a concept in _other_ systems and, in this case, means representations of a concept outside of moalmanac. They are made up of a [coding](https://va-ga4gh.readthedocs.io/en/latest/core-information-model/data-types.html#coding) and [relation](https://www.w3.org/TR/skos-reference/#vocab) statement. [GKS core](https://github.com/ga4gh/gks-core/blob/1.x/schema/gks-core/gks-core-source.yaml) currently allows `relation` to be populated with `broadMatch`, `closeMatch`, `exactMatch`, `narrowMatch`, `relatedMatch` and at the moment moalmanac only uses either `exactMatch` or `relatedMatch`. For example, therapies are mapped to the [NCI Enterprise Vocabulary Services](https://evsexplore.semantics.cancer.gov/evsexplore/):

```
"mappings": [  
  {    
   "coding": {  
      "id": "ncit:C411",  
      "code": "C411",  
      "name": "Dacarbazine",  
      "system": "https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/",  
      "systemVersion": "25.01d"  
    },  
    "relation": "exactMatch"  
  }  
]
```

Specific extensions and mappings will be explained within their relevant data type. 

We also want to give a special thank you to Daniel Puthawala and Kori Kuzama from the Wagner lab for their help and patience as we've badgered them with questions to understand the GKS ecosystem. Their expertise and the [Wagner Lab's normalizers](https://gk-pilot.readthedocs.io/en/stable/tools.html) are excellent. 

[Return to Table of Contents](#table-of-contents)
## [about.json](../referenced/about.json) 
[about.json](../referenced/about.json) contains metadata for moalmanac db and will be a root key within the [dereferenced](../moalmanac-draft.dereferenced.json) json. Unlike every other referenced data type, it is a single dictionary containing:
- `github` (str): a url for the moalmanac-db github repository
- `name` (str): the service name, "Molecular Oncology Almanac"
- `license` (str): the license that moalmanac-db is distributed under, GPL-2.0
- `release` (str): the release that the dereferenced version of the database is under. This will eventually be the date of the corresponding content release.
- `url` (str): url for the moalmanac.org, "https://moalmanac.org"
- `last_updated` (str): date of when the database was last updated, in [ISO 8601, Y-m-d, format](https://en.wikipedia.org/wiki/ISO_8601). 

```
{  
    "github": "https://github.com/vanallenlab/moalmanac-db",  
    "name": "Molecular Oncology Almanac",  
    "license": "GPL-2.0",  
    "release": "draft",  
    "url": "https://moalmanac.org",  
    "last_updated": "2025-02-27"  
}
```
[Return to Table of Contents](#table-of-contents)
## [agents.json](../referenced/agents.json) 
[Agents](https://va-ga4gh.readthedocs.io/en/latest/core-information-model/entities/agent.html) are an entity that va-spec defines as, "...that bears some form of responsibility for an activity taking place". Currently, we are using this to attribute changes to the database content to [the Van Allen lab](https://vanallenlab.dana-farber.org). Each record is a dictionary with the following fields:
- `id` (int): an integer id for the record.
- `type` (str): "Agent", must be "Agent".
- `subtype` (str): "Person", "Organization", or "Software".
- `name` (str): a human-readable name for the Agent.
- `description` (str): A free-text description of the Agent.

We likely can combine [organizations](#organizationsjson) with this table; however, we are using agents specifically for contributions to the database content while organizations are cited for publishing [documents](#documentsjson).

```
[  
  {    
    "id": 0,  
    "type": "Agent",  
    "subtype": "organization",  
    "name": "Van Allen lab",  
    "description": "Van Allen lab, Dana-Farber Cancer Institute"  
  }  
]
```
[Return to Table of Contents](#table-of-contents)
## [biomarkers.json](../referenced/biomarkers.json) 
Biomarkers are intended to follow the [categorical variant representation specification](https://github.com/ga4gh/cat-vrs), but at the moment they only follow the ["preallocated" example](https://github.com/ga4gh/cat-vrs/blob/1.x/examples/describedVariant-ex1.yaml) and place most fields as extensions. This data type will change the most as we continue to improve this version of moalmanac-db. 

Each record is a dictionary with the fields:
- `id` (int): an integer id for the record.
- `type` (str): "CategoricalVariant", must be "CategoricalVariant".
- `name` (str): a human-readable name for the biomarker.
- `extensions` (list[dict]): list of dictionaries for extensions to this concept, or items not captured by the data model.

The following biomarker types are currently represented in this version of moalmanac-db: protein expression, somatic variant, rearrangement, wild type, germline variant, mismatch repair, microsatelite stability, copy number, copy number (arm level), homologous recombination, tumor mutational burden. Fields for biomarkers currently represented in moalmanac are largely the same as [the current versions](https://github.com/vanallenlab/moalmanac-db/blob/main/docs/sop.md#molecular-features). The following new biomarker types are represented as follows:
### Copy number (arm level)
- `chromosome` (str): chromosome location of the copy number event.
- `arm` (str): chromosome arm location of the copy number event, must be "p" or "q".
- `direction` (str): direction of copy number event, "Amplification" or "Deletion".
- `_present` (boolean): a boolean value for if the biomarker is present or absent.
### Homologous recombination
- `status` (str): homologous recombination status, "Proficient" or "Deficient".
- `_present` (boolean): a boolean value for if the biomarker is present or absent.
### Mismatch repair
- `status` (str): mismatch repair status, "Proficient" or "Deficient".
- `_present` (boolean): a boolean value for if the biomarker is present or absent.
### Protein expression
- `marker` (str): marker of interest.
- `unit` (str): unit of measurement used to describe the biomarker.
- `equality` (str): equality to compare against the biomarker's `value`.
- `value` (float): value of the marker.
- `_present` (boolean): a boolean value for if the biomarker is present or absent.
### Wild type
- `_present` (boolean): a boolean value for if the biomarker is present or absent.  

[Return to Table of Contents](#table-of-contents)
## [codings.json](../referenced/codings.json) 
[Codings](https://va-ga4gh.readthedocs.io/en/latest/core-information-model/elements/coding.html#coding) are an element that va-spec defines as: 
> A structured representation of a code for a defined concept in a terminology or code system. 

We use this element to represent concepts from other systems, such as [OncoTree](https://oncotree.mskcc.org/) and the [NCI Thesaurus](https://evsexplore.semantics.cancer.gov/). Each record is a dictionary with the following fields:
- `id` (str): an identifier for the concept mapping in the external system.
- `code` (str): a symbol uniquely associated with the concept in the external system.
- `name` (str): a human-readable name for the concept in the external system.
- `system` (str): a url for the external system.
- `systemVersion` (str): the version of the external system that the concept mapping is represented in.
- `iris` (list[str]): a list of IRIs or URLs that are associated with this coding. 

An example record from [codings.json](../referenced/codings.json):
```
[  
  {    
    "id": "oncotree:ALL",
    "code": "ALL",
    "name": "Acute Lymphoid Leukemia",
    "system": "https://oncotree.mskcc.org",
    "systemVersion": "oncotree_2021_11_02",
    "iris": [
      "https://oncotree.mskcc.org/?version=oncotree_2021_11_02&field=CODE&search=ALL"
    ]
  }  
]
```
[Return to Table of Contents](#table-of-contents)
## [contributions.json](../referenced/contributions.json) 
[Contributions](https://va-ga4gh.readthedocs.io/en/latest/core-information-model/entities/activities/contribution.html) are defined as actions taken by an [agent](#agentsjson) when modifying contents of the database. As far as we can tell from va-spec's current documentation, contributions are within the framework are attached to Data Set, Statement, Evidence Line, and Study Result. We are considering adding contributions to each data type to track changes within the database content, independently of GitHub. 

Each record is a dictionary with the fields:
- `id` (int): an integer id for the record.
- `type` (str): "Contribution", must be "Contribution".
- `agent_id` (int): the `id` referenced within [agents.json](#agents-json).
- `description` (str): A free-text description of the Agent.
- `date` (str): date of when the contribution to the database content occurred, in [ISO 8601, Y-m-d, format](https://en.wikipedia.org/wiki/ISO_8601). 

When dereferenced, the field `agent_id` will be replaced with `agent` and it will contain the relevant record from [agents](#agentsjson). 

An example record from [agents.json](../referenced/agents.json):
```
[  
  {    
    "id": 0,  
    "type": "Contribution",  
    "agent_id": 0,  
    "description": "Initial access of FDA approvals",  
    "date": "2024-10-30"  
  },
  ...
]
```

An example record from [agents.json](../referenced/agents.json), after dereferencing:
```
[  
  {    
    "id": 0,  
    "type": "Contribution",  
    "agent": {
      "id": 0,
      "type": "Agent",
      "subtype": "organization",
      "name": "Van Allen lab",
      "description": "Van Allen lab, Dana-Farber Cancer Institute"
    },  
    "description": "Initial access of FDA approvals",  
    "date": "2024-10-30"  
  },
  ...
]
```
[Return to Table of Contents](#table-of-contents)
## [diseases.json](../referenced/diseases.json)
[Diseases and cancer types](https://va-ga4gh.readthedocs.io/en/1.0.0-ballot.2024-11/core-information-model/entities/domain-entities/conditions/disease.html) are categorized within va-spec under [Condition](https://va-ga4gh.readthedocs.io/en/1.0.0-ballot.2024-11/core-information-model/entities/domain-entities/conditions/index.html) and is represented as a [mappable concept](https://github.com/ga4gh/va-spec/blob/1.0.0-ballot.2024-11/schema/va-spec/base/json/Condition). We currently have mappings to [OncoTree](https://oncotree.mskcc.org/?version=oncotree_latest_stable&field=NAME)  with plans to expand to [NCI Enterprise Vocabulary Services](https://evsexplore.semantics.cancer.gov/evsexplore/). Extensions for diseases are a boolean to state if the cancer type is a solid tumor or not.

Each record is a dictionary with the fields:
- `id` (int): an integer id for the record.
- `conceptType` (str): "Disease", the conceptType for the mappable concept.
- `name` (str): a human-readable name for the Disease.
- `primary_coding_id` (str): the `code` from [codings.json](#codingsjson) that is primarily being used to represent this concept.
- `mappings` (list): list of concept mappings (representations in other systems) of the concept. Each record within `mappings` will contain a [`coding`](#codingsjson) and `relation`.
- `extensions` (list[dict]): list of dictionaries for extensions to this concept, or items not captured by the data model.

When dereferenced, several fields will update:
- `primary_coding_id` will be replaced with `primaryCoding` and it will contain the relevant record from [codings](#codingsjson).
- `mappings` will still be called `mappings`, but each member will be replaced with the relevant record from [mappings](mappingsjson).

An example record from [diseases.json](../referenced/diseases.json):
```
{  
  "id": 15,  
  "conceptType": "Disease",  
  "name": "Colorectal Adenocarcinoma",  
  "primary_coding_id": "oncotree:COADREAD"
  "mappings": [],  
  "extensions": [  
    {      
      "name": "solid_tumor",  
      "value": true,  
      "description": "Boolean value for if this tumor type is categorized as a solid tumor."  
    }  
  ]
  },
  ...
]
```

An example record from [diseases.json](../referenced/diseases.json), after dereferencing:
```
{  
  "id": 15,  
  "conceptType": "Disease",  
  "name": "Colorectal Adenocarcinoma",  
  "primaryCoding": {      
    "coding": {  
      "id": "oncotree:COADREAD",  
      "code": "COADREAD",  
      "name": "Colorectal Adenocarcinoma",  
      "system": "https://oncotree.mskcc.org/?version=oncotree_2021_11_02&field=CODE&search=",  
      "systemVersion": "oncotree_2021_11_02"  
    },  
    "relation": "exactMatch"  
  }    
  "mappings": [],  
  "extensions": [  
    {      
      "name": "solid_tumor",  
      "value": true,  
      "description": "Boolean value for if this tumor type is categorized as a solid tumor."  
    }  
  ]
  },
  ...
]
```
[Return to Table of Contents](#table-of-contents)
## [documents.json](../referenced/documents.json)
[Documents](https://va-ga4gh.readthedocs.io/en/1.0.0-ballot.2024-11/core-information-model/entities/information-entities/document.html) are published documents that we derive database content from. This data type currently has several fields that should be converted to extensions. Each record is a dictionary with the fields: 
- `id` (str): a string id for the record, currently "doc:{organization id}.{drug_name_brand}". If citing a particular version of a drug label instead of the latest, date can be appended in ISO 8601 format; e.g., "doc:{organization id}.{drug_name_brand}.{year}-{month}-{day}".
- `type` (str): must be "Document".
- `subtype` (str): a specific type of document. At the moment, moalmanac-db only uses subtype of `Regulatory approval` or `Publication`. 
- `name` (str): a human-readable name for the document.
- `aliases` (list[str]): a list of aliases for the document. This field is not currently used.
- `citation` (str): the citation for the document.
- `company` (str): the company which produces the drug referenced in the document. 
- `drug_name_brand` (str): the brand name for the drug referenced in the document.
- `drug_name_generic` (str): the generic name for the drug referenced in the document.
- `first_published` (str): the date when the document was first published, in [ISO 8601, Y-m-d, format](https://en.wikipedia.org/wiki/ISO_8601). 
- `access_date` (str): the date when the document was accessed, in [ISO 8601, Y-m-d, format](https://en.wikipedia.org/wiki/ISO_8601). 
- `organization_id` (int): the `id` referenced within [organizations](#organizationsjson). 
- `publication_date` (str): the date that this version of the document was published, in [ISO 8601, Y-m-d, format](https://en.wikipedia.org/wiki/ISO_8601). 
- `url` (str): the url to access this version of the document.
- `url_drug` (str): the url for the document's referenced drug through [Drugs@FDA](https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm). 
- `application_number` (int): the application number for the document's referenced drug through [Drugs@FDA](https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm).

For documents of the subtype `Regulatory approval`, `name` is specified as:
```
Brand name (generic name) [document type]. Agency alias.
```

For example, for `Regulatory approvals` from the U.S. FDA:
```
"name": "Talzenna (talazoparib) [package insert]. U.S. FDA."
```

When dereferenced, the field `organization_id` will be replaced with `organization` and it will contain the relevant record from [organizations](#organizationsjson). 

An example record from [documents.json](../referenced/documents.json):
```
[  
  {    
    "id": "doc:fda.abemciclib",  
    "type": "Document",  
    "subtype": "Regulatory approval",  
    "name": "Verzenio (abemaciclib) [package insert]. U.S. FDA.",  
    "aliases": [],  
    "citation": "Eli and Lily Company. Verzenio (abemaciclib) [package insert]. U.S. Food and Drug Administration website. https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/208716s010s011lbl.pdf. Revised March 2023. Accessed October 30, 2024.",  
    "company": "Eli and Lily Company.",  
    "drug_name_brand": "Verzenio",  
    "drug_name_generic": "abemaciclib",  
    "first_published": "",  
    "access_date": "2024-10-30",  
    "organization_id": "fda",  
    "publication_date": "2023-03-03",  
    "url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/208716s010s011lbl.pdf",  
    "url_drug": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=208716",  
    "application_number": 208716  
  },
  ...
]
```

An example record from [documents.json](../referenced/documents.json), after dereferencing:
```
[  
  {    
    "id": "doc:fda.abemciclib",  
    "type": "Document",  
    "subtype": "Regulatory approval",  
    "name": "Verzenio (abemaciclib) [package insert]. U.S. FDA.",  
    "aliases": [],  
    "citation": "Eli and Lily Company. Verzenio (abemaciclib) [package insert]. U.S. Food and Drug Administration website. https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/208716s010s011lbl.pdf. Revised March 2023. Accessed October 30, 2024.",  
    "company": "Eli and Lily Company.",  
    "drug_name_brand": "Verzenio",  
    "drug_name_generic": "abemaciclib",  
    "first_published": "",  
    "access_date": "2024-10-30",  
    "organization": {
      "id": "fda",
      "name": "Food and Drug Administration",
      "description": "Regulatory agency that approves drugs for use in the United States.",
      "url": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm",
      "last_updated": "2025-04-03"
    },  
    "publication_date": "2023-03-03",  
    "url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/208716s010s011lbl.pdf",  
    "url_drug": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=208716",  
    "application_number": 208716  
  },
  ...
]
```
[Return to Table of Contents](#table-of-contents)
## [genes.json](../referenced/genes.json)
Genes are a referenced field of [biomarkers](#biomarkersjson) and is a list of dictionaries, where each dictionary is the gene as a mappable concept. Each record is abbreviated  from the from the [Wagner Lab](https://www.nationwidechildrens.org/specialties/institute-for-genomic-medicine/research-labs/wagner-lab)'s / [VICC](https://cancervariants.org/index.html)'s [gene normalizer](https://github.com/cancervariants/gene-normalization). 

Currently, mappings used for Genes are HGNC, ENSEMBL, NCI gene, and RefSeq's MANE Select transcript. The chromosomal location of the Gene is stored within extensions as `location` and `location_sortable`.

Each record is a dictionary with the fields:
- `id` (int): an integer id for the record.
- `conceptType` (str): "Gene", the conceptType for the mappable concept.
- `name` (str): a human-readable name for the gene.
- `primary_coding_id` (str): the `code` from [codings.json](#codingsjson) that is primarily being used to represent this concept.
- `mappings` (list): list of concept mappings (representations in other systems) of the concept. Each record within `mappings` will contain a [`coding`](#codingsjson) and `relation`.
- `extensions` (list[dict]): list of dictionaries for extensions to this concept, or items not captured by the data model.

When dereferenced, several fields will update:
- `primary_coding_id` will be replaced with `primaryCoding` and it will contain the relevant record from [codings](#codingsjson).
- `mappings` will still be called `mappings`, but each member will be replaced with the relevant record from [mappings](mappingsjson).

An example record from [genes.json](../referenced/genes.json):
```
[  
  {    
    "id": 0,  
    "conceptType": "Gene",  
    "primaryCode": "hgnc:76",  
    "name": "ABL1",  
    "mappings": [  
      0,
      1,
      2  
    ],    
    "extensions": [  
      {        
        "name": "location",  
        "value": "9q34.12"  
      },  
      {        
        "name": "location_sortable",  
        "value": "09q34.12"  
      }  
    ]  
  },
  ...
]
```

An example record from [genes.json](../referenced/genes.json), after dereferencing:
```
[  
  {    
    "id": 0,  
    "conceptType": "Gene",  
    "primaryCode": {        
      "coding": {  
        "id": "hgnc:76",  
        "code": "HGNC:76",  
        "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id"  
      },  
      "relation": "exactMatch"  
    },
    "name": "ABL1",  
    "mappings": [   
      {        
        "coding": {  
          "id": "ensembl:ensg00000097007",  
          "code": "ENSG00000097007",  
          "system": "https://www.ensembl.org/id"  
        },  
        "relation": "relatedMatch"  
      },  
      {        
        "coding": {  
          "id": "ncbi:25",  
          "code": "25",  
          "system": "https://www.ncbi.nlm.nih.gov/gene"  
        },  
        "relation": "relatedMatch"  
      },  
      {        
        "coding": {  
          "id": "refseq:NM_005157.6",  
          "code": "NM_005157.6",  
          "system": "https://www.ncbi.nlm.nih.gov/nuccore"  
        },  
        "relation": "relatedMatch"  
      }  
    ],    
    "extensions": [  
      {        
        "name": "location",  
        "value": "9q34.12"  
      },  
      {        
        "name": "location_sortable",  
        "value": "09q34.12"  
      }  
    ]  
  },
  ...
]
```
[Return to Table of Contents](#table-of-contents)
## [indications.json](../referenced/indications.json)
Indications are a data type only used for statements originating from `Regulatory approval` [Documents](#documents.json), specifically containing the regulatory approval _as written_ in the document. 

Indications could align with va-spec through a combination of Documents and Statements, but it seems redundant as this would result in several more documents and "nested" statements within the database contents. 

Each record is a dictionary with the following fields:
- `id` (str): a string id for the record. This will be similar to `document_id`, replacing "doc:" with "ind:" and adding a colon and integer specifying a count of indication from the document; e.g., "ind:fda.abemciclib:0"
- `document_id` (str): the `id` referenced within [documents](#documentsjson). 
- `indication` (str): the regulatory approval as written in the document.
- `initial_approval_date` (str): the date that the approval, as written, was first approved the regulatory agency, in [ISO 8601, Y-m-d, format](https://en.wikipedia.org/wiki/ISO_8601). 
- `initial_approval_url` (str): the url for the regulatory approval that this indication first appeared in.
- `description` (str): the reformatted version of the text that will be used in [propositions](#propositionsjson). This differs from indication by citing the indication as the regulatory approval prefers and may include additional information to interpret the indication, such as describing the clinical trials that the indication is based on.
- `raw_biomarkers` (str): the biomarker(s) extracted from the indication.
- `raw_cancer_type` (str): the disease extracted from the indication.
- `raw_therapeutics` (str): the therapeutic(s) extracted from the indication.

When dereferenced, the field `document_id` will be replaced with `document` and it will contain the relevant record from [documents](#documentsjson).

An example record from [indications.json](../referenced/indications.json):
```
[  
  {    
    "id": "ind:fda.abemciclib:0",  
    "document_id": "id": "doc:fda.abemciclib",
    "indication": "Verzenio is a kinase inhibitor indicated in combination with endocrine therapy (tamoxifen or an aromatase inhibitor) for the adjuvant treatment of adult patients with hormone receptor (HR)-positive, human epidermal growth factor receptor 2 (HER2)-negative, node positive, early breast cancer at high risk of recurrence.",  
    "initial_approval_date": "2023-03-03",  
    "initial_approval_url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/208716s010s011lbl.pdf",  
    "description": "The U.S. Food and Drug Administration (FDA) granted approval to abemaciclib in combination with endocrine therapy (tamoxifen or an aromatase inhibitor) for the adjuvant treatment of adult patients with hormone receptor (HR)-positive, human epidermal growth factor 2 (HER2)-negative, node positive, early breast cancer at high risk of recurrence. This indication is based on the monarchE (NCT03155997) clinical trial, which was a randomized (1:1), open-label, two cohort, multicenter study. Initial endocrine therapy received by patients included letrozole (39%), tamoxifen (31%), anastrozole (22%), or exemestane (8%).",  
    "raw_biomarkers": "HR+, HER2-negative",  
    "raw_cancer_type": "early breast cancer",  
    "raw_therapeutics": "Verzenio (abemaciclib) in combination with endocrine therapy (tamoxifen or an aromatase inhibitor)"  
  },
  ...
]
```

An example record from [indications.json](../referenced/indications.json), after dereferencing:
```
[  
  {    
    "id": "ind:fda.abemciclib:0",  
    "document_id": {
       "id": "doc:fda.abemciclib",
      "type": "Document",
      "subtype": "Regulatory approval",
      "name": "Verzenio (abemaciclib) [package insert]. FDA.",
      "aliases": [],
      "citation": "Eli and Lily Company. Verzenio (abemaciclib) [package insert]. U.S. Food and Drug Administration website. https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/208716s010s011lbl.pdf. Revised March 2023. Accessed October 30, 2024.",
      "company": "Eli and Lily Company.",
      "drug_name_brand": "Verzenio",
      "drug_name_generic": "abemaciclib",
      "first_published": "",
      "access_date": "2024-10-30",
      "organization": {
        "id": "fda",
        "name": "Food and Drug Administration",
        "description": "Regulatory agency that approves drugs for use in the United States.",
        "url": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm",
        "last_updated": "2025-04-03"
      }, 
      "publication_date": "2023-03-03",
      "url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/208716s010s011lbl.pdf",
      "url_drug": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=208716",
      "application_number": 208716
    },  
    "indication": "Verzenio is a kinase inhibitor indicated in combination with endocrine therapy (tamoxifen or an aromatase inhibitor) for the adjuvant treatment of adult patients with hormone receptor (HR)-positive, human epidermal growth factor receptor 2 (HER2)-negative, node positive, early breast cancer at high risk of recurrence.",  
    "initial_approval_date": "2023-03-03",  
    "initial_approval_url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/208716s010s011lbl.pdf",  
    "description": "The U.S. Food and Drug Administration (FDA) granted approval to abemaciclib in combination with endocrine therapy (tamoxifen or an aromatase inhibitor) for the adjuvant treatment of adult patients with hormone receptor (HR)-positive, human epidermal growth factor 2 (HER2)-negative, node positive, early breast cancer at high risk of recurrence. This indication is based on the monarchE (NCT03155997) clinical trial, which was a randomized (1:1), open-label, two cohort, multicenter study. Initial endocrine therapy received by patients included letrozole (39%), tamoxifen (31%), anastrozole (22%), or exemestane (8%).",  
    "raw_biomarkers": "HR+, HER2-negative",  
    "raw_cancer_type": "early breast cancer",  
    "raw_therapeutics": "Verzenio (abemaciclib) in combination with endocrine therapy (tamoxifen or an aromatase inhibitor)"  
  },
  ...
]
```
[Return to Table of Contents](#table-of-contents)
## [mappings.json](../referenced/mappings.json)
[Mappings](https://va-ga4gh.readthedocs.io/en/latest/core-information-model/elements/concept-mapping.html) are representations of a concept in _other_ systems and, in this case, means representations of a concept outside of moalmanac. They are made up of a [coding](https://va-ga4gh.readthedocs.io/en/latest/core-information-model/data-types.html#coding) and [relation](https://www.w3.org/TR/skos-reference/#vocab) statement. [GKS core](https://github.com/ga4gh/gks-core/blob/1.x/schema/gks-core/gks-core-source.yaml) currently allows `relation` to be populated with `broadMatch`, `closeMatch`, `exactMatch`, `narrowMatch`, `relatedMatch` and at the moment moalmanac only uses either `exactMatch` or `relatedMatch`. For example, therapies are mapped to the [NCI Enterprise Vocabulary Services](https://evsexplore.semantics.cancer.gov/evsexplore/): 

Each record is a dictionary with the following fields:
- `id` (int): an integer id for the record.
- `primary_coding_id` (str): the `code` from [codings.json](#codingsjson) that is primarily being used to represent this concept.
- `coding_id` (str): the `code` from [codings.json](#codingsjson) that is being used to represent the concept being compared to.
- `relation` (str): the relationship between the concepts between `primary_coding_id` and `coding_id`, defined using SKOS references.

Mappings will not specifically be used to dereference itself as a table. Instead, it serves a relationship table to populate the `mappings` key of other tables.

An example record from [mappings.json](../referenced/mappings.json):
```
[  
  {    
    "id": 0,
    "primary_coding_id": "hgnc:76",
    "coding_id": "ensembl:ensg00000097007",
    "relation": "exactMatch"
  }  
]
```
[Return to Table of Contents](#table-of-contents)
## [organizations.json](../referenced/organizations.json)
Organizations are not an explicit data type modeled within va-spec, but it is closely related to [agents](#agentsjson). We likely can combine this table with this [agents](#agentsjson); however, we are using agents specifically for contributions to the database content while organizations are cited for publishing [documents](#documentsjson). 

Each record is a dictionary with the following fields:
- `id` (str): a string id for the record, currently the abbreviation for the organization in lowercase.
- `name` (str): the name of the organization.
- `description` (str): a free-text description of the organization.
- `url` (str): the url within the organzation's website used to identify relevant documents.
- `last_updated` (str): the date that the organization was last curated, in [ISO 8601, Y-m-d, format](https://en.wikipedia.org/wiki/ISO_8601). 

An example record from [organizations.json](../referenced/organizations.json):
```
[  
  {    
    "id": "fda",  
    "name": "Food and Drug Administration",  
    "description": "Regulatory agency that approves drugs for use in the United States.",  
    "url": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm",  
    "last_updated": "2025-01-10"  
  }  
]
```
[Return to Table of Contents](#table-of-contents)
## [propositions.json](../referenced/propositions.json)
[Propositions](https://va-ga4gh.readthedocs.io/en/1.0.0-ballot.2024-11/base-profiles/proposition-profiles.html) are a [base profile](https://va-ga4gh.readthedocs.io/en/1.0.0-ballot.2024-11/base-profiles/index.html) of knowledge within va-spec. Specifically, propositions contain a representation of knowledge depending on the type of proposition, including: variant pathogenicity, variant oncogenicity, variant therapeutic response, diagnostics, and prognostics. Propositions differ from Statements by **not** containing information on if the knowledge is true or false, it instead if a structured way to represent the knowledge relevant for that proposition type.

At the moment, this version of moalmanac-db is only leveraging [Variant Therapeutic Response Propositions](https://va-ga4gh.readthedocs.io/en/1.0.0-ballot.2024-11/base-profiles/proposition-profiles.html#variant-therapeutic-response-proposition). 

Each record is a dictionary with the following fields:
- `id` (int): an integer id for the record.
- `type` (str): "VariantTherapeuticResponseProposition", and reflects the type of proposition.
- `predicate` (str): "predictSensitivityTo", the relationship between the subject and object of the proposition.
- `biomarkers` (list[int]): a list where each element is an `id` referenced within [biomarkers](#biomarkersjson). 
- `conditionQualifier_id` (int): the `id` referenced within [diseases](#diseasesjson).
- `therapy_id` (int): the `id` referenced within [therapies](#therapiesjson) or null, if the proposition references a [therapygroup](#therapy_groupsjson).
- `therapy_group_id` (int): the `id` referenced within [therapy_groups](#therapy_groupsjson) or null, if the proposition references a [therapy](#therapiesjson).
- `objectTherapeutic`: (list[int]): a list where each element is an `id` referenced within [therapies](#therapiesjson). 

Biomarkers are intended to be represented using the field `subjectVariant`, but at the moment they are listed as arrays with implied AND logic. Cat-vrs is currently exploring [how to model groups of variants](https://github.com/ga4gh/cat-vrs/issues/92).

When dereferenced, several fields will update:
- `biomarkers` will still be called `biomarkers`, but each member will be replaced with the relevant record from [biomarkers](#biomarkersjson).
- `conditionQualifier_id` will be replaced with `conditionQualifier` and it will contain the relevant record from [diseases](#diseasesjson).
- `therapy_id` and `therapy_group_id` will both be replaced with `objectTherapeutic` and its value will depend on if the proposition references a record from [therapies](#therapiesjson), using the value from the `therapy_id` key, or [therapy_groups](#therapy_groupsjson), using the value from the `therapy_group_id` key.

An example record from [propositions.json](../referenced/propositions.json):
```
[  
  {    
    "id": 0,  
    "type": "VariantTherapeuticResponseProposition",  
    "predicate": "predictSensitivityTo",  
    "biomarkers": [  
      1,  
      2  
    ],  
    "conditionQualifier_id": 9,  
    "subjectVariant": {}, 
    "therapy_id": null,
    "therapy_group_id": 0
  },
  ...
]
```

An example record from [propositions.json](../referenced/propositions.json), after dereferencing:
```
[
  {    
    "id": 0,  
    "type": "VariantTherapeuticResponseProposition",  
    "predicate": "predictSensitivityTo",  
    "biomarkers": [  
      {
        "id": 1,
        "type": "CategoricalVariant",
        "name": "ER positive",
        "extensions": [
          {
            "name": "biomarker_type",
            "value": "Protein expression"
          },
          {
            "name": "marker",
            "value": "Estrogen receptor (ER)"
          },
          {
            "name": "unit",
            "value": "status"
          },
          {
            "name": "equality",
            "value": "="
          },
          {
            "name": "value",
            "value": "Positive"
          },
          {
            "name": "_present",
            "value": true
          }
        ]
      },
      {
        "id": 2,
        "type": "CategoricalVariant",
        "name": "HER2-negative",
        "extensions": [
          {
            "name": "biomarker_type",
            "value": "Protein expression"
          },
          {
            "name": "marker",
            "value": "Human epidermal growth factor receptor 2 (HER2)"
          },
          {
            "name": "unit",
            "value": "status"
          },
          {
            "name": "equality",
            "value": "="
          },
          {
            "name": "value",
            "value": "Negative"
          },
          {
            "name": "_present",
            "value": true
          }
        ]
      } 
    ],  
    "conditionQualifier_id": {
      "id": 9,
      "conceptType": "Disease",
      "name": "Invasive Breast Carcinoma",
      "primaryCode": "oncotree:BRCA",
      "mappings": [
        {
          "coding": {
            "id": "oncotree:BRCA",
            "code": "BRCA",
            "name": "Invasive Breast Carcinoma",
            "system": "https://oncotree.mskcc.org/?version=oncotree_2021_11_02&field=CODE&search=",
            "systemVersion": "oncotree_2021_11_02"
          },
          "relation": "exactMatch"
        }
      ],
      "extensions": [
        {
          "name": "solid_tumor",
          "value": true,
          "description": "Boolean value for if this tumor type is categorized as a solid tumor."
        }
      ]
    },  
    "subjectVariant": {}, 
    "objectTherapeutic": {
      "id": 0,
      "membershipOperator": "AND",
      "therapies": [
        {
          "id": 99,
          "conceptType": "Drug",
          "name": "Abemaciclib",
          "primaryCode": "ncit:C97660",
          "mappings": [
            {
              "coding": {
                "id": "ncit:C97660",
                "code": "C97660",
                "name": "Abemaciclib",
                "system": "https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/",
                "systemVersion": "25.01d"
              },
              "relation": "exactMatch"
            }
          ],
          "extensions": [
            {
              "name": "therapy_strategy",
              "value": [
                "CDK4/6 inhibition"
              ],
              "description": "Associated therapeutic strategy or mechanism of action of the therapy."
            },
            {
              "name": "therapy_type",
              "value": "Targeted therapy",
              "description": "Type of cancer treatment from cancer.gov: https://www.cancer.gov/about-cancer/treatment/types"
            }
          ]
        },
        {
          "id": 119,
          "conceptType": "Drug",
          "name": "Tamoxifen",
          "primaryCode": "ncit:C62078",
          "mappings": [
            {
              "coding": {
                "id": "ncit:C62078",
                "code": "C62078",
                "name": "Tamoxifen",
                "system": "https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/",
                "systemVersion": "25.01d"
              },
              "relation": "exactMatch"
            }
          ],
          "extensions": [
            {
              "name": "therapy_strategy",
              "value": [
                "Estrogen receptor inhibition"
              ],
              "description": "Associated therapeutic strategy or mechanism of action of the therapy."
            },
            {
              "name": "therapy_type",
              "value": "Hormone therapy",
              "description": "Type of cancer treatment from cancer.gov: https://www.cancer.gov/about-cancer/treatment/types"
            }
          ]
        }
      ]
    }
  },
  ...
]
```
[Return to Table of Contents](#table-of-contents)
## [statements.json](../referenced/statementsjson)
[Statements](https://va-ga4gh.readthedocs.io/en/1.0.0-ballot.2024-11/core-information-model/entities/information-entities/statement.html) are a core Information Entity within va-spec. Each statement contains one [proposition](#propositionsjson) and provides additional information around the proposition such as a citation for it, direction of the proposition (supports or disputes), and the evidence associated with the proposition. 

Each record is a dictionary with the following fields:
- `id` (int): an integer id for the record.
- `type` (str): must be "Statement"
- `description` (str): a human-readable description of the statement, currently copied from [indications](#indicationsjson).
- `contributions` (list[int]): a list where each element is an `id` referenced within [contributions](#contributionsjson). 
- `reportedIn` (list[str]): a list where each element is an `id` referenced within [documents](#documentsjson). 
- `proposition_id` (int): the `id` referenced within [propositions](#propositionsjson). 
- `direction` (str): either "supports", "disputes", or "neutral".
- `strength_id` (int): the `id` referenced within [strengths](#strengthsjson). 
- `indication_id` (str): the `id` referenced within [indications](#indicationsjson). 

When dereferenced, several fields will update:
- `indication_id` will be replaced with `indication` and it will contain the relevant record from [indications](#indicationsjson).
- `contributions` will still be called `contributions`, but each member will be replaced with the relevant record from [contributions](#contributionsjson).
- `reportedIn` will still be called `reportedIn`, but each member will be replaced with the relevant record from [documents](#documentsjson).
- `proposition_id` will be replaced with `proposition` and it will contain the relevant record from [propositions](#propositionsjson).
- `strength_id` will be replaced with `proposition` and it will contain the relevant record from [strengths](#strengthsjson).

An example record from [statements.json](../referenced/statements.json):
```
[  
  {    
    "id": 0,  
    "type": "Statement", 
    "description": "The U.S. Food and Drug Administration (FDA) granted approval to abemaciclib in combination with endocrine therapy (tamoxifen or an aromatase inhibitor) for the adjuvant treatment of adult patients with hormone receptor (HR)-positive, human epidermal growth factor 2 (HER2)-negative, node positive, early breast cancer at high risk of recurrence. This indication is based on the monarchE (NCT03155997) clinical trial, which was a randomized (1:1), open-label, two cohort, multicenter study. Initial endocrine therapy received by patients included letrozole (39%), tamoxifen (31%), anastrozole (22%), or exemestane (8%).",  
    "contributions": [  
      0  
    ],  
    "reportedIn": [  
      "doc:fda.abemciclib" 
    ],  
    "proposition_id": 0,  
    "direction": "supports",  
    "strength_id": 0,
    "indication_id": "ind:fda.abemciclib:0"     
  },
  ...
]
```

An example record from [statements.json](../referenced/statements.json), after dereferencing:
```
[
  {
    "id": 0,
    "type": "Statement",
    "description": "The U.S. Food and Drug Administration (FDA) granted approval to abemaciclib in combination with endocrine therapy (tamoxifen or an aromatase inhibitor) for the adjuvant treatment of adult patients with hormone receptor (HR)-positive, human epidermal growth factor 2 (HER2)-negative, node positive, early breast cancer at high risk of recurrence. This indication is based on the monarchE (NCT03155997) clinical trial, which was a randomized (1:1), open-label, two cohort, multicenter study. Initial endocrine therapy received by patients included letrozole (39%), tamoxifen (31%), anastrozole (22%), or exemestane (8%).",
    "contributions": [
      {
        "id": 0,
        "type": "Contribution",
        "description": "Initial access of FDA approvals",
        "date": "2024-10-30",
        "agent": {
          "id": 0,
          "type": "Agent",
          "subtype": "organization",
          "name": "Van Allen lab",
          "description": "Van Allen lab, Dana-Farber Cancer Institute"
        }
      }
    ],
    "reportedIn": [
      {
        "id": "doc:fda.abemciclib",
        "type": "Document",
        "subtype": "Regulatory approval",
        "name": "Verzenio (abemaciclib) [package insert]. FDA.",
        "aliases": [],
        "citation": "Eli and Lily Company. Verzenio (abemaciclib) [package insert]. U.S. Food and Drug Administration website. https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/208716s010s011lbl.pdf. Revised March 2023. Accessed October 30, 2024.",
        "company": "Eli and Lily Company.",
        "drug_name_brand": "Verzenio",
        "drug_name_generic": "abemaciclib",
        "first_published": "",
        "access_date": "2024-10-30",
        "publication_date": "2023-03-03",
        "url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/208716s010s011lbl.pdf",
        "url_drug": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=208716",
        "application_number": 208716,
        "organization": {
          "id": "fda",
          "name": "Food and Drug Administration",
          "description": "Regulatory agency that approves drugs for use in the United States.",
          "url": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm",
          "last_updated": "2025-04-03"
        }
      }
    ],
    "direction": "supports",
    "indication": {
      "id": "ind:fda.abemciclib:0",
      "indication": "Verzenio is a kinase inhibitor indicated in combination with endocrine therapy (tamoxifen or an aromatase inhibitor) for the adjuvant treatment of adult patients with hormone receptor (HR)-positive, human epidermal growth factor receptor 2 (HER2)-negative, node positive, early breast cancer at high risk of recurrence.",
      "initial_approval_date": "2023-03-03",
      "initial_approval_url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/208716s010s011lbl.pdf",
      "description": "The U.S. Food and Drug Administration (FDA) granted approval to abemaciclib in combination with endocrine therapy (tamoxifen or an aromatase inhibitor) for the adjuvant treatment of adult patients with hormone receptor (HR)-positive, human epidermal growth factor 2 (HER2)-negative, node positive, early breast cancer at high risk of recurrence. This indication is based on the monarchE (NCT03155997) clinical trial, which was a randomized (1:1), open-label, two cohort, multicenter study. Initial endocrine therapy received by patients included letrozole (39%), tamoxifen (31%), anastrozole (22%), or exemestane (8%).",
      "raw_biomarkers": "HR+, HER2-negative",
      "raw_cancer_type": "early breast cancer",
      "raw_therapeutics": "Verzenio (abemaciclib) in combination with endocrine therapy (tamoxifen or an aromatase inhibitor)",
      "document": {
        "id": "doc:fda.abemciclib",
        "type": "Document",
        "subtype": "Regulatory approval",
        "name": "Verzenio (abemaciclib) [package insert]. FDA.",
        "aliases": [],
        "citation": "Eli and Lily Company. Verzenio (abemaciclib) [package insert]. U.S. Food and Drug Administration website. https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/208716s010s011lbl.pdf. Revised March 2023. Accessed October 30, 2024.",
        "company": "Eli and Lily Company.",
        "drug_name_brand": "Verzenio",
        "drug_name_generic": "abemaciclib",
        "first_published": "",
        "access_date": "2024-10-30",
        "publication_date": "2023-03-03",
        "url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/208716s010s011lbl.pdf",
        "url_drug": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=208716",
        "application_number": 208716,
        "organization": {
          "id": "fda",
          "name": "Food and Drug Administration",
          "description": "Regulatory agency that approves drugs for use in the United States.",
          "url": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm",
          "last_updated": "2025-04-03"
        }
      }
    },
    "proposition": {
      "id": 0,
      "type": "VariantTherapeuticResponseProposition",
      "predicate": "predictSensitivityTo",
      "biomarkers": [
        {
          "id": 1,
          "type": "CategoricalVariant",
          "name": "ER positive",
          "extensions": [
            {
              "name": "biomarker_type",
              "value": "Protein expression"
            },
            {
              "name": "marker",
              "value": "Estrogen receptor (ER)"
            },
            {
              "name": "unit",
              "value": "status"
            },
            {
              "name": "equality",
              "value": "="
            },
            {
              "name": "value",
              "value": "Positive"
            },
            {
              "name": "_present",
              "value": true
            }
          ]
        },
        {
          "id": 2,
          "type": "CategoricalVariant",
          "name": "HER2-negative",
          "extensions": [
            {
              "name": "biomarker_type",
              "value": "Protein expression"
            },
            {
              "name": "marker",
              "value": "Human epidermal growth factor receptor 2 (HER2)"
            },
            {
              "name": "unit",
              "value": "status"
            },
            {
              "name": "equality",
              "value": "="
            },
            {
              "name": "value",
              "value": "Negative"
            },
            {
              "name": "_present",
              "value": true
            }
          ]
        }
      ],
      "subjectVariant": {},
      "conditionQualifier": {
        "id": 9,
        "conceptType": "Disease",
        "name": "Invasive Breast Carcinoma",
        "mappings": [],
        "extensions": [
          {
            "name": "solid_tumor",
            "value": true,
            "description": "Boolean value for if this tumor type is categorized as a solid tumor."
          }
        ],
        "primaryCoding": {
          "id": "oncotree:BRCA",
          "code": "BRCA",
          "name": "Invasive Breast Carcinoma",
          "system": "https://oncotree.mskcc.org",
          "systemVersion": "oncotree_2021_11_02",
          "iris": [
            "https://oncotree.mskcc.org/?version=oncotree_2021_11_02&field=CODE&search=BRCA"
          ]
        }
      },
      "objectTherapeutic": {
        "id": 0,
        "membershipOperator": "AND",
        "therapies": [
          {
            "id": 99,
            "conceptType": "Drug",
            "name": "Abemaciclib",
            "mappings": [],
            "extensions": [
              {
                "name": "therapy_strategy",
                "value": [
                  "CDK4/6 inhibition"
                ],
                "description": "Associated therapeutic strategy or mechanism of action of the therapy."
              },
              {
                "name": "therapy_type",
                "value": "Targeted therapy",
                "description": "Type of cancer treatment from cancer.gov: https://www.cancer.gov/about-cancer/treatment/types"
              }
            ],
            "primaryCoding": {
              "id": "ncit:C97660",
              "code": "C97660",
              "name": "Abemaciclib",
              "system": "https://evsexplore.semantics.cancer.gov",
              "systemVersion": "25.01d",
              "iris": [
                "https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/C97660"
              ]
            }
          },
          {
            "id": 119,
            "conceptType": "Drug",
            "name": "Tamoxifen",
            "mappings": [],
            "extensions": [
              {
                "name": "therapy_strategy",
                "value": [
                  "Estrogen receptor inhibition"
                ],
                "description": "Associated therapeutic strategy or mechanism of action of the therapy."
              },
              {
                "name": "therapy_type",
                "value": "Hormone therapy",
                "description": "Type of cancer treatment from cancer.gov: https://www.cancer.gov/about-cancer/treatment/types"
              }
            ],
            "primaryCoding": {
              "id": "ncit:C62078",
              "code": "C62078",
              "name": "Tamoxifen",
              "system": "https://evsexplore.semantics.cancer.gov",
              "systemVersion": "25.01d",
              "iris": [
                "https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/C62078"
              ]
            }
          }
        ]
      }
    },
    "strength": {
      "id": 0,
      "conceptType": "Evidence",
      "name": "Approval",
      "mappings": [],
      "primaryCoding": {
        "id": "ncit:C25425",
        "code": "C25425",
        "name": "Approval",
        "system": "https://evsexplore.semantics.cancer.gov",
        "systemVersion": "25.01d",
        "iris": [
          "https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/C25425"
        ]
      }
    }
  },
  ...
]
```
[Return to Table of Contents](#table-of-contents)
## [strengths.json](../referenced/strengths.json)
Strengths is a field within the [Statement](https://va-ga4gh.readthedocs.io/en/latest/core-information-model/entities/information-entities/statement.html) information entity within va-spec, and is a mappable concept used to report the confidence associated with a statement. This is being used as a category to describe the underlying evidence of a statement.

Currently, mappings used for strengths are from the [NCI Enterprise Vocabulary Services](https://evsexplore.semantics.cancer.gov/evsexplore/). A mapping for Approval is present and we will expand to represent the evidence categories [currently captured within moalmanac](https://www.moalmanac.org/about).

Each record is a dictionary with the fields:
- `id` (int): an integer id for the record.
- `conceptType` (str): "Evidence strength", the conceptType for the mappable concept.
- `name` (str): a human-readable name for the strength.
- `primary_coding_id` (str): the `code` from relevant record in `mappings`'s `coding` that is primarily being used to represent this concept mapping. Each record within `mappings` will contain a [`coding`](#codingsjson) and `relation`.
- `mappings` (list): list of concept mappings (representations in other systems) of the concept.
- `extensions` (list[dict]): list of dictionaries for extensions to this concept, or items not captured by the data model.

When dereferenced, several fields will update:
- `primary_coding_id` will be replaced with `primaryCoding` and it will contain the relevant record from [codings](#codingsjson).
- `mappings` will still be called `mappings`, but each member will be replaced with the relevant record from [mappings](mappingsjson).

An example record from [strengths.json](../referenced/strengths.json):
```
[
  {
    "id": 0,
    "conceptType": "Evidence",
    "name": "Approval",
    "primary_coding_id": "ncit:C25425",
    "mappings": []
  }
]
```

An example record from [strengths.json](../referenced/strengths.json), after dereferencing:
```
[
  {
    "id": 0,
    "conceptType": "Evidence",
    "name": "Approval",
    "primaryCoding": {
      "id": "ncit:C25425",
      "code": "C25425",
      "name": "Approval",
      "system": "https://evsexplore.semantics.cancer.gov",
      "systemVersion": "25.01d",
      "iris": [
        "https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/C25425"
      ]
    },
    "mappings": []
  }
]
```
[Return to Table of Contents](#table-of-contents)
## [therapies.json](../referenced/therapies.json)
Therapies are the therapeutics associated with therapeutic sensitivity propositions. 

Currently, mappings used for therapies are from the [NCI Enterprise Vocabulary Services](https://evsexplore.semantics.cancer.gov/evsexplore/). Extensions used are `therapy_strategy`, from the current version of the database, and `therapy_type`, which is the [type of cancer treatment from cancer.gov](https://www.cancer.gov/about-cancer/treatment/types).

Each record is a dictionary with the fields:
- `id` (int): an integer id for the record.
- `conceptType` (str): "Drug", the conceptType for the mappable concept.
- `name` (str): a human-readable name for the therapy.
- `primary_coding_id` (str): the `code` from [codings.json](#codingsjson) that is primarily being used to represent this concept.
- `mappings` (list): list of concept mappings (representations in other systems) of the concept. Each record within `mappings` will contain a [`coding`](#codingsjson) and `relation`.
- `extensions` (list[dict]): list of dictionaries for extensions to this concept, or items not captured by the data model.

When dereferenced, several fields will update:
- `primary_coding_id` will be replaced with `primaryCoding` and it will contain the relevant record from [codings](#codingsjson).
- `mappings` will still be called `mappings`, but each member will be replaced with the relevant record from [mappings](mappingsjson).

An example record from [therapies.json](../referenced/therapies.json):
```
[
  {
    "id": 0,
    "conceptType": "Drug",
    "name": "Brentuximab Vedotin",
    "primary_coding_id": "ncit:C66944",
    "mappings": [],
    "extensions": [
      {
        "name": "therapy_strategy",
        "value": [
          "target CD30 antigens"
        ],
        "description": "Associated therapeutic strategy or mechanism of action of the therapy."
      },
      {
        "name": "therapy_type",
        "value": "Targeted therapy",
        "description": "Type of cancer treatment from cancer.gov: https://www.cancer.gov/about-cancer/treatment/types"
      }
    ]
  },
  ...
]
```

An example record from [therapies.json](../referenced/therapies.json), after dereferencing:
```
[
  {
    "id": 0,
    "conceptType": "Drug",
    "name": "Brentuximab Vedotin",
    "primaryCode": "ncit:C66944",
    "mappings": [
      {
        "coding": {
          "id": "ncit:C66944",
          "code": "C66944",
          "name": "Brentuximab Vedotin",
          "system": "https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/",
          "systemVersion": "25.01d"
        },
        "relation": "exactMatch"
      }
    ],
    "extensions": [
      {
        "name": "therapy_strategy",
        "value": [
          "target CD30 antigens"
        ],
        "description": "Associated therapeutic strategy or mechanism of action of the therapy."
      },
      {
        "name": "therapy_type",
        "value": "Targeted therapy",
        "description": "Type of cancer treatment from cancer.gov: https://www.cancer.gov/about-cancer/treatment/types"
      }
    ]
  },
  ...
]
```
[Return to Table of Contents](#table-of-contents)
## [therapy_groups.json](../referenced/therapy_groups.json)
Therapy groups are the sets of [therapies](#therapiesjson) associated with therapeutic sensitivity propositions. Within [Variant Therapeutic Response Propositions](https://va-ga4gh.readthedocs.io/en/1.0.0-ballot.2024-11/base-profiles/proposition-profiles.html#variant-therapeutic-response-proposition), only one object is accepted within the `objectTherapeutic` field and va-spec manages this by expecting a [single therapy](https://va-ga4gh.readthedocs.io/en/1.0.0-ballot.2024-11/core-information-model/entities/domain-entities/therapeutics/drug.html) or a [therapy group](https://va-ga4gh.readthedocs.io/en/1.0.0-ballot.2024-11/core-information-model/entities/domain-entities/therapeutics/therapy-group.html) object. 

Each record is a dictionary with the fields:
- `id` (int): an integer id for the record.
- `membershipOperator` (str): either "AND" or "OR"
- `therapies` (list[int]): a list where each element is an `id` referenced within [therapies](#therapiesjson).

When dereferenced, `therapies` will still be called `therapies`, but each member will be replaced with the relevant record from [therapies](#therapiesjson).

An example record from [therapy_groups.json](../referenced/therapy_groups.json):
```
[
  {
    "id": 0,
    "membershipOperator": "AND",
    "therapies": [
      99,
      119
    ]
  },
  ...
]
```

An example record from [therapy_groups.json](../referenced/therapy_groups.json), after dereferencing:
```
[
  {
    "id": 0,
    "membershipOperator": "AND",
    "therapies": [
      {
        "id": 99,
        "conceptType": "Drug",
        "name": "Abemaciclib",
        "primaryCode": "ncit:C97660",
        "mappings": [
          {
            "coding": {
              "id": "ncit:C97660",
              "code": "C97660",
              "name": "Abemaciclib",
              "system": "https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/",
              "systemVersion": "25.01d"
            },
            "relation": "exactMatch"
          }
        ],
        "extensions": [
          {
            "name": "therapy_strategy",
            "value": [
              "CDK4/6 inhibition"
            ],
            "description": "Associated therapeutic strategy or mechanism of action of the therapy."
          },
          {
            "name": "therapy_type",
            "value": "Targeted therapy",
            "description": "Type of cancer treatment from cancer.gov: https://www.cancer.gov/about-cancer/treatment/types"
          }
        ]
      },
      {
        "id": 119,
        "conceptType": "Drug",
        "name": "Tamoxifen",
        "primaryCode": "ncit:C62078",
        "mappings": [
          {
            "coding": {
              "id": "ncit:C62078",
              "code": "C62078",
              "name": "Tamoxifen",
              "system": "https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/",
              "systemVersion": "25.01d"
            },
            "relation": "exactMatch"
          }
        ],
        "extensions": [
          {
            "name": "therapy_strategy",
            "value": [
              "Estrogen receptor inhibition"
            ],
            "description": "Associated therapeutic strategy or mechanism of action of the therapy."
          },
          {
            "name": "therapy_type",
            "value": "Hormone therapy",
            "description": "Type of cancer treatment from cancer.gov: https://www.cancer.gov/about-cancer/treatment/types"
          }
        ]
      }
    ]
  }
  ...
]
```
[Return to Table of Contents](#table-of-contents)