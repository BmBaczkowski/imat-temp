#!/usr/local/bin/python

from argparse import ArgumentParser
import json
import logging
import os
import pandas as pd

from utils.utils import get_sub_info
from utils.task04_beh import get_beh, beh_json
from utils.task04_events import clean_csv_task, events_json


parser = ArgumentParser(prog="bids_task04", description="", epilog="")
parser.add_argument("sourcedir", type=str, help="data source directory")
parser.add_argument("destdir", type=str, help="data output directory")
parser.add_argument("logdir", type=str, help="log directory")
args = parser.parse_args()

# logfile
logfilename = os.path.join(args.logdir, "beh_task-04.log")
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

    filename_task = os.path.join(sub_src_dir, "task04.csv")
    if not os.path.isfile(filename_task):
        mylogs.warning("%s:Datafile of task-04 not available" % sub_name)
        continue
    # TASK BEH
    beh_task = get_beh(filename_task)
    if beh_task.empty:
        mylogs.warning(
            ("%s:Data of task-04 unavailable " "(file exists but is empty)") % sub_name
        )
        continue
    filenameout = os.path.join(sub_dir, "%s_task-04_beh.tsv" % sub_name)
    mylogs.info("%s:Saving task-04 beh into tsv file" % sub_name)
    beh_task.to_csv(filenameout, sep="\t", index=False)
    # TASK EVENTS
    task_events = clean_csv_task(filename_task)
    filenameout = os.path.join(sub_dir, "%s_task-04_events.tsv" % sub_name)
    mylogs.info("%s:Saving task-04 events into tsv file" % sub_name)
    task_events.to_csv(filenameout, sep="\t", index=False)


mylogs.info("%s:Log a sidecar task-04 beh json file" % sub_name)
filenameout_json = os.path.join(args.destdir, "task-04_beh.json")
with open(filenameout_json, "w", encoding="utf-8") as f:
    json.dump(beh_json(), f, ensure_ascii=False, indent=4)

mylogs.info("%s:Log a sidecar task-04 events json file" % sub_name)
filenameout_json = os.path.join(args.destdir, "task-04_events.json")
with open(filenameout_json, "w", encoding="utf-8") as f:
    json.dump(events_json(), f, ensure_ascii=False, indent=4)
