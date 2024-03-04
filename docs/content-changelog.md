# Content Changelog
The following changes have been made to the content catalogued within the Molecular Oncology Almanac knowledge base.

## March 2024 release
Added entries:
- (FDA) _EGFR_ exon 20 insertions and sensitivity to amivantamab-vmjw in combination with carboplatin and pemetrexed for patients with non-small cell lung cancer.
- (FDA) _EGFR_ exon 19 deletions or p.L858R and sensitivity to osimertinib in combination with cisplatin and pemetrexed for patients with locally advanced or metastatic non-small cell lung cancer.
- (FDA) _EGFR_ exon 19 deletions or p.L858R and sensitivity to osimertinib for patients with metastatic non-small cell lung cancer.
- (FDA) _MET_ splice site and deletion variants (exon 14 skipping) and sensitivity to tepotinib for patients with metastatic non-small cell lung cancer. 

Revised entries:
- (FDA) _EGFR_ p.T790M and sensitivity to osimertinib, updated citation and publication date to reflect March 2017 approval (from accelerated approval) date for this indication.
- (FDA) _EGFR_ exon 20 insertions and sensitivity to amivantamab-vmjw, updated publication date from 2021-05-01 to 2021-05-21. 
- (FDA) _EGFR_ exon 19 deletions or p.L858R and sensitivity to osimertinib as an adjuvant therapy for patients with metastatic non-small cell lung cancer, updated publication date from 2020-12-01 to 2020-12-11.

Removed entries:
- (FDA) _MET_ exon 14 nonsense variants and sensitivity to cabmatinib in patients with non-small cell lung cancer.
- (Guideline) _MET_ exon 14 nonsense variants and sensitivity to crizotinib in patients with non-small cell lung cancer.

The U.S. FDA also granted accelerated approval to [lifileucel for patients with unresectable or metastatic melanoma](https://www.fda.gov/drugs/resources-information-approved-drugs/fda-grants-accelerated-approval-lifileucel-unresectable-or-metastatic-melanoma), but a drug label is not yet present for lifileucel.

## February 2024 release
Added entries:
- (FDA) _BRAF_ p.V600E/K and sensitivity to vemurafenib for patients with Erdheim-Chester disease. 

Revised entries:
- (FDA) _BRCA1/2_ somatic variants and sensitivity to rucaparib for patients with fallopean tube cancer had the oncotree term updated to High-Grade Serous Fallopian Tube Cancer.
- (FDA) _FGFR3_ fusions, p.R248C, p.S249C, p.G370C, and p.Y373C and sensitivity to erdafitinib for patients with urothelial carcinoma received an updated approval.
- "Oncogenic Mutations" was removed from the `variant_annotation` field from all 10 records with that value.

Removed entries:
- (FDA) _FGFR2_ fusions and sensitivity to erdafitinib for patients with urothelial carcinoma. The FDA amended their prior accelerated approval for erdafitinib, removing susceptible _FGFR2_ alterations from the indication.

## January 2024 release
Added entries:
- (FDA) _ERBB2_ amplification and sensitivity to neratinib in combination with capecitabine for patients with breast cancer.

Revised entries:
- (FDA) _ERBB2_ amplification and sensitivity to neratinib for patients with breast cancer, received an updated description and citation.

## December 2023 release
Added entries:
- (FDA) _PIK3CA_ and _AKT_ somatic variants and _PTEN_ loss of function variants and sensitivity to capivasertib in combination with fulvestrant for patients with breast cancer.
- (FDA) _ROS1_ rearrangements and sensitivity to repotrectinib in patients with nsclc.

Revised entries:
- (FDA) _ERBB2_ amplification and sensitivity to pembrolizumab in combination with trastuzumab, fluoropyrimidine- and platinum- containing chemotherapy for patients with gastric or gastroesophageal junction (GEJ) adenocarcinoma received an updated indication from the FDA. 
- (FDA) _NTRK1/2/3_ rearrangements and sensitivity to larotrectinib were changed from translocation to fusion rearrangement type.
- _EGFR_ p.L858R entries now all contain information for exon and rsid values
- _ABL1_ p.T315I entries were revised to have consistent exon and rsid values
- _NRAS_ p.G12C entries now include an rsid
- The OncoTree terms and codes were swapped for _ATK1_ missense variants and p.E17K and sensitivity to MK-2206 in breast cancer and _ATM_ knockdowns in colorectal cancer

Removed entries:
- (Clinical evidence) _PTEN_ deletions and resistance to pembrolizumab in uterine leimyoma (Peng et al. 2016) had a duplicate entry in the knowledge base, which has been removed.

## November 2023 release
This month's data release features recent FDA approvals, updates of mutational signatures from version 2 to 3.4, updates to the source fields for several citations, removal of several entries, revising format of all clinical guideline citations, and the `publication_date` field has been populated for all current database records. 

Added entries:
- (FDA) _BCR_::_ABL1_ and sensitivity to bosutinib for pediatric patients with CML.
- (FDA) _BRAF_ p.V600E and sensitivity to encorafenib in combination with binimetinib for adult patients with NSCLC.
- (FDA) _IDH1_ p.R132C, p.R132H, and somatic variants and sensitivity to ivosidenib for patients with myelodysplastic syndromes (MDS). 
- (Guideline) _FLT3_ p.D835A, p.D835E, p.D835H, p.D835Y and poor prognosis in patients with MDS.
- (Guideline) _GATA2_ missense, nonsense, frameshift, and splice site variants and poor prognosis in patients with MDS.
- (Guideline) _NPM1_ p.W288Cfs*12 and poor prognosis in patients with MDS.
- (Guideline) _NRAS_ p.G12A, p.G12C, p.G12D, p.G12R, p.G12S, p.G12V, p.G13A, p.G13D, p.G13R, p.G13V, p.Q61E, p.Q61H, p.Q61L, p.Q61P, and p.Q61R and poor prognosis for patients with MDS. 
- (Guideline) _SETBP1_ p.I865N and poor prognosis for patients with MDS.
- (Guideline) _SF3B1_ p.I704S and poor prognosis for patients with MDS. 
- (Guideline) _SRSF2_ p.P95A, p.P95H, p.P95L, p.P95R, and p.P95_R102del and poor prognosis for patients with MDS. 
- (Guideline) _TP53_ missense, nonsense, splice site, and frameshift variants and poor prognosis for patients with MDS. 
- (Guideline) _U2AF1_ p.S34A, p.S34F, p.S34Y, p.Q157P, p.Q157R and poor prognosis for patients with MDS.

Revised entries:
- (FDA) _NTRK1/2/3_ fusions and sensitivity to entrectinib were revised due to the FDA's approval for adult or pediatric patients older than 1 month with any solid tumor.
- (Guideline) _PDGFRB_ translocations and sensitivity to imatinib in mds was revised to match updated guidelines that specify ETV6 as a fusion partner and CMML as a more specific tumor type.
- (Guideline) _TET2_ variants and sensitivity to Azacitidine was downgraded from Guideline to Clinical evidence.
- (Preclinical) _BRAF_ p.V600E and sensitivity to dabrafenib in combination with either omipalisib (PI3K/Akt/mTOR) or bevacizumab (VEGF/VEGFR) was revised to add clinical context and expand upon the relationship description.  
- All Mutational Signature relationships (17) have been updated from version 2 to version 3.4. 
- The citation text was updated for Bostner et al. 2007 (PMID: 7486065), Leone et al. 2008 (PMID: 18829482), Corcoran et al. 2010 (PMID: 21098728), Sillars-Hardebol et al. 2012 (PMID: 22207630), Dickson et al. 2013 (PMID: 23569312), Etemadmoghadam et al. 2013 (PMID: 24218601), Johung et al. 2013 (PMID: 23897899), Van Allen et al. 2014 (PMID: 25096233), Wagle et al. 2014 (PMID: 24265154), Gorre et al. 2016 (PMID: 11423618), Luo et al. 2016 (PMID: 27580028), Cuppens et al. 2017 (PMID: 28232476), and Willliams et al. 2020 (PMID: 28283584).
- The DOI and/or URL were updated for Takano et al. 2005 (PMID: 15998907), Fong et al. 2009 (PMID: 19553641), Tesser-Gamba et al. 2012 (PMID: 22154052), Chatterjee et al. 2013 (PMID: 23565244), Hunter et al. 2014 (PMID: 24937673), Mak et al. 2015 (PMID: 25450872), Fondello et al. 2016 (PMID: 27399807), Hugo et al. 2016 (PMID: 26997480), Ke et al. 2016 (PMID: 27717507), Sung et al. 2016 (PMID: 27793752), George et al. 2017 (PMID: 28228279), Mouw et al. 2017 (PMID: 28630051), Aldubayan et al. 2018 (PMID: 29478780), Seligson et al. 2018 (PMID: 30541756), De Bono et al. 2019, and Tewari et al. 2021 (PMID: 34496240). Many of these changes are due to a recently discovered issue with DOIs pointing to journals published through Elsevier. 
- The NCT code was updated for Le et al. 2015 (PMID: 26028255)

Removed entries,
- (Guideline) _BCR::ABL1_ and sensitivity to dasatinib, imatinib, and nilotinib in CML to reduce redundency from other CML guideline entries. 
- (Guideline) _BRAF_ p.V600E and sensitivity to dabrafenib in combination with trametinib in patients with NSCLC. This citation was incorrectly categorized as a Guideline as it references an FDA approval, which has since been added to the knowledge base.  
- (Guideline) _BRCA1/2_ germline variants and sensitivity to pazopanib in ovarian cancer because the underlying source does not mention this relationship in the context of BRCA1/2. 
- (Guideline) _BRCA2_ germline variants and sensitivity to olaparib in ovarian cancer, as there was a duplicate record.
- (Guideline) _KIT_ variants and poor prognosis in head and neck mucosal melanoma, as the citation suggests that head and neck mucosal melanoma has a poor prognosis independent of _KIT_ status.
- (Guideline) _KRAS_, _PRFPF8_variants and poor prognosis in MDS. While KRAS is included in the IPSS-M Prognostic Risk Schema, KRAS being highlight as associated with poor prognosis is not explicitly stated in current guidelines. 
- (Guideline) _NRAS_, _SETBP1_, _TP53_ variants and poor prognosis in MDS has been removed as the current guidelines cite specific amino acid changes, which have been added.
- (Clinical trial) _EGFR_ variants and sensitivity to Durvalumab + Gefitinib in NSCLC was removed [per further studies](https://pubmed.ncbi.nlm.nih.gov/33012782/) observing a negative finding.
- (Clinical trial) _KRAS_ p.G12C and sensitivity to AMG 510 was removed because there are now associated FDA approvals, and we will be phasing out abstracts from the knowledge base.
- (Clinical evidence) _NRAS_ p.Q61L and sensitivity to Selumetinib in MDS was removed as it contained a duplicate record. 
- (Preclinical) _BRAF_ p.V600E and sensitivity to GANT61 was removed because the study findings were independent of melanoma cell line BRAF or NRAS status.

## October 2023 release
Added entries:
- (Preclinical) _ATM_ copy number deletions and sensitivity to talazoparib in osteosarcoma.
- (Preclinical) _BAP1_ copy number deletions and sensitivity to talazoparib in osteosarcoma.
- (Preclinical) _BARD1_ copy number deletions and sensitivity to talazoparib in osteosarcoma.
- (Preclinical) _CCNE1_ copy number amplifications and sensitivity to dinaciclib in osteosarcoma.
- (Preclinical) _CDK4_ copy number amplifications and sensitivity to palbociclib in osteosarcoma.
- (Preclinical) _CHEK2_ copy number deletions and sensitivity to talazoparib in osteosarcoma.
- (Preclinical) _FANCA_ copy number deletions and sensitivity to talazoparib in osteosarcoma.
- (Preclinical) _FGFR1_ copy number amplifications and sensitivity to AZ4547 and PD173074 in osteosarcoma.
- (Preclinical) _MYC_ copy number amplifications and sensitivity to AT7519 in osteosarcoma.
- (Preclinical) _PTEN_ copy number deletions and sensitivity to MK-2206 and rapamycin in osteosarcoma.
- (Preclinical) _RB1_ somatic variants and sensitivity to olaparib and palbociclib in osteosarcoma.
- (Preclinical) _TP53_ copy number deletions and sensitivity to talazoparib in osteosarcoma.
- (Preclinical) _TP53_ somatic variants and sensitivity to NSC59984 in osteosarcoma.

Revised entries:
- (FDA) _ERBB2_ amplifications in metastatic breast cancer were revised to list invasive breast carcinoma as the cancer type.
- (FDA) _TSC1_ and _TSC2_ somatic variants and sensitivity to everolimus in subependymal giant cell astrocytoma were revised to include Oncotree terms and codes. 
- (Preclinical) _AKT1_ somatic variants and p.E17K and sensitivity to MK-2206 were revised to include breast cancer as the Oncotree terms and code. The description was also updated for both cataloged relationships.
- (Preclinical) _ATM_ p.A1127D, c.2251-10T>G, and shRNA knockdown and sensitivity to olaparib was revised to update the doi of the underlying journal article and properly list the Oncotree code.
- (Preclinical) _CDKN2A_ copy number deletions and sensitivity to EPZ015666 was adjusted to inferential evidence because the underlying relationship is for MTAP deletions, which are commonly co-deleted with CDKN2A. 
- (Preclinical) _PTEN_ copy number deletions and somatic frameshift, nonsense, and splice site variants and sensitivity to AZD8186 were edited to add prostate cancer as the tumor type and the description was revised.
- (Preclinical) _RB1_ shRNA knockdowns and resistance to palbociclib in prostate cancer was revised to properly list the Oncotree code and term. 
- (Inferential) COSMIC mutational signature 10 and sensitivity to pembrolizumab and durvalumab was revised to list any solid tumor as the cancer type.

`publication_date` was also added for all revised entries.

Removed entries:
- (Preclinical) _PIK3CB_ and sensitivity to AZD8186. 

## September 2023 release
Added entries:
- (FDA) _BRCA1_ somatic and germline variants and sensitivity to abiraterone acetate in combination with niraparib for patients with metastatic castration-resistant prostate cancer.
- (FDA) _BRCA2_ somatic and germline variants and sensitivity to abiraterone acetate in combination with niraparib for patients with metastatic castration-resistant prostate cancer.
- (FDA) MSI-H and sensitivity to dostarlimab-gxly in combination with carboplatin and paclitaxel, followed by single agent dostarlimab-gxly, in endometrial cancer. 

Revised entries:
- (FDA) _EGFR_ p.T790M and sensitivity to osimertinib, resolved typo in description.
- (FDA) _RET_ fusions and sensitivity to pralsetinib, received regular approval from FDA after being previously granted accelerated approval. 
- All prior entries have been revised to have `last_updated` date be in ISO 8601 date standard of `YYYY-MM-DD`

Removed entries:
- (FDA) _RET_ somatic variants and sensitivity to pralsetinib in medullary thyroid cancer was [withdrawn voluntary by Genentech](https://www.gene.com/media/statements/ps_062923). 

The field `publication_date` has been added to entries added or modified in this release. Our team will populate this field for prior records over future releases.

## July 2023 release
Added entries:
- (FDA) _BRCA1_ and _BRCA2_ somatic and germline variants and sensitivity to olaparib in combination with abiraterone and prednisone or prednisolone for patients with metastatic castration-resistant prostate cancer. 
- (FDA) _BRCA1_ and _BRCA2_  germline variants and sensitivity to olaparib for patients with metastatic pancreatic adenocarcinoma. 
- (FDA) _BRCA1_ and _BRCA2_ germline variants and sensitivity to olaparib for the treatment of adult patients with HER2-negative high risk early breast cancer. 
- (FDA) _ATM_, _ATR_, _BRCA1_, _BRCA2_, _CDK12_, _CHEK2_, _FANCA_, _MLH1_, _MRE11A_, _NBN_, _PALB2_, and _RAD51C_ somatic variants and sensitivity to talazoparib in combination with enzalutamide for patients with metastatic castration-resistant prostate cancer.

Revised entries:
- (FDA) _BRCA1_ and _BRCA2_ germline variants and sensitivity to olaparib in breast cancer. Revised description to add additional approval details from FDA drug label.

## April 2023 release
Added entries:
- (FDA) _BRAF_ p.V600E and sensitivity to dabrafenib in combination with trametinib for pediatric patients with low-grade glioma.

## February 2023 release
In this release, we add two recent precision oncology approvals from the FDA regarding ER signaling inhibition in two cancer types.

Added entries:
- (FDA) _ERBB2_ copy number amplifications and sensitivity to trastuzumab in combination with tucatinib in colorectal cancer.
- (FDA) _ESR1_ somatic variants and sensitivity to elacestrant in breast cancer.

## January 2023 release
In this release, we add two recent precision oncology approvals from the FDA.

Added entries:
- (FDA) _IDH1_ p.R132C, p.R132G, p.R132H, p.R132L, and p.R132S and sensitivity to olutasidenib in acute myeloid leukemia.
- (FDA) _KRAS_ p.G12C and sensitivity to adagrasib in non-small cell lung cancer.

## December 2022 release
In this release, we have removed neoantigen burden as a cataloged feature type and combined Silencing with Knockdown feature types. 

Added entries:
- (FDA) _RET_ fusions and sensitivity to selpercatinib in any solid tumor.

Revised entries:
- (Preclinical) _PPARGC1A_ knockdown with CRSPR-Cas9 and not favorable prognosis in melanoma was changed from the feature type Silencing to Knockdown.
- (Preclinical) _USP11_ knockdown with siRNA and sensitivity to olaparib in osteosarcoma was changed from the feature type Silencing to Knockdown.

Removed entries:
- (Clinical evidence) High Neoantigen Burden and sensitivity to pembrolizumab in non-small cell lung cancer.

## October 2022 release
Added entries:
- (FDA) _FGFR2_ rearrangements and sensitivity to futibatinib in intrahepatic cholangiocarcinoma.

Revised entries:
- (Clinical evidence) _SPOP_ variants and favorable prognosis in prostate adenocarcinoma was changed to sensitivity to abiraterone. Additionally, the doi url was revised to correctly point to the citation.

## September 2022 release
Added entries:
- (FDA) _FGFR1_ rearrangements and sensitivity to pemigatinib in myeloid/lymphoid neoplasms.

## August 2022 release
Added entries:
- (FDA) _ALK-EML4_ and sensitivity to crizotinib in inflammatory myofibroblastic tumors.
- (Clinical trial) _BRCA1_ and _BRCA2_ germline variants and sensitivity to olaparib.  
- (Clinical evidence) _BRCA2_ copy number deletion and loss-of-function somatic variants and sensitivity to olaparib in uterine leiomyosarcoma.
- (Clinical evidence) _CDKN2A_ deletion and sensitivity to palbociclib in uterine leiomyosarcoma.
- (Clinical evidence) _MYOCD_ amplification as a diagnostic for strong smooth muscle differentiation in leiomyosarcoma.
- (Preclinical) _RB1_ copy number deletion and somatic variants and sensitivity to olaparib and talazoparib in prostate cancer.
- (Preclinical) _RB1_ knockout and resistance to palbociclib in prostate cancer.
- (Preclinical) _USP11_ silencing and sensitivity to olaparib in osteosarcoma.
- (Inferential) _ATRX_ copy number deletions and poor prognosis in leiomyosarcoma. 
- (Inferential) _BRCA1_ and _BRCA2_ copy number deletion and loss-of-function somatic variants and sensitivity to PARP inhibition (KU0058684, KU0058948).
- (Inferential) _CDKN2C_ deletion may confer sensitivity to CDK4/6 inhibitors. 
- (Inferential) _MAP2K4_ and _MAPK7_ copy number amplification and not sensitive to chemotherapy as well as poor prognosis in osteosarcoma.  
- (Inferential) _PDGFRA_ copy number amplification and poor prognosis in breast cancer.
- (Inferential) _PTEN_ copy number deletion and poor prognosis in uterine leiomyosarcoma. 
- (Inferential) _PTEN_ copy number deletion and sensitivity to sapanisertib in combination with alpelisib in uterine leiomyosarcoma. 

## July 2022 release
Added entries:
- (FDA) _BRAF_ p.V600E and sensitivity to dabrafenib in combination with trametinib in any solid tumor.
- (FDA) _IDH1_ p.R132C, p.R132H and sensitivity to ivosidenib either in combination with azacitidine or as a monotherapy in acute myeloid leukemia.
- (FDA) MSI-H and sensitivity to pembrolizumab in endometrial carcinoma.

## March 2022 release
Revised entries:
- (FDA) _KRAS_ p.G12C and sensitivity to sotorasib's description was revised to remove underscores.
- (Preclinical) _KRAS_ somatic variants and sensitivity to FGFR1 inhibitor + trametinib was revised to remove a trailing space from the therapy name.

## November 2021 release
Added entries:
- (FDA) _BCR-ABL1_ and sensitivity to asciminib in chronic phase chronic myeloid leukemia. 
- (Clinical evidence) _SPOP_ missense somatic variants and favorable prognosis in de-novo metastatic castration-sensitive prostate cancer. 
- (Clinical evidence) _SPOP_ missense somatic variants and sensitivity to abiraterone in metastatic castration-resistant prostate cancer
- (Clinical evidence) _SPOP_ missense somatic variants and sensitivity to anti-androgen therapy.
- (Inferential) _CD274_ amplification and sensitivity to atezolizumab in non-small cell lung cancer. 

Revised entries:
- (FDA) _FGFR2_ fusions and sensitivity to erdafitnib's description was revised to match the standard's described in our [S.O.P.](https://github.com/vanallenlab/moalmanac-db/blob/main/docs/sop.md).

## October 2021 release
Added entries:
- (FDA) _EGFR_ exon 20 insertion variants and sensitivity to mobocertinib in non-small cell lung cancer.

Revised entries:
- (FDA) _BRCA1/2_ pathogenic germline variants and sensitivity to talazoparib was revised to properly cite the package insert and correct a spelling error in the description.
- (FDA) _BCR_-_ABL1_ and sensitivity to bosutinib in chronic myelogenous leukemia was revised to update the hyperlink for the package insert.
- (FDA) _BRAF_ p.V600E and sensitivity to encorafenib in melanoma was revised to update the hyperlink for the package insert. 
- (FDA) TMB-High and sensitivity to pembrolizumab in any solid tumor was revised to correct a spelling error in the description.

## September 2021 release
Added entries:
- (FDA) _IDH1_ p.R132C, p.R132H and sensitivity to ivosidenib in acute myeloid leukemia and cholangiocarcinoma.
- (FDA) _IDH1_ somatic variants and sensitivity to ivosidenib in acute myeloid leukemia and cholangiocarcinoma.
- (FDA) _PDGFRA_ p.D842V and sensitivity to avapritinib in gastrointestinal stromal tumors. 
- (Preclinical) _KIT_ p.D816V and sensitivity to avapritinib in gastrointestinal stromal tumors.
- (Preclinical) _KIT_ exon 11 and 17 somatic variants and sensitivity to avapritinib in gastrointestinal stromal tumors.
- (Preclinical) _KIT_ somatic variants and sensitivity to avapritinib in mast cell leukemia.   
- (Preclinical) _PDGFRA_ p.D842V and sensitivity to avapritinib in gastrointestinal stromal tumors.
- (Preclinical) _PDGFRA_ exon 18 somatic variants and sensitivity to avapritinib in gastrointestinal stromal tumors

Revised entries:
- (Guideline) _PDGFRA_ p.842V and sensitivity to imatinib was revised to not sensitive.  

## June 2021 release
Added entries:
- (FDA) _EGFR_ exon 20 insertion somatic variants and sensitivity to amivantamab-vmjw in metastatic non-small cell lung cancer.
- (FDA) _FGFR2_ fusions and sensitivity to infigratinib in cholangiocarcinoma.
- (FDA) _KRAS_ p.G12C and sensitivity to sotorasib in non-small cell lung cancer.

## May 2021 release
Added entries:
- (FDA) _ERBB2_ amplifications and sensitivity to pembrolizumab in combination with fluoropyrimidine, trastuzumab, and platinum-based chemotherapy in gastric or gastroesophageal junction adenocarcinoma.
- (Inferential) _CD274_ amplifications and sensitivity to pembrolizumab in gastric or gastroesophageal junction adenocarcinoma.

Revised entries:
- (Clinical evidence) _NF1_ germline variants associated with radiation therapy was not labeled with a clinical assertion. "1" has been set for adverse_event_risk.
- (Inferential) _ERBB2_ amplification and sensitivity to trastuzumab was changed to an inferential assertion from FDA. The description was also updated for these entries.

## February 2021 release
In addition to the content changes listed below, this release added a therapeutic strategy (`therapy_strategy`) for all sensitive and resistance relationships. 

Added entries:
- (FDA) _EGFR_ p.L858R and sensitivity to osimertinib in non-small cell lung cancer.
- (FDA) _EGFR_ exon 19 deletions and sensitivity to osimertinib in non-small cell lung cancer.
- (FDA) HER2-positive breast cancer and sensitivity to margetuximab-cmkb + chemotherapy. 

Revised entries:
- (Guideline) _ABL1_ p.T315I suggesting sensitivity to Omacetaxine in CML has been recategorized from a targeted therapy to chemotherapy.
- (Guideline) MSI-High associated with resistance to 5-Fluorouracil in colorectal adenocarcinoma. 5-Fluorouracil was reclassified as a chemotherapy therapy type instead of targeted therapy.
- (Guideline) _TET2_ somatic variants suggesting sensitivity to azacitidine was changed from a targeted therapy to chemotherapy.
- (Clinical evidence) _PAK1_ amplifications associated with poor prognosis in breast cancer. Removed Tamoxifen from this association as it is not asserting therapeutic sensitivity or resistance.
- (Preclinical) _KRAS_ somatic variants associated with sensitivity to trametinib + fgfr1 inhibition. Recorded therapy name to be alphabetical and changed inhibitor to be lowercase.
- (Preclinical) _RUNX1_--_RUNX1T1_ fusions and sensitivity to azacitidine + panobinostat has been reclassified as a combination therapy from targeted therapy. 

Mutational signature version has been added as a feature definition for mutational signatures. All catalogued assertions of this feature type are currently using Mutational Signatures (v2).

Several assertions from clinical guideline sources for multiple myeloma and myelodysplasia were incorrectly reported as clinical evidence. These have been updated to be guidelines.

Removed entries:

## December 2020 release
Added entries:
- (FDA) _RET_ somatic variants associated with sensitivity to pralsetinib in advanced or metastatic medullary thyroid cancer. 
- (FDA) _RET_ fusions associated with sensitivity to pralsetinib in advanced or metastatic thyroid cancer.
- (Inferential) _CDK274_ amplifications associated with sensitivity to chemotherapy in combination with pembrolizumab in locally recurrent or metastatic triple-negative breast cancer.

Revised entries:
- (Guideline) _CDK4_ amplifications associated with sensitivity to palbociclib in well-differentiated and dedifferentiated liposarcoma, updated source. 
- (Guideline) _KIT_ somatic variants associated with sensitivity to sunitinib in thymic carcinomas, updated source. 

Removed entries:
- (Preclinical) _CDKN2B_ deletions associated with sensitivity to EPZ015666.

## November 2020 release
This release focuses on FDA approvals since March 2020. In addition to the following changes, the citation style for all FDA approved associated have been updated to match [American Medical Association (AMA) style formatting](https://mdanderson.libanswers.com/faq/26246).

Added entries:
- (FDA) _ATM_ somatic variants associated with sensitivity to olaparib in metastatic castration-resistant prostate cancer.
- (FDA) _BARD1_ somatic variants associated with sensitivity to olaparib in metastatic castration-resistant prostate cancer.
- (FDA) _BRAF_ p.V600K, p.V600E associated with sensitivity to encorafenib in melanoma.
- (FDA) _BRAF_ p.V600E associated with sensitivity to cetuximab + encorafenib in colorectal cancer. 
- (FDA) _BRCA1_ and _BRCA2_ somatic and germline variants associated with sensitivity to olaparib in metastatic castration-resistant prostate cancer.
- (FDA) _BRCA1_ and _BRCA2_ somatic and germline variants associated with sensitivity to niraparib in ovarian, fallopian tube, and peritoneal cancer.
- (FDA) _BRCA1_ and _BRCA2_ somatic variants associated with sensitivity to bevacizumab and olaparib in advanced ovarian, fallopian tube, and peritoneal cancer. 
- (FDA) _BRIP1_ somatic variants associated with sensitivity to olaparib in metastatic castration-resistant prostate cancer.
- (FDA) _CD274_ copy number amplifications associated with sensitivity to atezolizumab in non-small cell lung cancer. 
- (FDA) _CDK12_ somatic variants associated with sensitivity to olaparib in metastatic castration-resistant prostate cancer.
- (FDA) _CHEK1_ and _CHEK2_ somatic variants associated with sensitivity to olaparib in metastatic castration-resistant prostate cancer.
- (FDA) _ERBB2_ copy number amplifications associated with sensitivity to capecitabine + trastuzumab + tucatinib in breast cancer. 
- (FDA) _ERBB2_ copy number amplifications associated with sensitivity to chemotherapy + hyaluronidase-zzxf + pertuzumab + trastuzumab in breast cancer.
- (FDA) _ERBB2_ copy number amplifications associated with sensitivity to docetaxel + hyaluronidase-zzxf + pertuzumab + trastuzumab in metastatic breast cancer.
- (FDA) _EZH2_ p.Y646*, p.Y646F, p.Y646N, p.A682G, and p.A692V associated with sensitivity to tazemetostat in relapsed or refractory follicular lymphoma. 
- (FDA) _FANCL_ somatic variants associated with sensitivity to olaparib in metastatic castration-resistant prostate cancer.
- (FDA) _FGFR2_ fusions associated with sensitivity to pemigatinib in cholangiocarcinoma. 
- (FDA) High-TMB (> 10 coding mutations per Mb) associated with sensitivity to pembrolizumab in any unresectable or metastatic solid tumor.
- (FDA) _MET_ somatic splice site, deletion, and nonsense variants associated with sensitivity to capmatinib and crizotinib in non-small cell lung cancer.
- (FDA) _PALB2_ somatic variants associated with sensitivity to olaparib in metastatic castration-resistant prostate cancer.
- (FDA) _RAD51B_, _RAD51C_, _RAD51D_, and _RAD51L_ somatic variants associated with sensitivity to olaparib in metastatic castration-resistant prostate cancer.
- (FDA) _RET_ fusions associated with sensitivity to pralsetinib in non-small cell lung cancer.
- (FDA) _RET_ somatic variants associated with sensitivity to selpercatinib in medullarly thyroid cancer.
- (FDA) _RET_ fusions associated with sensitivity to selpercatinib in non-small cell lung cancer and thyroid cancer.
- (Inferential) COSMIC Signature 3, associated with Homologous Recombination Deficiency (HRD), associated with sensitivity to bevacizumab and olaparib in advanced ovarian, fallopian tube, and peritoneal cancer. 

Revised entries:
- (Clinical trial) _ATM_ frameshift, nonsense, and splice site somatic variants associated with sensitivity to BAY1895344 in any solid tumor. Updated disease context from "Advanced metastatic" to "Advanced or metastatic".
