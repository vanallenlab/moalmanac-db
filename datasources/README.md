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
