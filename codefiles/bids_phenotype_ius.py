#!/usr/local/bin/python

from argparse import ArgumentParser
import json
import logging
import numpy as np
import os
import pandas as pd


def main():
    parser = ArgumentParser(prog="bids_phenotype_ius", description="", epilog="")
    parser.add_argument("sourcedir", type=str, help="data source directory")
    parser.add_argument("phenotypedir", type=str, help="data output directory")
    parser.add_argument("logdir", type=str, help="logfile directory")
    args = parser.parse_args()

    FILEOUT = os.path.join(args.phenotypedir, "ius.tsv")

    # store logfile for debugging
    logfile = os.path.join(args.logdir, "ius.log")
    logging.basicConfig(
        filename=logfile, encoding="utf-8", filemode="w", level=logging.DEBUG
    )

    # init log info
    logging.info(
        "Export limesurvey intolerance of uncertainty scale data into tsv file"
    )

    # read in the file
    df = pd.read_csv(os.path.join(args.sourcedir, "results_en.tsv"), sep="\t")

    # subsetting variables
    df = df[
        [
            "ID",
            "UI18[UI1]",
            "UI18[UI2]",
            "UI18[UI3]",
            "UI18[UI4]",
            "UI18[UI5]",
            "UI18[UI6]",
            "UI18[UI7]",
            "UI18[UI8]",
            "UI18[UI9]",
            "UI18[UI10]",
            "UI18[UI11]",
            "UI18[UI12]",
            "UI18[UI13]",
            "UI18[UI14]",
            "UI18[UI15]",
            "UI18[UI16]",
            "UI18[UI17]",
            "UI18[UI18]",
        ]
    ]

    df.rename(
        columns={
            "ID": "participant_id",
            "UI18[UI1]": "item-01",
            "UI18[UI2]": "item-02",
            "UI18[UI3]": "item-03",
            "UI18[UI4]": "item-04",
            "UI18[UI5]": "item-05",
            "UI18[UI6]": "item-06",
            "UI18[UI7]": "item-07",
            "UI18[UI8]": "item-08",
            "UI18[UI9]": "item-09",
            "UI18[UI10]": "item-10",
            "UI18[UI11]": "item-11",
            "UI18[UI12]": "item-12",
            "UI18[UI13]": "item-13",
            "UI18[UI14]": "item-14",
            "UI18[UI15]": "item-15",
            "UI18[UI16]": "item-16",
            "UI18[UI17]": "item-17",
            "UI18[UI18]": "item-18",
        },
        inplace=True,
    )

    # rename subject id
    for i in df["participant_id"]:
        df["participant_id"].replace(i, "sub-%i" % i, inplace=True)

    # replace NaN with "n/a"
    df.fillna("n/a", inplace=True)

    # reshape from wide to long
    df = pd.melt(
        df, id_vars=["participant_id"], var_name="ui_item", value_name="ui_response"
    )

    logging.info("Saving limesurvey data into phenotype/ius.tsv file")
    df.to_csv(FILEOUT, sep="\t", index=False)

    # create a sidecar json file
    description = {
        "MeasurmentToolMetadata": {
            "Description": "Intolerance of Uncertainty Scale. German version.",
            "TermURL": "n/a",
            "DOI": "10.1026/1616-3443.37.3.190",
        },
        "Derivative": "false",
        "ui_item": {
            "Description": "The questionnaire consists of 18 items.",
        },
        "ui_response": {
            "Description": "n/a",
            "Levels": {
                "1": "not at all characteristic of me",
                "2": "n/a",
                "3": "somewhat characteristic of me",
                "4": "n/a",
                "5": "entirely charachteristic of me",
            },
        },
    }

    logging.info("Log a sidecar json file")
    with open(os.path.join(args.phenotypedir, "ius.json"), "w", encoding="utf-8") as f:
        json.dump(description, f, ensure_ascii=False, indent=4)

    logging.info("Finished")


main()
