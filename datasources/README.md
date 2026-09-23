Datasources used for codings.

## NCI Thesaurus



## OncoTree

[OncoTree](https://oncotree.mskcc.org) is used for secondary codings of cancer types. We use the [/api/tumorTypes](https://oncotree.mskcc.org/swagger/index.html#/TumorTypes/get_api_tumorTypes) endpoint.

Fetches the JSON tree for the given OncoTree version from the public OncoTree
API and writes it to datasources/{version}_tree.json.

### Usage

Required arguments:

```bash
--mode, -m    <string>  OncoTree endpoint; choices = "flat" or "tree"
--version, -v <string<  OncoTree version to download; e.g., "oncotree_2025_10_03"
```

Example:

```bash
python download_oncotree.py --mode flat --version oncotree_2025_10_03
```
