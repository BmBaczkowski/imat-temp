#!/usr/local/bin/python

from argparse import ArgumentParser
import json
import logging
import numpy as np
import os
import pandas as pd


def main():
    parser = ArgumentParser(prog="bids_phenotype_stai", description="", epilog="")
    parser.add_argument("sourcedir", type=str, help="data source directory")
    parser.add_argument("phenotypedir", type=str, help="data output directory")
    parser.add_argument("logdir", type=str, help="logfile directory")
    args = parser.parse_args()

    FILEOUT = os.path.join(args.phenotypedir, "stai_trait.tsv")

    # store logfile for debugging
    logfile = os.path.join(args.logdir, "stai_trait.log")
    logging.basicConfig(
        filename=logfile, encoding="utf-8", filemode="w", level=logging.DEBUG
    )

    # init log info
    logging.info("Export limesurvey stai trait data into tsv file")

    # read in the file
    df = pd.read_csv(os.path.join(args.sourcedir, "results_en.tsv"), sep="\t")

    # subsetting variables
    df = df[
        [
            "ID",
            "STAI[ST1]",
            "STAI[ST2]",
            "STAI[ST3]",
            "STAI[ST4]",
            "STAI[ST5]",
            "STAI[ST6]",
            "STAI[ST7]",
            "STAI[ST8]",
            "STAI[ST9]",
            "STAI[ST10]",
            "STAI[ST11]",
            "STAI[ST12]",
            "STAI[ST13]",
            "STAI[ST14]",
            "STAI[ST15]",
            "STAI[ST16]",
            "STAI[ST17]",
            "STAI[ST18]",
            "STAI[ST19]",
            "STAI[ST20]",
        ]
    ]

    df.rename(
        columns={
            "ID": "participant_id",
            "STAI[ST1]": "item-01",
            "STAI[ST2]": "item-02",
            "STAI[ST3]": "item-03",
            "STAI[ST4]": "item-04",
            "STAI[ST5]": "item-05",
            "STAI[ST6]": "item-06",
            "STAI[ST7]": "item-07",
            "STAI[ST8]": "item-08",
            "STAI[ST9]": "item-09",
            "STAI[ST10]": "item-10",
            "STAI[ST11]": "item-11",
            "STAI[ST12]": "item-12",
            "STAI[ST13]": "item-13",
            "STAI[ST14]": "item-14",
            "STAI[ST15]": "item-15",
            "STAI[ST16]": "item-16",
            "STAI[ST17]": "item-17",
            "STAI[ST18]": "item-18",
            "STAI[ST19]": "item-19",
            "STAI[ST20]": "item-20",
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
        df,
        id_vars=["participant_id"],
        var_name="stai_trait_item",
        value_name="stai_trait_response",
    )

    logging.info("Saving limesurvey data into phenotype/stai_trait.tsv file")
    df.to_csv(FILEOUT, sep="\t", index=False)

    # create a sidecar json file
    description = {
        "MeasurmentToolMetadata": {
            "Description": "The State-Trait Anxiety Inventory",
            "TermURL": "n/a",
        },
        "Derivative": "false",
        "stai_trait_item": {
            "Description": (
                "The questionnaire consists of 20 items. "
                "Reversed items 1, 6, 7, 10, 13, 16, 19."
            ),
        },
        "stai_trait_response": {
            "Description": "n/a",
            "Levels": {
                "1": "almost never",
                "2": "sometimes",
                "3": "often",
                "4": "almost always",
            },
        },
    }

    logging.info("Log a sidecar json file")
    with open(
        os.path.join(args.phenotypedir, "stai_trait.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(description, f, ensure_ascii=False, indent=4)

    logging.info("Finished")


main()
