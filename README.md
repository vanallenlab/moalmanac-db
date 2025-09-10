# Molecular Oncology Almanac - Database
[![DOI](https://zenodo.org/badge/318264235.svg)](https://doi.org/10.5281/zenodo.17089309)
[![License](https://img.shields.io/github/license/vanallenlab/moalmanac-db.svg)](./LICENSE)

**We are in the process of updating to a new database schema. Read more [here](/docs/referenced-schema-draft-about.md)**!

Molecular Oncology Almanac (MOAlmanac) is a clinical interpretation algorithm paired with an underlying knowledge base for precision oncology. The primary objective of MOAlmanac is to identify and associate molecular alterations with therapeutic sensitivity and resistance as well as disease prognosis. This is done for “first-order” genomic alterations -- individual events such as somatic variants, copy number alterations, fusions, and germline -- as well as “second-order” events -- those that are not associated with one single mutation, and may be descriptive of global processes in the tumor such as tumor mutational burden, microsatellite instability, mutational signatures, and whole-genome doubling.

The underlying database of this method is dependent on expert curation of the current body of knowledge on how molecular alterations affect clinical actionability. As the field of precision oncology grows, the quantity of research on how specific alterations affect therapeutic response and patient prognosis expands at an increasing rate. Curating the latest literature and presenting it in an accessible manner increases the abilities of clinicians and researchers alike to rapidly assess the importance of a molecular feature.

## Using this repository
Browse the contents of the Molecular Oncology Almanac through this repository, our [browser (https://moalmanac.org)](https://moalmanac.org), or our [API](https://app.swaggerhub.com/apis-docs/vanallenlab/almanac-browser). Previous releases, with release notes, can be found under [releases](https://github.com/vanallenlab/moalmanac-db/releases) and a history of all changes can be read in the [content changelog](https://news.moalmanac.org/category/database).

If you wish to suggest an assertion for cataloging in this database, you can do so by
- Following our [standard operating procedure](/docs/sop.md) and opening a [pull request](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/about-pull-requests)
- Suggesting an entry through our [web browser's form](https://moalmanac.org/add)
- Suggesting an entry through our [Google Chrome extension](https://chrome.google.com/webstore/detail/molecular-oncology-almana/jliaipolchffpaccagodphgjpfdpcbcm)

## Installation
### Download
This repository can be downloaded through GitHub by either using the website or terminal. To download on the website, navigate to the top of this page, click the green `Clone or download` button, and select `Download ZIP` to download this repository in a compressed format. To install using GitHub on terminal, type:

```bash
git clone https://github.com/vanallenlab/moalmanac-db.git
cd moalmanac-db
```

### Python dependencies
This repository uses Python 3.12. We recommend using a [virtual environment](https://docs.python.org/3/tutorial/venv.html) and running Python with either [Anaconda](https://www.anaconda.com/download/) or [Miniconda](https://conda.io/miniconda.html).

Run the following from this repository's directory to create a virtual environment and install dependencies with Anaconda or Miniconda:
```bash
conda create -y -n moalmanac-db python=3.12
conda activate moalmanac-db
pip install -r requirements.txt
```

Or, if using base Python:
```bash
virtualenv venv
source activate venv/bin/activate
pip install -r requirements.txt
```

To make the virtual environment available to jupyter notebooks, execute the following code while the virtual environment is activated:
```bash
pip install jupyter
ipython kernel install --user --name=moalmanac-db
```

## Testing
We are currently using [pytest](https://docs.pytest.org/en/stable/) for testing in this repository. From the root directory, run:
```bash
pytest tests/
```

## Citation
If you find this tool or any code herein useful, please cite:
> [Reardon, B., Moore, N.D., Moore, N.S., *et al*. Integrating molecular profiles into clinical frameworks through the Molecular Oncology Almanac to prospectively guide precision oncology. *Nat Cancer* (2021). https://doi.org/10.1038/s43018-021-00243-3](https://www.nature.com/articles/s43018-021-00243-3)

If you want to cite a specific version of the database, use our Zenodo DOIs.
- The concept DOI always points to the latest version: [https://doi.org/10.5281/zenodo.17089309)](https://doi.org/10.5281/zenodo.17089309).
- Each release also has a version-specific DOI. We began minting Zenodo DOIs with our 2025-09-04 release; if you would like a DOI for a prior version, please [contact us](https://dev.moalmanac.org/about#contact).

## Disclaimer - For research use only
DIAGNOSTIC AND CLINICAL USE PROHIBITED. DANA-FARBER CANCER INSTITUTE (DFCI) and THE BROAD INSTITUTE (Broad) MAKE NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING, WITHOUT LIMITATION, WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NONINFRINGEMENT OR VALIDITY OF ANY INTELLECTUAL PROPERTY RIGHTS OR CLAIMS, WHETHER ISSUED OR PENDING, AND THE ABSENCE OF LATENT OR OTHER DEFECTS, WHETHER OR NOT DISCOVERABLE.

In no event shall DFCI or Broad or their Trustees, Directors, Officers, Employees, Students, Affiliates, Core Faculty, Associate Faculty and Contractors, be liable for incidental, punitive, consequential or special damages, including economic damages or injury to persons or property or lost profits, regardless of whether the party was advised, had other reason to know or in fact knew of the possibility of the foregoing, regardless of fault, and regardless of legal theory or basis. You may not download or use any portion of this program for any non-research use not expressly authorized by DFCI or Broad. You further agree that the program shall not be used as the basis of a commercial product and that the program shall not be rewritten or otherwise adapted to circumvent the need for obtaining permission for use of the program other than as specified herein.
