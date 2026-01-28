#!/usr/local/bin/python

from argparse import ArgumentParser
import json
import logging
import numpy as np
import os
import pandas as pd


def main():
    parser = ArgumentParser(prog="bids_participants", description="", epilog="")
    parser.add_argument("sourcedir", type=str, help="data source directory")
    parser.add_argument("destdir", type=str, help="data output directory")
    args = parser.parse_args()

    FILEOUT = os.path.join(args.destdir, "participants.tsv")

    # store logfile for debugging
    logfilesdir = os.path.join(args.destdir, "logfiles")
    logfile = os.path.join(logfilesdir, "participants.log")
    logging.basicConfig(
        filename=logfile, encoding="utf-8", filemode="w", level=logging.DEBUG
    )

    # init log info
    logging.info("Export limesurvey data into participants.tsv file")

    # read in the limesurvey file
    df = pd.read_csv(os.path.join(args.sourcedir, "results_en.tsv"), sep="\t")

    # subsetting variables
    df = df[["ID", "AGE", "SEX", "EXPERIMENTS", "PASTEXPERIMENTS[SQ001]"]]

    # rename columns
    df.rename(
        columns={
            "ID": "participant_id",
            "AGE": "age",
            "SEX": "sex",
            "EXPERIMENTS": "n_of_past_experiments",
            "PASTEXPERIMENTS[SQ001]": "similar_past_experiments",
        },
        inplace=True,
    )

    # rename subject ids
    for i in df["participant_id"]:
        df["participant_id"].replace(i, "sub-%i" % i, inplace=True)

    # replace NaN with "n/a"
    df.fillna("n/a", inplace=True)

    # save the data frame
    logging.info("Saving limesurvey data into participants.tsv file")
    df.to_csv(FILEOUT, sep="\t", index=False)

    # create a sidecar json file
    description = {
        "age": {
            "Description": "age of the participant",
            "Units": "years",
        },
        "sex": {
            "Description": "sex of the participant as reported by the participant",
            "Levels": {
                "M": "male",
                "F": "female",
            },
        },
        "n_of_past_experiments": {
            "Description": (
                "estimated number of studies the participant "
                "previously took part as reported by the participant"
            ),
            "Units": "integer",
        },
        "similar_past_experiments": {
            "Description": (
                "estimated possibility whether the participant "
                "previously took part in a similar study "
                "(i.e., with electric shocks) as reported by the participant"
            ),
            "Levels": {
                "Y": "yes",
                "N": "no",
                "U": "unsure",
            },
        },
    }

    logging.info("Log a sidecar json file")
    with open(
        os.path.join(args.destdir, "participants.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(description, f, ensure_ascii=False, indent=4)

    logging.info("Finished")


main()
