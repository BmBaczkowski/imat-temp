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

    FILEOUT = os.path.join(args.destdir, "logbook.json")

    # prepare the log for debugging
    logfile = os.path.join(args.logdir, "logbook.log")
    logging.basicConfig(
        filename=logfile, encoding="utf-8", filemode="w", level=logging.DEBUG
    )

    logging.info("Reading in the file")

    # read in the file
    df = pd.read_csv(os.path.join(args.sourcedir, "logbook.tsv"), sep="\t")
    df = df[df["Experimentator"].isnull() == False]

    # subsetting variables
    df = df[
        [
            "Participant",
            "Experimentator",
            "Comments",
        ]
    ]

    df.rename(
        columns={
            "Participant": "participant_id",
            "Experimentator": "experimentator",
            "Comments": "comments",
        },
        inplace=True,
    )

    # rename subject id
    for i in df["participant_id"]:
        df["participant_id"].replace(i, "sub-%i" % i, inplace=True)

    # replace NaN with "n/a"
    df.fillna("n/a", inplace=True)

    # convert to json
    jsonstring = json.loads(df.to_json(orient="records"))

    logging.info("Saving logbook data into assessment/ json file")
    with open(FILEOUT, "w", encoding="utf-8") as f:
        json.dump(jsonstring, f, ensure_ascii=False, indent=4)

    logging.info("Finished")


main()
