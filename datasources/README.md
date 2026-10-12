Datasources used for codings. Documentation in this README are written as if the scripts are being run from the repository's root directory.

## NCI Thesaurus

The [NCI Thesaurus](https://ncithesaurus.nci.nih.gov) is used for codings of diseases, drugs, and other concepts. The flat file archive for the given NCI Thesaurus version is downloaded from the [NCI EVS FTP archive](https://evs.nci.nih.gov/ftp1/NCI_Thesaurus/archive/), extracted, and written to datasources/{version}_Thesaurus.txt.

### Usage

Required arguments:

```bash
--version, -v <string>  NCI Thesaurus version to download; e.g., "26.08e"
```

Example:

```bash
python datasources/scripts/download_nci_thesaurus.py --version 26.08e
```

## OncoTree

[OncoTree](https://oncotree.mskcc.org) is used for secondary codings of cancer types. Specifically, the [/api/tumorTypes](https://oncotree.mskcc.org/swagger/index.html#/TumorTypes/get_api_tumorTypes) (flat) endpoint or the [/api/tumorTypes/tree](https://oncotree.mskcc.org/swagger/index.html#/TumorTypes/get_api_tumorTypes_tree) (tree) endpoint are used for the given OncoTree version from the public OncoTree API. The response is written to datasources/{version}_{mode}.json.

### Usage

Required arguments:

```bash
--mode, -m    <string>  OncoTree endpoint; choices = "flat" or "tree"
--version, -v <string<  OncoTree version to download; e.g., "oncotree_2025_10_03"
```

Example:

```bash
python datasources/scripts/download_oncotree.py --mode flat --version oncotree_2025_10_03
```

## RefSeq

[RefSeq](https://www.ncbi.nlm.nih.gov/refseq/) records are used to generate sequence references, sequence locations, and exon coordinates for genes. Records are downloaded for a gene's transcript and the transcript's protein product from [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) and written to datasources/refseq/. Accessions must include their version; e.g., "NM_005228.5", not "NM_005228". An existing file for the same accession will be overwritten.

NCBI limits requests without an API key to three per second. To use an [NCBI API key](https://support.nlm.nih.gov/kbArticle/?pn=KA-05317), set the `NCBI_API_KEY` environment variable and it will be passed with each request.

### Transcript GenBank flat file

The GenBank flat file for a transcript is downloaded from the [EFetch](https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.EFetch) endpoint of the nuccore database and written to datasources/refseq/{accession}.gb.

The file is the source of exon coordinates. Its `exon` features give each exon's start and end on the transcript, which become one sequence location per exon in referenced/sequence_locations.json and are listed in the gene's `transcript_exons`. Its `CDS` feature gives where the coding sequence starts and ends on the transcript, which sets the gene's `cds_start`, is used to convert each coding exon's transcript coordinates to protein coordinates (the gene's `protein_product_exons`), and names the protein product's accession (`protein_id`).

#### Usage

Required arguments:

```bash
--accession, -a <string>  Versioned RefSeq transcript accession; e.g., "NM_005228.5"
```

Example:

```bash
python datasources/scripts/download_refseq_transcript_genbank.py --accession NM_005228.5
```

### Protein product ESummary

The document summary for a protein product is downloaded from the [ESummary](https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESummary) endpoint of the protein database and written to datasources/refseq/{accession}.esummary.json.

The file is used to look up the protein product's NCBI GI number (`uid`), which RefSeq flat files no longer report. The GI number forms the protein's NCBI link, `https://www.ncbi.nlm.nih.gov/protein/{gi}`, in the `iris` of its RefSeq coding in referenced/codings.json. The summary also reports the protein's length (`slen`) and title, which are useful for checking that the accession is the expected protein product.

#### Usage

Required arguments:

```bash
--accession, -a <string>  Versioned RefSeq protein accession; e.g., "NP_005219.2"
```

Example:

```bash
python datasources/scripts/download_refseq_protein_esummary.py --accession NP_005219.2
```

### Protein product GenPept flat file

The GenPept flat file for a protein product is downloaded from the [EFetch](https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.EFetch) endpoint of the protein database and written to datasources/refseq/{accession}.gp.

The file is kept as a reference copy of the protein record and is not currently read by any script. It contains the protein's amino acid sequence (`ORIGIN`), which can be used to confirm the reference amino acid at a position when curating a protein change such as p.L858R, annotated `Region` and `Site` features such as domains and binding sites, and the transcript that encodes the protein (`coded_by`).

#### Usage

Required arguments:

```bash
--accession, -a <string>  Versioned RefSeq protein accession; e.g., "NP_005219.2"
```

Example:

```bash
python datasources/scripts/download_refseq_protein_genpept.py --accession NP_005219.2
```
