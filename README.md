Molecular Oncology Almanac - Database

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17089309.svg)](https://doi.org/10.5281/zenodo.17089309)
[![License: CC BY 4.0](https://img.shields.io/badge/Database-CC%20BY%204.0-informational)](./LICENSE)
[![License: GPL v2](https://img.shields.io/badge/Code-GPL%20v2-informational)](./LICENSE-code.md)

Molecular Oncology Almanac (moalmanac) is a clinical interpretation algorithm paired with an underlying knowledge base for precision oncology. The primary objective of moalmanac is to identify and associate molecular alterations with therapeutic sensitivity and resistance as well as disease prognosis. This is done for “first-order” genomic alterations -- individual events such as somatic variants, copy number alterations, fusions, and germline -- as well as “second-order” events -- those that are not associated with one single mutation, and may be descriptive of global processes in the tumor such as tumor mutational burden, microsatellite instability, mutational signatures, and whole-genome doubling.

The underlying database of this method is dependent on expert curation of the current body of knowledge on how molecular alterations affect clinical actionability. As the field of precision oncology grows, the quantity of research on how specific alterations affect therapeutic response and patient prognosis expands at an increasing rate. Curating the latest literature and presenting it in an accessible manner increases the abilities of clinicians and researchers alike to rapidly assess the importance of a molecular feature.

## Using this repository

Browse the contents of the Molecular Oncology Almanac through this repository, our [browser (https://moalmanac.org)](https://moalmanac.org), or our [API](https://api.moalmanac.org). Previous releases, with release notes, can be found under [releases](https://github.com/vanallenlab/moalmanac-db/releases) and a history of all changes can be read in the [content changelog](https://news.moalmanac.org/category/database).

If you wish to suggest an assertion for cataloging in this database, you can do so by:

- Following our [standard operating procedure](/docs/sop.md) and opening a [pull request](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/about-pull-requests)

## Installation

### Download

This repository can be downloaded through GitHub by either using the website or terminal. To download on the website, navigate to the top of this page, click the green `Clone or download` button, and select `Download ZIP` to download this repository in a compressed format. To install using GitHub on terminal, type:

```bash
git clone https://github.com/vanallenlab/moalmanac-db.git
cd moalmanac-db
```

### Python dependencies

This repository uses Python 3.12. We recommend managing your environment wih [Conda-forge](https://conda-forge.org)'s installer [Miniforge](https://conda-forge.org/download/).

Run the following from this repository's directory to create a virtual environment and install dependencies with Miniforge:

```bash
conda env create -f environment.yaml
conda activate moalmanac-db
```

The [environment.yaml](./environment.yaml) file specifies Python 3.12 and delegates package installation to pip using pyproject.toml. No separate `pip install` step is needed.

Or, if you prefer not to use conda, you can use a standard [virtual environment](https://docs.python.org/3/tutorial/venv.html):

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install .
```

If using VS Code, open the repository folder and select the interpreter via **Command Palette → Python: Select Interpreter**, then choose `moalmanac-db` from the list.

## Testing

We are currently using [pytest](https://docs.pytest.org/en/stable/) for testing in this repository. From the root directory, run:

```bash
pytest tests/
```

## Citation

The Molecular Oncology Almanac database is available under CC BY 4.0, which requires appropriate credit. If you use the database, or find this tool or any code herein useful, please cite:
> [Reardon, B., Moore, N.D., Moore, N.S., *et al*. Integrating molecular profiles into clinical frameworks through the Molecular Oncology Almanac to prospectively guide precision oncology. *Nat Cancer* (2021). https://doi.org/10.1038/s43018-021-00243-3](https://www.nature.com/articles/s43018-021-00243-3)

Where relevant, please also cite the version of the database used with its Zenodo DOI.

- The concept DOI always points to the latest version: [https://doi.org/10.5281/zenodo.17089309](https://doi.org/10.5281/zenodo.17089309).
- Each release also has a version-specific DOI. We began minting Zenodo DOIs with our 2025-09-04 release; if you would like a DOI for a prior version, please [contact us](https://moalmanac.org/about#contact).

## License

- Database content: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/), see [LICENSE](./LICENSE).
- Scripts in `utils/` and `tests/`: [GNU General Public License, Version 2 (GPL v2)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html), see [LICENSE-code.md](./LICENSE-code.md).
- Third-party files in [datasources/](./datasources) are not covered by the CC BY license; see [datasources/README.md](./datasources/README.md#licensing).

## Disclaimer

For purposes of this Disclaimer, the “Service” means the Molecular Oncology Almanac database, software, API, browsers, and related materials.

THIS DATABASE AND SOFTWARE HAVE NOT BEEN VALIDATED FOR DIAGNOSTIC OR CLINICAL USE, AND DANA-FARBER CANCER INSTITUTE (DFCI) MAKES NO WARRANTY OF FITNESS FOR DIAGNOSTIC OR CLINICAL USE. USERS ARE SOLELY RESPONSIBLE FOR ENSURING THAT THEIR ACCESS TO AND USE OF THE DATABASE, SOFTWARE, API, BROWSERS, AND RELATED MATERIALS COMPLIES WITH ALL APPLICABLE LAWS, REGULATIONS, INSTITUTIONAL POLICIES, AND ETHICAL REQUIREMENTS, INCLUDING ANY REQUIREMENTS APPLICABLE TO RESEARCH INVOLVING HUMAN SUBJECTS OR HUMAN-DERIVED DATA. DFCI MAKES NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING, WITHOUT LIMITATION, WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NONINFRINGEMENT OR VALIDITY OF ANY INTELLECTUAL PROPERTY RIGHTS OR CLAIMS, WHETHER ISSUED OR PENDING, AND THE ABSENCE OF LATENT OR OTHER DEFECTS, WHETHER OR NOT DISCOVERABLE.

In no event shall DFCI or its trustees, directors, officers, employees, students, affiliates, core faculty, associate faculty and contractors be liable for incidental, punitive, consequential or special damages, including economic damages or injury to persons or property or lost profits, regardless of whether the party was advised, had other reason to know or in fact knew of the possibility of the foregoing, regardless of fault, and regardless of legal theory or basis. To the extent liability cannot be disclaimed, DFCI’s liability shall be limited to direct, actual damages resulting from DFCI’s failure to perform its obligations under the applicable terms.

The Molecular Oncology Almanac database is made available under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/), which permits use, including commercial use, provided appropriate credit is given. The software is licensed under the [GNU General Public License, Version 2 (GPL v2)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html). Certain third-party code or materials may be subject to separate license terms. For additional terms governing access to and use of the Service, please see the Terms of Use.
