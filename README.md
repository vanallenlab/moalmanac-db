# Molecular Oncology Almanac - Database
Molecular Oncology Almanac (MOAlmanac) is a clinical interpretation algorithm paired with an underlying knowledge base for precision oncology. The primary objective of MOAlmanac is to identify and associate molecular alterations with therapeutic sensitivity and resistance as well as disease prognosis. This is done for “first-order” genomic alterations -- individual events such as somatic variants, copy number alterations, fusions, and germline -- as well as “second-order” events -- those that are not associated with one single mutation, and may be descriptive of global processes in the tumor such as tumor mutational burden, microsatellite instability, mutational signatures, and whole-genome doubling.

The underlying database of this method is dependent on expert curation of the current body of knowledge on how molecular alterations affect clinical actionability. As the field of precision oncology grows, the quantity of research on how specific alterations affect therapeutic response and patient prognosis expands at an increasing rate. Curating the latest literature and presenting it in an accessible manner increases the abilities of clinicians and researchers alike to rapidly assess the importance of a molecular feature.

## Using this repository
Browse to contents of the Molecular Oncology Almanac through this repository, through our [browser (https://moalmanac.org)](https://moalmanac.org), or through our [API](https://app.swaggerhub.com/apis-docs/vanallenlab/almanac-browser). Previous releases, with release notes, can be found under [releases](https://github.com/vanallenlab/moalmanac-db/releases) and a history of all changes can be read in the [content changelog](/docs/content-changelog.md).

If you wish to suggest an assertion for cataloging in this database, you can do so by
- Following our [standard operating procedure](/docs/sop.md) and opening a [pull request](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/about-pull-requests)
- Suggesting an entry through our [web browser's form](https://moalmanac.org/add)
- Suggesting an entry through our [Google Chrome extension](https://chrome.google.com/webstore/detail/molecular-oncology-almana/jliaipolchffpaccagodphgjpfdpcbcm)

## Citation
If you find this tool or any code herein useful, please cite:  
> [Reardon, B. *et al.* (2020). Clinical interpretation of integrative molecular profiles to guide precision cancer medicine. *bioRxiv* 2020.09.22.308833 doi:10.1101/2020.09.22.308833](https://www.biorxiv.org/content/10.1101/2020.09.22.308833v1)

## Disclaimer - For research use only
DIAGNOSTIC AND CLINICAL USE PROHIBITED. DANA-FARBER CANCER INSTITUTE (DFCI) and THE BROAD INSTITUTE (Broad) MAKE NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING, WITHOUT LIMITATION, WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NONINFRINGEMENT OR VALIDITY OF ANY INTELLECTUAL PROPERTY RIGHTS OR CLAIMS, WHETHER ISSUED OR PENDING, AND THE ABSENCE OF LATENT OR OTHER DEFECTS, WHETHER OR NOT DISCOVERABLE.

In no event shall DFCI or Broad or their Trustees, Directors, Officers, Employees, Students, Affiliates, Core Faculty, Associate Faculty and Contractors, be liable for incidental, punitive, consequential or special damages, including economic damages or injury to persons or property or lost profits, regardless of whether the party was advised, had other reason to know or in fact knew of the possibility of the foregoing, regardless of fault, and regardless of legal theory or basis. You may not download or use any portion of this program for any non-research use not expressly authorized by DFCI or Broad. You further agree that the program shall not be used as the basis of a commercial product and that the program shall not be rewritten or otherwise adapted to circumvent the need for obtaining permission for use of the program other than as specified herein.
