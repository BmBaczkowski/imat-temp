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

    FILEOUT = os.path.join(args.destdir, "free_text_data.json")

    # prepare the log for debugging
    logfile = os.path.join(args.logdir, "free_text_data.log")
    logging.basicConfig(
        filename=logfile, encoding="utf-8", filemode="w", level=logging.DEBUG
    )

    logging.info("Reading in the file")

    # read in the file
    df = pd.read_csv(os.path.join(args.sourcedir, "results_en.tsv"), sep="\t")

    # subsetting variables
    df = df[
        [
            "ID",
            "TASK01RULE",
            "TASK01STRATEGY",
            "TASKSHOCKRULE",
            "TASKSHOCKSSTRATEGY",
            #           "FEEDBACK",
        ]
    ]

    df.rename(
        columns={
            "ID": "participant_id",
            "TASK01RULE": "task_with_pairs_rule_description",
            "TASK01STRATEGY": "task_with_pairs_strategy_description",
            "TASKSHOCKRULE": "tasks_with_shocks_rule_description",
            "TASKSHOCKSSTRATEGY": "tasks_with_shocks_strategy_description",
            #           "FEEDBACK": "feedback",
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

    logging.info("Saving participant free text data into assessment/ json file")
    with open(FILEOUT, "w", encoding="utf-8") as f:
        json.dump(jsonstring, f, ensure_ascii=False, indent=4)

    logging.info("Finished")


main()
