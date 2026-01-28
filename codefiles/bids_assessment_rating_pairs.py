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

    FILEOUT = os.path.join(args.destdir, "ratings_tasks_with_pairs.tsv")

    # prepare the log for debugging
    logfile = os.path.join(args.logdir, "ratings_tasks_with_pairs.log")
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
            "TASK01DIFFICULTY[SQ001]",
            "TASK01PERFORMANCE[SQ001]",
            "TASK04DIFFICULTY[SQ001]",
            "TASK04PERFORMANCE[SQ001]",
        ]
    ]

    df.rename(
        columns={
            "ID": "participant_id",
        },
        inplace=True,
    )

    # rename subject id
    for i in df["participant_id"]:
        df["participant_id"].replace(i, "sub-%i" % i, inplace=True)

    # replace NaN with "n/a"
    df.fillna("n/a", inplace=True)

    # reshape from wide to long: difficulty
    df1 = pd.melt(
        df,
        id_vars=["participant_id"],
        value_vars=["TASK01DIFFICULTY[SQ001]", "TASK04DIFFICULTY[SQ001]"],
        var_name="task_id",
        value_name="difficulty_rating",
    )

    # replace A-values
    df1.replace(
        ["A1", "A2", "A3", "A4", "A5", "A6"], [1, 2, 3, 4, 5, "n/a"], inplace=True
    )
    df1.replace(
        ["TASK01DIFFICULTY[SQ001]", "TASK04DIFFICULTY[SQ001]"],
        ["task-01", "task-04"],
        inplace=True,
    )

    # reshape from wide to long: performance
    df2 = pd.melt(
        df,
        id_vars=["participant_id"],
        value_vars=["TASK01PERFORMANCE[SQ001]", "TASK04PERFORMANCE[SQ001]"],
        var_name="task_id",
        value_name="performance_rating",
    )

    # replace A-values
    df2.replace(
        ["A1", "A2", "A3", "A4", "A5", "A6", "A7"],
        [1, 2, 3, 4, 5, 6, "n/a"],
        inplace=True,
    )
    df2.replace(
        ["TASK01PERFORMANCE[SQ001]", "TASK04PERFORMANCE[SQ001]"],
        ["task-01", "task-04"],
        inplace=True,
    )

    # concate both data frames
    df = df1.merge(df2)

    logging.info(
        (
            "Saving limesurvey data of ratings about the tasks "
            "with pairs into assessment/ tsv file"
        )
    )
    df.to_csv(FILEOUT, sep="\t", index=False)

    # create a sidecar json file
    description = {
        "task_id": {
            "Description": "Id of the task to which the rating refers",
            "Levels": {
                "task-01": "Rating relates to the first task",
                "task-04": "Rating relates to the last task",
            },
        },
        "difficulty_rating": {
            "Description": (
                "Question to task-01:"
                "How difficult was the first task "
                "(learning the combinations between sounds and symbols)? "
                "Question to task-04: "
                "How difficult was the last task "
                "-- the task that involved "
                "combining sounds and symbols?"
            ),
            "Levels": {
                "1": "very easy",
                "2": "n/a",
                "3": "n/a",
                "4": "n/a",
                "5": "very difficult",
            },
        },
        "performance_rating": {
            "Description": (
                "Question to task-01: "
                "How well do you think you performed "
                "on the first task? Question to task-04: "
                "How well do you think your performance "
                "was on the last task?"
            ),
            "Levels": {
                "1": "0%",
                "2": "20%",
                "3": "40%",
                "4": "60%",
                "5": "80%",
                "6": "100%",
            },
        },
    }

    logging.info("Log a sidecar json file")
    with open(
        os.path.join(args.destdir, "ratings_tasks_with_pairs.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(description, f, ensure_ascii=False, indent=4)
    logging.info("Finished")


main()
