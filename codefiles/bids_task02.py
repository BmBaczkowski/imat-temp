#!/usr/local/bin/python


from argparse import ArgumentParser
import json
import logging
import os
import pandas as pd

from utils.utils import get_sub_info
from utils.task02_events import (
    clean_csv_responses,
    clean_csv_task,
    cat_task_responses,
    split_df,
    events_json,
)
from utils.task02_beh import get_beh, beh_json


parser = ArgumentParser(prog="bids_task02", description="", epilog="")
parser.add_argument("sourcedir", type=str, help="data source directory")
parser.add_argument("destdir", type=str, help="data output directory")
parser.add_argument("logdir", type=str, help="log directory")
args = parser.parse_args()

# logfile
logfilename = os.path.join(args.logdir, "beh_task-02.log")
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
    filename_task = os.path.join(sub_src_dir, "task02.csv")
    if not os.path.isfile(filename_task):
        mylogs.warning("%s:Datafile of task-02 not available" % sub_name)
        continue
    csv_task = clean_csv_task(filename_task)
    if csv_task.empty:
        mylogs.warning(
            ("%s:Data of task-02 unavailable " "(file exists but is empty)") % sub_name
        )
        continue
    csv_responses = pd.DataFrame()
    for i in range(1, 3):
        filename = os.path.join(sub_src_dir, "task02_responses_part%d.csv" % i)
        if not os.path.isfile(filename):
            mylogs.warning(
                ("%s:Response file of task-02 block-0%d " "not available")
                % (sub_name, i)
            )
            continue
        csv_responses = pd.concat([csv_responses, clean_csv_responses(filename)])
    csv_task_responses = cat_task_responses(csv_task, csv_responses)
    runs = split_df(csv_task_responses)
    for i, run in enumerate(runs):
        filenameout = os.path.join(
            sub_dir, ("%s_task-02_block-0%i_events.tsv" % (sub_name, i + 1))
        )
        mylogs.info(
            ("%s:Saving task-02 block-0%i events into " "tsv file task-2 block-0%i")
            % (sub_name, i + 1, i + 1)
        )
        run.to_csv(filenameout, sep="\t", index=False)
    # TASK BEH
    beh_runs = get_beh(csv_task_responses)
    for i, beh_run in enumerate(beh_runs):
        filenameout = os.path.join(
            sub_dir, ("%s_task-02_block-0%i_beh.tsv" % (sub_name, i + 1))
        )
        mylogs.info(
            ("%s:Saving task-02 block-0%i into beh" "tsv file task-02 block-0%i")
            % (sub_name, i + 1, i + 1)
        )
        beh_run.to_csv(filenameout, sep="\t", index=False)


# JSON events
mylogs.info("Log a sidecar task-02 events json file")
filenameout_json = os.path.join(args.destdir, "task-02_events.json")
with open(filenameout_json, "w", encoding="utf-8") as f:
    json.dump(events_json(), f, ensure_ascii=False, indent=4)

# JSON beh
mylogs.info("Log a sidecar task-02 beh json file")
filenameout_json = os.path.join(args.destdir, "task-02_beh.json")
with open(filenameout_json, "w", encoding="utf-8") as f:
    json.dump(beh_json(), f, ensure_ascii=False, indent=4)
