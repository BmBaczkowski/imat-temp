#!/usr/local/bin/python

import json
import os
import sys
from datetime import date


def show_usage(name):
    print("Usage: ", name, "destdir\n"),
    return sys.exit()


dataset_description = {
    "Name": "n/a",
    "BIDSVersion": "v1.8.0",
    "DatasetType": "raw",
    "License": "n/a",
    "Authors": [
        "Blazej M. Baczkowski",
        "n/a",
    ],
    "Acknowledgments": "n/a",
    "HowToAcknowledge": "Please cite this paper: doi:",
    "Funding": [
        "n/a",
    ],
    "EthicsApprovals": [
        "Local Ethics Committee of Hamburg Universitaet (Votum 2022_17)",
    ],
    "ReferencesAndLinks": [
        "n/a",
    ],
    "DatasetDOI": "n/a",
    "GeneratedBy": [
        {
            "Name": "n/a",
            "Version": "n/a",
            "Description": "n/a",
            "CodeURL": "file:///../code-sourcedata2rawdata",
            "Container": {
                "Type": "docker",
                "Tag": "n/a",
            },
        },
    ],
    "SourceDatasets": [
        {
            "URL": "file:///path/to/code-ptb/ACRONYM-ptb",
            "Version": "3130403c773fd734b909085c90ee8cd",
        },
        {
            "URL": "file:///path/to/source-datasets/ACRONYM-data-biopac",
            "Version": "c1ca3ef0602137a276b5450cb7ed1995",
        },
        {
            "URL": "file:///path/to/source-datasets/ACRONYM-data-limesurvey",
            "Version": "8085ad0ddc18ad198567c0eca3802ec7",
        },
        {
            "URL": "file:///path/to/source-datasets/ACRONYM-data-ptb",
            "Version": "b1785b8f1d1a7236feb63b6020b86904",
        },
        {
            "URL": "file:///path/to/source-datasets/ACRONYM-data-smi-samples",
            "Version": "8b1ecc03509e8adc825a8093351df4e3",
        },
    ],
}

# read in parameters
n = len(sys.argv)
if n < 2:
    name = sys.argv[0]
    show_usage(os.path.basename(name))
else:
    destdir = sys.argv[1]


with open(
    os.path.join(destdir, "dataset_description.json"), "w", encoding="utf-8"
) as f:
    json.dump(dataset_description, f, ensure_ascii=False, indent=4)

with open(
    os.path.join(destdir, "logfiles", "dataset_description.log"), "w", encoding="utf-8"
) as f:
    f.write("Dataset description completed")
