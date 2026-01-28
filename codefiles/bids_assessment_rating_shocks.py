#!/usr/local/bin/python

from argparse import ArgumentParser
import json
import logging
import numpy as np
import os
import pandas as pd


def main():
    parser = ArgumentParser(prog="bids_assessment_data", description="", epilog="")
    parser.add_argument("sourcedir", type=str, help="data source directory")
    parser.add_argument("destdir", type=str, help="data output directory")
    parser.add_argument("logdir", type=str, help="log directory")
    args = parser.parse_args()

    FILEOUT = os.path.join(args.destdir, "ratings_tasks_with_shocks.tsv")

    # prepare the log for debugging
    logfile = os.path.join(args.logdir, "ratings_tasks_with_shocks.log")
    logging.basicConfig(
        filename=logfile, encoding="utf-8", filemode="w", level=logging.DEBUG
    )

    logging.info("Reading in the file")

    # read in the file
    df = pd.read_csv(os.path.join(args.sourcedir, "logbook.tsv"), sep="\t")

    # remove empty rows
    df = df[df["Experimentator"].isnull() == False]

    # subsetting variables
    df = df[
        [
            "Participant",
            "Volts",
            "shockRating",
            "fearRating",
            "nSchocks1",
            "surpriseRating",
            "nShocks2",
        ]
    ]

    df.rename(
        columns={
            "Participant": "participant_id",
            "Volts": "volts",
            "shockRating": "shock_rating",
            "fearRating": "fear_rating",
            "nSchocks1": "n_shocks_task02",
            "nShocks2": "n_shocks_task03",
            "surpriseRating": "surprise_rating",
        },
        inplace=True,
    )

    # rename subject id
    for i in df["participant_id"]:
        df["participant_id"].replace(i, "sub-%i" % i, inplace=True)

    # replace NaN with "n/a"
    df.fillna("n/a", inplace=True)

    logging.info(
        (
            "Saving logbook data of ratings about the tasks with "
            "shocks into assessment/ tsv file"
        )
    )
    df.to_csv(FILEOUT, sep="\t", index=False)

    # create a sidecar json file
    description = {
        "volts": {
            "Description": (
                "Stimulus output level as indicated by the stimulation device"
            ),
            "Units": "volts",
        },
        "shock_rating": {
            "Description": (
                "Shock intensity felt during task 02 as indicated by "
                "the participant on pain intensity scale"
            ),
            "Levels": {
                "0": "No sensation",
                "1": "n/a",
                "2": "n/a",
                "3": "n/a",
                "4": "n/a",
                "5": "n/a",
                "6": "n/a",
                "7": "n/a",
                "8": "n/a",
                "9": "n/a",
                "10": "Very high intensity",
            },
        },
        "fear_rating": {
            "Description": (
                "Intensity of fear felt during the task 02 "
                "as indicated by the participant on a scale"
            ),
            "Levels": {
                "0": "No fear at all",
                "1": "n/a",
                "2": "n/a",
                "3": "n/a",
                "4": "n/a",
                "5": "n/a",
                "6": "n/a",
                "7": "n/a",
                "8": "n/a",
                "9": "n/a",
                "10": "Extreme fear",
            },
        },
        "n_shocks_task02": {
            "Description": (
                "Estimated number of shocks received during "
                "the task 02 as indicated by the participant"
            ),
            "Units": "integer",
        },
        "n_shocks_task03": {
            "Description": (
                "Estimated number of shocks received during "
                "the task 03 as indicated by the participant"
            ),
            "Units": "integer",
        },
        "surprise_rating": {
            "Description": (
                "How surprised was a participant by the fact that there were "
                "no shocks delivered in task 03"
            ),
            "Levels": {
                "0": "not surprised at all",
                "1": "n/a",
                "2": "n/a",
                "3": "n/a",
                "4": "n/a",
                "5": "very surprised",
            },
        },
    }

    logging.info("Log a sidecar json file")
    with open(
        os.path.join(args.destdir, "ratings_tasks_with_shocks.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(description, f, ensure_ascii=False, indent=4)
    logging.info("Finished")


main()
