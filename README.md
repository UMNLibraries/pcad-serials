# pcad
Scripts and notebooks to determine where print serials overlap with electronic serials having post-cancellation access and holdings in trusted repositories.

## Post Cancellation Access Determination

Post Cancellation Access Determination (PCAD) is a process that analyzes and combines data from several sources, including Alma, BTAA Shared Print Repository, and Portico,
to determine print serial volumes that are candidates for withdrawal. In order to be identified by this process as candidates for withdrawal, serial volumes must meet two criteria:
they must have equivalent licensed electronic coverage with a post-cancellation access agreement, and they must be represented in one of two trusted preservation repositories,
BTAA Shared Print Repository or Portico.

This is a very complex analysis, requiring a number of dependent steps and inputs. It has been broken up into several scripts and notebooks to clarify the flow of the analysis.
Each notebook includes a description of what it does, along with its required inputs and outputs.

## Process overview:

1. Gather the required files: Alma libraries and locations for PCAD consideration, Portico holdings report, BTAA SPR holdings report, list of Alma electronic collections with PCA.
2. Query Alma for all serial records in the libraries and locations specified. 
3. Save the query as a set and export MARC records.
3. Run `extract_pcad_from_marc.py` on the exported MARC file of print records.
4. Process the output of `extract_pcad_from_marc.py` with PCAD notebook 1: `pcad_1_cluster_clean_ids.ipynb`
5. Create two Alma sets of electronic serial records based on identifiers extracted from print serial records (OCLC numbers and ISSNs).
6. Combine the Alma sets and export MARC records.
7. Run `extract_pcad_from_marc.py` on the exported MARC file of electronic records.
8. Process the output of `extract_pcad_from_marc.py` with PCAD notebook 1: `pcad_1_cluster_clean_ids.ipynb`.
9. Process the outputs of both runs of PCAD notebook 1 with PCAD notebook 2: `pcad_2_ep_track_and_melt.ipynb`.
10. Run `get_ecoll_ids.py` on the `.pkl` output of PCAD notebook 2 (`p_and_e_{date}.pkl`). This script retrieves electronic collection IDs for all MMS IDs in the dataframe via API. This will likely take several hours to run, depending on the number of MMS IDs.
11. Create Alma Analytics report of portfolios with PCA on the basis of the list of e-collections with PCA. The report path is `/shared/University of Minnesota/Twin Cities/PCAD/PCAD-collection-IDs-to-title-info`.
12. Process the `.pkl` output of `get_ecoll_ids.py`, the Analytics report `.csv`, the `.pkl` file output of PCAD notebook 2, and the trusted repository spreadsheets with PCAD notebook 3: `pcad_3_process_e_and_repo_coverage`.
13. Create an All Titles set in Alma by uploading the tab-delimited file of MMS IDs output by PCAD Notebook 3.
14. Use the Alma publishing profile `pcad p2e physical serials with items loc data` to publish the set. The profile publishes item-level enumeration and chronology data for all items belonging to the bibliographic records in the set.
15. Process the published MARC file of item enum/chron data with PCAD notebook 4: `pcad_4_enum_chron_item_filtering`. You will also need a spreadsheet of included libraries/locations in order to filter the item data.
17. Process the output of PCAD notebook 4 and the `.pkl` file output of PCAD notebook 3 (`all_groups_*.pkl`) with PCAD notebook 5: `pcad_5_combine_coverage_calculate_vols`.
18. Process the outputs of PCAD notebook 5 (16 `.pkl` files) with PCAD notebook 6: `pcad_6_make_final_spreadsheet`.
19. Manually rename the tabs in the `.xlsx` file produced by PCAD notebook 6 to describe the contents of each tab.
20. Relax and take a deep breath, because this monster is finished.

## Requirements

Anaconda/conda is recommended, but two requirements files are included:
- `conda_requirements.txt` to create a conda environment (`conda create --name <env> --file conda_requirements.txt`)
- `requirements.txt` to create a pip virtual environment without Anaconda or conda.

## Credits
This analysis was originated by Kelly Thompson in 2018, and much of the process and code is still as Kelly originally wrote it. Extensively revised by Stacie Traill in 2019 and 2020.
