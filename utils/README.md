# Utility scripts for the Molecular Oncology Almanac database
This directory contains a collection of utility scripts designed to facilitate the management and processing of the Molecular Oncology Almanac (moalmanac) database.

**Note: The default arguments for scripts within this directory assume execution from the root directory of this repository.**

# Table of contents
- [dereference.py](#dereferencepy)
- [populate_statement_description_from_indication.py](#populate_statement_description_from_indicationpy)
- [json_utils.py](#json_utilspy)
- [read.py](#readpy)
- [write.py](#writepy)

# Scripts
## dereference.py
`dereference.py` creates a single JSON file for the moalmanac database by dereferencing referenced JSON files. By default, these are located in the `referenced/` folder of this repository.

### Usage
Optional arguments:
```bash
    --about           <string>    referenced JSON for database metadata. Default: referenced/about.json
    --agents          <string>    referenced JSON for agents that either contribute to the database or publish documents cited within the database. Default: referenced/agents.json
    --biomarkers      <string>    referenced JSON for biomarkers. Default: referenced/biomarkers.json
    --codings         <string>    referenced JSON for codings. Default: referenced/codings.json
    --contributions   <string>    referenced JSON for contributions to database. Default: referenced/contributions.json
    --diseases        <string>    referenced JSON for cancer types. Default: referenced/diseases.json
    --documents       <string>    referenced JSON for documents cited in the database. Default: referenced/documents.json
    --genes           <string>    referenced JSON for genes associated with biomarkers. Default: referenced/genes.json
    --indications     <string>    referenced JSON for regulatory approvals for use or reimbursement. Default: referenced/indications.json
    --mappings        <string>    referenced JSON for mappings. Default: referenced/mappings.json
    --propositions    <string>    referenced JSON for propositions. Default: referenced/propositions.json
    --statements      <string>    referenced JSON for statements. Default: referenced/statements.json
    --strengths       <string>    referenced JSON for strengths. Default: referenced/strengths.json
    --therapies       <string>    referenced JSON for therapies. Default: referenced/therapies.json
    --therapy-groups  <string>    referenced JSON for therapy groups. Default: referenced/therapy_groups.json
    --urls            <string>    referenced JSON for urls. Default: referenced/urls.json
    --output          <string>    file path for dereferenced JSON output by this script. Default: moalmanac-draft.dereferenced.json
    --clear           <boolean>   remove currently dereferenced entity files in dereferenced/ folder. Default: False.
    --quiet           <boolean>   suppress print statements when writing dereferenced entity files to dereferenced/ folder. Default: False.
```

### Example
To run with default parameters:
```bash
python -m utils.dereference
```

Alternatively, all arguments can be specified explicitly:
```bash
python -m utils.dereference \
  --about referenced/about.json \
  --agents referenced/agents.json \
  --biomarkers referenced/biomarkers.json \
  --codings referenced/codings.json \
  --contributions referenced/contributions.json \
  --diseases referenced/diseases.json \
  --documents referenced/documents.json \
  --genes referenced/genes.json \
  --indications referenced/indications.json \
  --mappings referenced/mappings.json \
  --propositions referenced/propositions.json \
  --statements referenced/statements.json \
  --strengths referenced/strengths.json \
  --therapies referenced/therapies.json \
  --therapy-groups referenced/therapy-groups.json \
  --urls referenced/urls.json \
  --output  moalmanac-draft.dereferenced.json \
  --clear
```

[Back to table of contents](#table-of-contents)

## json_utils.py

[Back to table of contents](#table-of-contents)

## read.py

[Back to table of contents](#table-of-contents)

## write.py

[Back to table of contents](#table-of-contents)
