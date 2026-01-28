#!/usr/local/bin/python

import fnmatch
import json
import os
import pandas as pd
import scipy.io as sio
import numpy as np
from PIL import Image


def get_sub_info(sourcedir, destdir):
    sub_info = []
    for _, _, files in os.walk(sourcedir):
        files.sort()
        for fname in fnmatch.filter(files, "*.txt"):
            sub_file = os.path.join(sourcedir, fname)
            fname = os.path.splitext(fname)[0]
            fparts = fname.split("_")
            sub_name = "sub-%s" % fparts[0]
            task = fparts[1]
            task = task.replace("task", "task-")
            if len(fparts) > 2:
                block = fparts[-1]
                block = block.replace("block", "block-")
            else:
                block = "n/a"

            sub_dir = os.path.join(destdir, sub_name, "beh")
            sub_info.append((sub_file, sub_name, sub_dir, task, block))
    return sub_info


def read_header(filename):
    with open(filename, "r") as myfile:
        counter = -1
        head = []
        for line in myfile:
            counter += 1
            head.append(line)
            if "Time" in line:
                break
            elif "Subject" in line:
                sub_line = counter
            elif "Description" in line:
                task_line = counter

    return (head, sub_line, task_line)


def check_header(header, sub_name, task, block):
    sub_line = header[1]
    task_line = header[2]

    sub_name = sub_name.replace("sub-", "")
    task = task.replace("-", "")
    block = block.replace("-", "")
    sub_matches = sub_name in header[0][sub_line]
    task_matches = task in header[0][task_line]
    block_matches = True

    if not "n/a" in block:
        block_match = block in header[0][task_line]

    return (sub_matches, task_matches, block_matches)


def get_df_samples(filename, header):
    skiprows = len(header[0]) - 1
    df = pd.read_csv(filename, skiprows=skiprows, low_memory=False)

    # remove samples of type message
    df = df.loc[df["Type"] != "MSG"]

    # remove columns of no info
    df.drop(["Stimulus", "Type", "Trial", "Frame", "Aux1"], axis=1, inplace=True)

    # add one column
    df["marker_value"] = 0

    # re-order columns
    df = df[
        [
            "Time",
            "L POR X [px]",
            "L POR Y [px]",
            "L EPOS X",
            "L EPOS Y",
            "L EPOS Z",
            "L Raw X [px]",
            "L Raw Y [px]",
            "L Dia X [px]",
            "L Dia Y [px]",
            "L Pupil Diameter [mm]",
            "L CR1 X [px]",
            "L CR1 Y [px]",
            "L CR2 X [px]",
            "L CR2 Y [px]",
            "L GVEC X",
            "L GVEC Y",
            "L GVEC Z",
            "L Event Info",
            "R POR X [px]",
            "R POR Y [px]",
            "R EPOS X",
            "R EPOS Y",
            "R EPOS Z",
            "R Raw X [px]",
            "R Raw Y [px]",
            "R Dia X [px]",
            "R Dia Y [px]",
            "R Pupil Diameter [mm]",
            "R CR1 X [px]",
            "R CR1 Y [px]",
            "R CR2 X [px]",
            "R CR2 Y [px]",
            "R GVEC X",
            "R GVEC Y",
            "R GVEC Z",
            "R Event Info",
            "Timing",
            "Pupil Confidence",
            "marker_value",
        ]
    ]
    return df


def get_marker_events(sourcedir, subname, task, block):
    if task in "task-02" or task in "task-03" or task in "task-04":
        block = ""
    else:
        block = block.replace("-", "")
        block = "_" + block

    filename = os.path.join(
        sourcedir,
        subname.replace("sub-", ""),
        "%s_et_event%s.mat" % (task.replace("-", ""), block),
    )
    mat_events = sio.loadmat(filename, squeeze_me=True, struct_as_record=False)
    eventdata = mat_events["eteventdata"]

    return eventdata


def get_calibration(sourcedir, subname, task, block):
    if task in "task-03" or task in "task-04":
        block = ""
    elif task in "task-02":
        block = block.replace("block-0", "_part")
    else:
        block = block.replace("-", "")
        block = "_" + block

    filename = os.path.join(
        sourcedir,
        subname.replace("sub-", ""),
        "%s_et_calibration%s.mat" % (task.replace("-", ""), block),
    )
    matfile = sio.loadmat(filename, squeeze_me=True, struct_as_record=False)
    calibration = matfile["calValInfo"]
    if isinstance(calibration.attempt, np.ndarray):
        if not calibration.attempt[-1].valResultAccept:
            return (None, None)
        cal = calibration.attempt[-1]
    else:
        if not calibration.attempt.valResultAccept:
            return (None, None)
        cal = calibration.attempt

    cal_deviations = [
        cal.validateAccuracy.deviationLX,
        cal.validateAccuracy.deviationLY,
        cal.validateAccuracy.deviationRX,
        cal.validateAccuracy.deviationRY,
    ]
    cal_deviations = np.round(cal_deviations, 3)

    points = np.vstack(
        (calibration.calibrationPoints.X, calibration.calibrationPoints.Y)
    ).T
    calinfo = {"points": points, "deviations": cal_deviations}

    im = Image.fromarray(cal.validateImage)

    return (calinfo, im)


def join_df_events(df, eventdata):
    df.drop_duplicates(subset=["Time"], inplace=True)
    indx = df["Time"].isin(eventdata.timestamp)
    if not sum(indx) == eventdata.event.shape[0]:
        eventdata.timestamp, indicies = np.unique(
            eventdata.timestamp, return_index=True
        )
        eventdata.event = eventdata.event[indicies]
        time_indx = np.isin(eventdata.timestamp, df["Time"])
        eventdata.timestamp = eventdata.timestamp[time_indx]
        eventdata.event = eventdata.event[time_indx]
        indx = df["Time"].isin(eventdata.timestamp)

    df.loc[indx, "marker_value"] = eventdata.event
    return df


def get_time_diff(df, test_events):
    mask = df["marker_value"].isin(test_events)
    ref_event = np.nonzero(mask.values)[0][0]
    time_diff = df["Time"].iloc[0] - df["Time"].iloc[ref_event]
    # convert to seconds
    time_diff = time_diff / 1e6
    time_diff = np.round(time_diff, 3)
    return time_diff


def save_files(basename, df, time_diff, calinfo):
    tsvout = basename + ".tsv"
    df.to_csv(tsvout, sep="\t", index=False, header=False)
    caltype = "HV%i" % calinfo["points"].shape[0]
    jsonstring = {
        "StartTime": time_diff,
        "CalibrationPosition": calinfo["points"].tolist(),
        "CalibrationList": {
            "Type": caltype,
            "LeftEyeDeviationX": calinfo["deviations"][0],
            "LeftEyeDeviationY": calinfo["deviations"][1],
            "RightEyeDeviationX": calinfo["deviations"][2],
            "RightEyeDeviationY": calinfo["deviations"][3],
        },
    }
    jsonout = basename + ".json"
    with open(jsonout, "w", encoding="utf-8") as f:
        json.dump(jsonstring, f, ensure_ascii=False, indent=4)


def json_smi(levels):
    jsonstring = {
        "SamplingFrequency": 250,
        "StartTime": 0,
        "Columns": [
            "left_gaze_x",
            "left_gaze_y",
            "left_eye_position_x",
            "left_eye_position_y",
            "left_eye_position_z",
            "left_pupil_position_x",
            "left_pupil_position_y",
            "left_pupil_diam_x",
            "left_pupil_diam_y",
            "left_pupil_diam_circular",
            "left_corneal_reflex1_position_x",
            "left_corneal_reflex1_position_y",
            "left_corneal_reflex2_position_x",
            "left_corneal_reflex2_position_y",
            "left_gaze_vector_x",
            "left_gaze_vector_y",
            "left_gaze_vector_z",
            "left_eye_event",
            "right_gaze_x",
            "right_gaze_y",
            "right_eye_position_x",
            "right_eye_position_y",
            "right_eye_position_z",
            "right_pupil_position_x",
            "right_pupil_position_y",
            "right_pupil_diam_x",
            "right_pupil_diam_y",
            "right_pupil_diam_circular",
            "right_corneal_reflex1_position_x",
            "right_corneal_reflex1_position_y",
            "right_corneal_reflex2_position_x",
            "right_corneal_reflex2_position_y",
            "right_gaze_vector_x",
            "right_gaze_vector_y",
            "right_gaze_vector_z",
            "right_eye_event",
            "timing",
            "pupil_confidence",
            "marker_value",
        ],
        "Manufacturer": "SensoMotoric Instruments",
        "ManufacturerModelName": "RED 250 mobile",
        "SoftwareVersions": "I View X 4.4.0",
        "SampleCoordinateUnit": "n/a",
        "SampleCoordinateSystem": "gaze-on-screen",
        "EnvironmentCoordinates": ["0,0", "top left"],
        "EventIdentifier": "n/a",
        "RawSamples": 1,
        "IncludedEyeMovementEvents": "n/a",
        "DetectionAlgorithm": "SMI BeGaze 3.7.60",
        "DetectionAlgorithmSettings": {
            "EventDetection": "high speed",
            "SaccadeDetection": {
                "MinDuration": ["Auto", "22 ms"],
                "PeakVelocityThreshold": "40 degrees/s",
                "MinFixationDuration": "50 ms",
                "PeakVelocity": {
                    "Start": "20% of saccade length",
                    "End": "80% of saccade length",
                },
                "Geometry": {
                    "StimulusScreenResolution": "1920 x 1200 px",
                    "PhysicalStimulusDimensions": "520 x 325 mm",
                    "DistanceMonitor-Head": "700 mm",
                },
            },
        },
        "CalibrationPosition": [
            [960, 600],
            [528, 114],
            [1392, 114],
            [528, 1086],
            [1392, 1086],
            [528, 600],
            [960, 114],
            [1392, 600],
            [960, 1086],
        ],
        "CalibrationUnit": "px",
        "CalibrationList": [
            [
                "HV9",
                "Left",
                "n/a",
                "n/a",
                "n/a",
            ],
            [
                "HV9",
                "Right",
                "n/a",
                "n/a",
                "n/a",
            ],
        ],
        "RecordedEye": "Both",
        "RawDataFilters": "n/a",
        "ScreenSize": "520 x 325 mm",
        "ScreenResolution": "1920 x 1200 px",
        "ScreenRefreshRate": "59 Hz",
        "PupilPositionType": "pupil on screen",
        "PupilFitMethod": "n/a",
        "left_gaze_x": {
            "Description": "Horizontal gaze position of the left eye",
            "Unit": "px",
        },
        "left_gaze_y": {
            "Description": "Vertical gaze position of the left eye",
            "Unit": "px",
        },
        "left_eye_position_x": {
            "Description": "Left eye position on X",
            "Unit": "n/a",
        },
        "left_eye_position_y": {
            "Description": "Left eye position on Y",
            "Unit": "n/a",
        },
        "left_eye_position_z": {
            "Description": "Left eye position on Z",
            "Unit": "n/a",
        },
        "left_pupil_position_x": {
            "Description": "Horizontal pupil position of the left eye",
            "Unit": "px",
        },
        "left_pupil_position_y": {
            "Description": "Vertical pupil position of the left eye",
            "Unit": "px",
        },
        "left_pupil_diam_x": {
            "Description": "Horizontal pupil diameter of the left eye",
            "Unit": "px",
        },
        "left_pupil_diam_y": {
            "Description": "Vertical pupil diameter of the left eye",
            "Unit": "px",
        },
        "left_pupil_diam_circular": {
            "Description": "Circular pupil diameter of the left eye",
            "Unit": "mm",
        },
        "left_corneal_reflex_position1_x": {
            "Description": "First horizontal conrneal reflex position of the left eye",
            "Unit": "px",
        },
        "left_corneal_reflex_position1_y": {
            "Description": "First vertical conrneal reflex position of the left eye",
            "Unit": "px",
        },
        "left_corneal_reflex_position2_x": {
            "Description": "Second horizontal conrneal reflex position of the left eye",
            "Unit": "px",
        },
        "left_corneal_reflex_position2_y": {
            "Description": "Second vertical conrneal reflex position of the left eye",
            "Unit": "px",
        },
        "left_gaze_vector_x": {
            "Description": "Gaze vector on X of the left eye",
            "Unit": "n/a",
        },
        "left_gaze_vector_y": {
            "Description": "Gaze vector on Y of the left eye",
            "Unit": "n/a",
        },
        "left_gaze_vector_z": {
            "Description": "Gaze vector on Z of the left eye",
            "Unit": "n/a",
        },
        "left_eye_event": {
            "Description": "Type of event detected for the interval containing this sample",
            "Levels": {
                "fixation": "n/a",
                "saccade": "n/a",
                "blink": "n/a",
            },
        },
        "right_gaze_x": {
            "Description": "Horizontal gaze position of the right eye",
            "Unit": "px",
        },
        "right_gaze_y": {
            "Description": "Vertical gaze position of the right eye",
            "Unit": "px",
        },
        "right_eye_position_x": {
            "Description": "right eye position on X",
            "Unit": "n/a",
        },
        "right_eye_position_y": {
            "Description": "right eye position on Y",
            "Unit": "n/a",
        },
        "right_eye_position_z": {
            "Description": "right eye position on Z",
            "Unit": "n/a",
        },
        "right_pupil_position_x": {
            "Description": "Horizontal pupil position of the right eye",
            "Unit": "px",
        },
        "right_pupil_position_y": {
            "Description": "Vertical pupil position of the right eye",
            "Unit": "px",
        },
        "right_pupil_diam_x": {
            "Description": "Horizontal pupil diameter of the right eye",
            "Unit": "px",
        },
        "right_pupil_diam_y": {
            "Description": "Vertical pupil diameter of the right eye",
            "Unit": "px",
        },
        "right_pupil_diam_circular": {
            "Description": "Circular pupil diameter of the right eye",
            "Unit": "mm",
        },
        "right_corneal_reflex_position1_x": {
            "Description": "First horizontal conrneal reflex position of the right eye",
            "Unit": "px",
        },
        "right_corneal_reflex_position1_y": {
            "Description": "First vertical conrneal reflex position of the right eye",
            "Unit": "px",
        },
        "right_corneal_reflex_position2_x": {
            "Description": "Second horizontal conrneal reflex position of the right eye",
            "Unit": "px",
        },
        "right_corneal_reflex_position2_y": {
            "Description": "Second vertical conrneal reflex position of the right eye",
            "Unit": "px",
        },
        "right_gaze_vector_x": {
            "Description": "Gaze vector on X of the right eye",
            "Unit": "n/a",
        },
        "right_gaze_vector_y": {
            "Description": "Gaze vector on Y of the right eye",
            "Unit": "n/a",
        },
        "right_gaze_vector_z": {
            "Description": "Gaze vector on Z of the right eye",
            "Unit": "n/a",
        },
        "right_eye_event": {
            "Description": "Type of event detected for the interval containing this sample",
            "Levels": {
                "fixation": "n/a",
                "saccade": "n/a",
                "blink": "n/a",
            },
        },
        "timing": {
            "Description": "Quality values",
            "Unit": "n/a",
        },
        "pupil_confidence": {
            "Description": "n/a",
            "Unit": "n/a",
        },
        "marker_value": {
            "Description": "Marker value associated with a task event",
            "Levels": levels,
        },
    }
    return jsonstring
