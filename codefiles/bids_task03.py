#!/usr/local/bin/python

from argparse import ArgumentParser
import json
import logging
import os
import pandas as pd

from utils.utils import get_sub_info
from utils.task03_events import (
    clean_csv_responses,
    clean_csv_task,
    cat_task_responses,
    events_json,
)
from utils.task03_beh import get_beh, beh_json


parser = ArgumentParser(prog="bids_task03", description="", epilog="")
parser.add_argument("sourcedir", type=str, help="data source directory")
parser.add_argument("destdir", type=str, help="data output directory")
parser.add_argument("logdir", type=str, help="log directory")
args = parser.parse_args()

# logfile
logfilename = os.path.join(args.logdir, "beh_task-03.log")

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
    filename_task = os.path.join(sub_src_dir, "task03.csv")
    if not os.path.isfile(filename_task):
        mylogs.warning("%s:Datafile of task-03 not available" % sub_name)
        continue
    csv_task = clean_csv_task(filename_task)
    if csv_task.empty:
        mylogs.warning(
            ("%s:Data of task-03 unavailable " "(file exists but is empty)") % sub_name
        )
        continue
    filename = os.path.join(sub_src_dir, "task03_responses.csv")
    if not os.path.isfile(filename):
        mylogs.warning("%s:Response file of task-03 not available" % sub_name)
        continue
    csv_responses = clean_csv_responses(filename)
    csv_task_responses = cat_task_responses(csv_task, csv_responses)
    filenameout = os.path.join(sub_dir, "%s_task-03_events.tsv" % sub_name)
    mylogs.info("%s:Saving task-03 events into tsv file" % sub_name)
    csv_task_responses.to_csv(filenameout, sep="\t", index=False)

    # TASK BEH
    beh_task = get_beh(csv_task_responses)
    filenameout = os.path.join(sub_dir, "%s_task-03_beh.tsv" % sub_name)
    mylogs.info("%s:Saving task-03 beh into tsv file" % sub_name)
    beh_task.to_csv(filenameout, sep="\t", index=False)

# JSON events
mylogs.info("Log a sidecar task-03 events json file")
filenameout_json = os.path.join(args.destdir, "task-03_events.json")
with open(filenameout_json, "w", encoding="utf-8") as f:
    json.dump(events_json(), f, ensure_ascii=False, indent=4)

# JSON beh
mylogs.info("Log a sidecar task-03 beh json file")
filenameout_json = os.path.join(args.destdir, "task-03_beh.json")
with open(filenameout_json, "w", encoding="utf-8") as f:
    json.dump(beh_json(), f, ensure_ascii=False, indent=4)
