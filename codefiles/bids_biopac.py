#!/usr/local/bin/python

from argparse import ArgumentParser
import json
import logging
import numpy as np
import os
import pandas as pd
import sys

from utils.utils_biopac import (
    get_sub_info,
    read_acq_data,
    cleanmarkers,
    replaceshocks,
    get_time_diff,
    save_files,
    json_biopac,
)


# start / stop markers to trim data
task_dict = {
    "task-shockcalibration": [250, 252],
    "task-01": [110, 116],
    "task-02": [120, 126],
    "task-03": [130, 136],
    "task-04": [150, 152],
}

# first event as reference point for StartTime
events_dict = {
    "task-01": [82, 84, 86],
    "task-02": [20, 40, 100],
    "task-03": [20, 40, 100],
    "task-04": [82, 84, 86],
}

# marker levels per task
mrk_levels = {
    "task-shockcalibration": {
        "Levels": {
            "1": "US onset",
        }
    },
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


parser = ArgumentParser(prog="bids_biopac", description="", epilog="")
parser.add_argument("sourcedir", type=str, help="data source directory")
parser.add_argument("destdir", type=str, help="data output directory")
parser.add_argument("logdir", type=str, help="log directory")
args = parser.parse_args()

# logfile
logfilename = os.path.join(args.logdir, "biopac.log")
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
mylogs.critical("Export biopac data from .acq to .tsv files")

sub_info = get_sub_info(args.sourcedir, args.destdir)
for sub_file, sub_name, sub_dir in sub_info:
    mylogs.info("%s: Reading file %s" % (sub_name, os.path.basename(sub_file)))
    data = read_acq_data(sub_file)

    # clean markers
    data[:, -1] = cleanmarkers(data[:, -1])
    # replace a train of 1s (shocks) with a single instance
    data[:, -1] = replaceshocks(data[:, -1])

    # find tasks and blocks
    for key in task_dict:
        indx_start = np.where(data[:, -1] == task_dict[key][0])[0]
        indx_stop = np.where(data[:, -1] == task_dict[key][1])[0]
        if indx_start.size == 0 and indx_stop.size == 0:
            mylogs.debug(
                "%s:%s:Task not present in file %s"
                % (sub_name, key, os.path.basename(sub_file))
            )
            continue
        elif indx_start.size == 0:
            mylogs.debug(
                "%s:%s:Start marker unavailable in file %s"
                % (sub_name, key, os.path.basename(sub_file))
            )
            continue
        elif indx_stop.size == 0:
            mylogs.debug(
                "%s:%s:Stop marker unavailable in file %s"
                % (sub_name, key, os.path.basename(sub_file))
            )
            continue
        elif len(indx_start) != len(indx_stop):
            mylogs.debug(
                "%s:%s:Fix uneven number of start stop markers in file %s"
                % (sub_name, key, os.path.basename(sub_file))
            )
            indx_start = [indx_start[-1]]
        elif (len(indx_start) == len(indx_stop)) != 1:
            mylogs.debug(
                "%s:%s:Start / Stop marker more than once in file %s"
                % (sub_name, key, os.path.basename(sub_file))
            )

        # remove task on / off markers
        indx_start[0] = indx_start[0] + 1
        indx_stop[0] = indx_stop[0] - 1

        if key == "task-01":
            indx_pause_start = np.where(data[:, -1] == 112)[0]
            indx_pause_start = indx_pause_start - 1
            indx_pause_stop = np.where(data[:, -1] == 114)[0]
            indx_pause_stop = indx_pause_stop + 1
            segments = np.array(
                (
                    [indx_start[0], indx_pause_start[0]],
                    [indx_pause_stop[0], indx_pause_start[1]],
                    [indx_pause_stop[1], indx_stop[0]],
                )
            )
            for count, val in enumerate(segments):
                task = data[val[0] : val[1], :]
                time_diff = get_time_diff(task, events_dict[key])
                task = task[:, 1:]
                task_basename = os.path.join(
                    sub_dir,
                    "%s_%s_block-0%i_recording-biopac_physio"
                    % (sub_name, key, count + 1),
                )
                save_files(task_basename, task, time_diff)
                mylogs.info(
                    "%s:%s:block-0%i:Saving data into .tsv file"
                    % (sub_name, key, count + 1)
                )

        elif key == "task-02":
            indx_pause_start = np.where(data[:, -1] == 122)[0]
            indx_pause_start = indx_pause_start - 1
            indx_pause_stop = np.where(data[:, -1] == 124)[0]
            indx_pause_stop = indx_pause_stop + 1
            segments = np.array(
                (
                    [indx_start[0], indx_pause_start[0]],
                    [indx_pause_stop[0], indx_stop[0]],
                )
            )
            for count, val in enumerate(segments):
                task = data[val[0] : val[1], :]
                time_diff = get_time_diff(task, events_dict[key])
                task = task[:, 1:]
                task_basename = os.path.join(
                    sub_dir,
                    "%s_%s_block-0%i_recording-biopac_physio"
                    % (sub_name, key, count + 1),
                )
                save_files(task_basename, task, time_diff)
                mylogs.info(
                    "%s:%s:block-0%i:Saving data into .tsv file"
                    % (sub_name, key, count + 1)
                )

        else:
            task = data[indx_start[0] : indx_stop[0], :]
            if key == "task-shockcalibration":
                time_diff = 0
            else:
                time_diff = get_time_diff(task, events_dict[key])
            task = task[:, 1:]
            task_basename = os.path.join(
                sub_dir, "%s_%s_recording-biopac_physio" % (sub_name, key)
            )
            save_files(task_basename, task, time_diff)
            mylogs.info("%s:%s:Saving data into .tsv file" % (sub_name, key))

for key in task_dict:
    mylogs.info("Log a json sidecar file for task %s" % key)
    filenameout_json = os.path.join(
        args.destdir, "%s_recording-biopac_physio.json" % key
    )
    with open(filenameout_json, "w", encoding="utf-8") as f:
        json.dump(
            json_biopac(mrk_levels[key]["Levels"]), f, ensure_ascii=False, indent=4
        )
