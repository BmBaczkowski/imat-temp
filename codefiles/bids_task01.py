#!/usr/local/bin/python

from argparse import ArgumentParser
import json
import logging
import numpy as np
import os
import pandas as pd

from utils.utils import get_sub_info
from utils.task01_events import (
    clean_csv_responses,
    clean_csv_task,
    cat_task_responses,
    split_df,
    events_json,
)
from utils.task01_afc import get_afc, afc_json


parser = ArgumentParser(prog="bids_task01", description="", epilog="")
parser.add_argument("sourcedir", type=str, help="data source directory")
parser.add_argument("destdir", type=str, help="data output directory")
parser.add_argument("logdir", type=str, help="log directory")
args = parser.parse_args()

# logfile
logfilename = os.path.join(args.logdir, "beh_task-01.log")
mylogs = logging.getLogger()
mylogs.setLevel(logging.NOTSET)

logfile = logging.FileHandler(logfilename, mode="w")
logfile.setLevel(logging.CRITICAL)
stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
stream.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))

mylogs.addHandler(logfile)
mylogs.addHandler(stream)

# init log info
mylogs.critical("Export psychtoolbox data")

sub_info = get_sub_info(args.sourcedir, args.destdir)

for sub_src_dir, sub_name, sub_dir in sub_info:
    mylogs.info("%s:Reading files" % sub_name)

    # TASK EVENTS
    filename_task = os.path.join(sub_src_dir, "task01.csv")
    if not os.path.isfile(filename_task):
        mylogs.warning("%s:Datafile of task-01 not available" % sub_name)
        continue
    csv_task = clean_csv_task(filename_task)
    if csv_task.empty:
        mylogs.warning(
            ("%s:Data of task-01 unavailable " "(file exists but is empty)") % sub_name
        )
        continue
    csv_responses = pd.DataFrame()
    for i in range(1, 4):
        filename = os.path.join(sub_src_dir, "task01_responses_block0%d.csv" % i)
        if not os.path.isfile(filename):
            mylogs.warning(
                ("%s:Response file of task-01 block-0%d " "not available")
                % (sub_name, i)
            )
            continue
        csv_responses = pd.concat([csv_responses, clean_csv_responses(filename, i)])
    csv_task_responses = cat_task_responses(csv_task, csv_responses)
    runs = split_df(csv_task_responses)
    for i, run in enumerate(runs):
        filenameout = os.path.join(
            sub_dir, ("%s_task-01_block-0%i_events.tsv" % (sub_name, i + 1))
        )
        mylogs.info(
            ("%s:Saving task-01 block-0%i events into " "tsv file task-01 block-%i")
            % (sub_name, i + 1, i + 1)
        )
        run.to_csv(filenameout, sep="\t", index=False)

    # AFC
    afc_runs = get_afc(filename_task)
    for i, afc_run in enumerate(afc_runs):
        filenameout = os.path.join(
            sub_dir, ("%s_task-01_subtask-afc_block-0%i_beh.tsv" % (sub_name, i + 1))
        )
        mylogs.info(
            (
                "%s:Saving task-01 block-0%i afc into "
                "tsv file task-01 subtask-afc block-0%i"
            )
            % (sub_name, i + 1, i + 1)
        )
        afc_run.to_csv(filenameout, sep="\t", index=False)

# JSON task-01_events
mylogs.info("Log a sidecar task-01 events json file")
filenameout_json = os.path.join(args.destdir, "task-01_events.json")
with open(filenameout_json, "w", encoding="utf-8") as f:
    json.dump(events_json(), f, ensure_ascii=False, indent=4)

# JSON task-01_beh-afc
mylogs.info("Log a sidecar task-01 beh-afc json file")
filenameout_json = os.path.join(args.destdir, "task-01_subtask-afc_beh.json")
with open(filenameout_json, "w", encoding="utf-8") as f:
    json.dump(afc_json(), f, ensure_ascii=False, indent=4)
