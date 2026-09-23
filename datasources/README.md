Datasources used for codings. Documentation in this README are written as if the scripts are being run from the repository's root directory.

## NCI Thesaurus



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
