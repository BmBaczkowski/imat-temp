# IMAT Temp – Data Harmonization Pipeline

This repository contains a data pipeline for harmonizing behavioral and psychophysiological data into [BIDS-like](https://bids.neuroimaging.io/) format.


## Purpose

This repository serves as a workspace for developing and testing a data harmonization pipeline.  
The goal is to transform raw source data into a BIDS-like organized dataset.

## Overview of the Pipeline

The pipeline:

- Ingests raw behavioral data and psychophysiological (eye-tracking and skin conductance) data from source directories
- Standardizes file naming and structure
- Maps metadata into BIDS-compatible fields
- Generates BIDS-like directory structure
- Prepares datasets for downstream analysis

## Output

The pipeline produces a BIDS-like dataset:

```shell
data/raw/
├── CHANGES
├── LICENSE
├── README.md
├── assessment
├── code-psychtoolbox
├── code-source2raw
├── dataset_description.json
├── logfiles
├── participants.json
├── participants.tsv
├── phenotype
├── sub-r002
├── task-01_events.json
├── task-01_recording-biopac_physio.json
├── task-01_recording-eyetracking_physio.json
├── task-01_subtask-afc_beh.json
├── task-02_beh.json
├── task-02_events.json
├── task-02_recording-biopac_physio.json
├── task-02_recording-eyetracking_physio.json
├── task-03_beh.json
├── task-03_events.json
├── task-03_recording-biopac_physio.json
├── task-03_recording-eyetracking_physio.json
├── task-04_beh.json
├── task-04_events.json
├── task-04_recording-biopac_physio.json
├── task-04_recording-eyetracking_physio.json
└── task-shockcalibration_recording-biopac_physio.json
```

