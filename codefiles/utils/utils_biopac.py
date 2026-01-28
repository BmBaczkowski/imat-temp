#!/usr/local/bin/python

import bioread
import fnmatch
import json
import os
import numpy as np


def get_sub_info(sourcedir, destdir):
    sub_info = []
    for _, _, files in os.walk(sourcedir):
        files.sort()
        for fname in fnmatch.filter(files, "*.acq"):
            sub_file = os.path.join(sourcedir, fname)
            sub_name = "sub-%s" % fname[:4]
            sub_dir = os.path.join(destdir, sub_name, "beh")
            sub_info.append((sub_file, sub_name, sub_dir))
    return sub_info


def read_acq_data(fname):
    # read the data
    biopacdata = bioread.read(fname)
    # re-code markers
    # from volts (5) to binary (1) codes
    digit_channels = np.empty([len(biopacdata.channels[0].data), 8])
    for i in range(2, 10):
        digit_channels[:, i - 2] = biopacdata.channels[i].data
    digit_channels = np.where(digit_channels == 5, 1, 0)
    # from binary to integer
    digit_channels = np.packbits(digit_channels, axis=1, bitorder="little")
    # channel with time index
    time_indx = biopacdata.channels[0].time_index
    # create new data table
    data = np.column_stack(
        (
            time_indx,
            biopacdata.channels[0].data,
            biopacdata.channels[1].data,
            np.squeeze(digit_channels),
        )
    )
    return data


def cleanmarkers(markers):
    # replace a train of repeated consequtive markers
    # into a single instance
    # e.g., __"1""1""1"__ into __"1"__
    cleaned = np.zeros(len(markers))
    derivative = np.append(0, np.diff(markers))
    derivative[derivative <= 0] = 0
    indx = np.where(derivative > 0)[0]
    cleaned[indx] = markers[indx]
    return cleaned


def replaceshocks(cleanedmarkers):
    # replace a train of stimulus application
    # into a single marker
    # i.e., __1__1__1__1__ into __1__
    indx = np.where(cleanedmarkers == 1)
    derivative = np.diff(np.append(0, indx))
    indx = np.delete(indx, np.where(derivative > 50))
    cleanedmarkers[indx] = 0
    return cleanedmarkers


def get_time_diff(task, test_events):
    mask = np.isin(task[:, -1], test_events)
    ref_event = np.nonzero(mask)[0][0]
    time_diff = task[0, 0] - task[ref_event, 0]
    time_diff = np.round(time_diff, 3)
    return time_diff


def save_files(task_basename, task, time_diff):
    tsvout = task_basename + ".tsv"
    np.savetxt(tsvout, task, fmt="%f\t%f\t%d")

    jsonstring = {
        "StartTime": time_diff,
    }
    jsonout = task_basename + ".json"
    with open(jsonout, "w", encoding="utf-8") as f:
        json.dump(jsonstring, f, ensure_ascii=False, indent=4)


def json_biopac(levels):
    jsonstring = {
        "SamplingFrequency": 500,
        "StartTime": 0,
        "Columns": ["skin_conductance", "ecg", "marker_value"],
        "Manufacturer": "Biopac Systems Inc",
        "ManufacturerModelName": "MP150",
        "SoftwareVersions": "AcqKnowledge 5.0.5",
        "skin_conductance": {
            "Description": "Continous skin conductance measurment",
            "Units": "microsiemens",
        },
        "ecg": {
            "Description": "Continous recording of the heart's electrical activity",
            "Units": "volts",
        },
        "marker_value": {
            "Description": "Marker value associated with an event",
            "Levels": levels,
        },
    }
    return jsonstring
