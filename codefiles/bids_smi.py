#!/usr/local/bin/python

from argparse import ArgumentParser
import json
import logging
import numpy as np
import os
import pandas as pd
import sys
from PIL import Image


from utils.utils_smi import (
    get_sub_info,
    read_header,
    check_header,
    get_df_samples,
    get_marker_events,
    get_calibration,
    join_df_events,
    get_time_diff,
    save_files,
    json_smi,
)


# first event as reference point for StartTime
events_dict = {
    "task-01": [82, 84, 86],
    "task-02": [20, 40, 100],
    "task-03": [20, 40, 100],
    "task-04": [82, 84, 86],
}

# marker levels per task
mrk_levels = {
    "task-01": {
        "Levels": {
            "82": "Onset of sound condition S1",
            "84": "Onset of sound condition S2",
            "86": "Onset of sound condition S3",
            "10": "Onset of image condition A1 associated with S1",
            "20": "Onset of image condition A2 associated with S1",
            "30": "Onset of image condition B1 associated with S2",
            "40": "Onset of image condition B2 associated with S2",
            "50": "Onset of image condition C1 associated with S3",
            "60": "Onset of image condition C2 associated with S3",
            "80": "fixation cross onset",
            "92": "alternative forced choice onset",
        }
    },
    "task-02": {
        "Levels": {
            "1": "US onset",
            "20": "Condition type A2 / CS- onset",
            "22": "Condition type A2 / CS- offset",
            "40": "Condition type B2 / CS+ onset",
            "42": "Condition type B2 / CS+ offset",
            "94": "Scene image onset",
            "100": "Condition type B2 / CS+ onset followed by the shock",
            "102": "Condition type B2 / CS+ offset",
        }
    },
    "task-03": {
        "Levels": {
            "10": "Onset of image condition A1 associated with S1",
            "20": "Onset of image condition A2 associated with S1",
            "30": "Onset of image condition B1 associated with S2",
            "40": "Onset of image condition B2 associated with S2",
            "50": "Onset of image condition C1 associated with S3",
            "60": "Onset of image condition C2 associated with S3",
            "82": "Onset of sound S1",
            "84": "Onset of sound S2",
            "86": "Onset of sound S3",
            "94": "Scene image onset",
        }
    },
    "task-04": {
        "Levels": {
            "82": "Onset of sound S1",
            "84": "Onset of sound S2",
            "86": "Onset of sound S3",
        }
    },
}


parser = ArgumentParser(prog="bids_smi", description="", epilog="")
parser.add_argument("sourcedir_samples", type=str, help="data source directory")
parser.add_argument("sourcedir_mat", type=str, help="data source directory")
parser.add_argument("destdir", type=str, help="data output directory")
parser.add_argument("logdir", type=str, help="log directory")
args = parser.parse_args()

# logfile
logfilename = os.path.join(args.logdir, "smi.log")
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
mylogs.critical("Export eye-tracking data to .tsv files")

sub_info = get_sub_info(args.sourcedir_samples, args.destdir)
for sub_file, sub_name, sub_dir, task, block in sub_info:
    mylogs.info("%s: Reading file %s" % (sub_name, os.path.basename(sub_file)))
    header = read_header(sub_file)
    if not all(check_header(header, sub_name, task, block)):
        mylogs.warning(
            "%s:%s: File does not match the subject"
            % (sub_name, os.path.basename(sub_file))
        )
    df = get_df_samples(sub_file, header)
    eventdata = get_marker_events(args.sourcedir_mat, sub_name, task, block)
    calinfo, im = get_calibration(args.sourcedir_mat, sub_name, task, block)
    if calinfo is None:
        mylogs.warning(
            "%s:%s: Calibration info unavailable"
            % (sub_name, os.path.basename(sub_file))
        )
        continue

    df = join_df_events(df, eventdata)
    time_diff = get_time_diff(df, events_dict[task])
    # remove timestamps from data frame
    df.drop(["Time"], axis=1, inplace=True)
    df.fillna("n/a", inplace=True)

    if task in "task-03" or task in "task-04":
        block = ""
    else:
        block = "_" + block

    filename_out = os.path.join(
        sub_dir, "%s_%s%s_recording-eyetracking_physio" % (sub_name, task, block)
    )
    save_files(filename_out, df, time_diff, calinfo)
    mylogs.info("%s:%s:Saving data into .tsv file" % (sub_name, task))

    im.save(filename_out.replace("physio", "photo") + ".png")
    mylogs.info("%s:%s:Saving calibration image file" % (sub_name, task))


for key in mrk_levels:
    mylogs.info("Log a json sidecar file for task %s" % key)
    filenameout_json = os.path.join(
        args.destdir, "%s_recording-eyetracking_physio.json" % key
    )
    with open(filenameout_json, "w", encoding="utf-8") as f:
        json.dump(json_smi(mrk_levels[key]["Levels"]), f, ensure_ascii=False, indent=4)
