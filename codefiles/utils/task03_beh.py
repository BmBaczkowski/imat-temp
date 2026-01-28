#!/usr/local/bin/python

import pandas as pd
import numpy as np
import json

from utils.utils import get_indx


def get_beh(csv_task):
    conds_indx = csv_task["event_type"].apply(
        lambda x: True if x in ["S1", "S2", "S3"] else False
    )
    task_beh = csv_task.loc[conds_indx, "event_type"].copy(deep=True).to_frame()
    task_beh["sound_stim_id"] = csv_task.loc[conds_indx, "stim_id"]
    sound_indx = conds_indx[conds_indx].index
    stop_indx = task_beh.index[1:].append(pd.Index([csv_task.index[-1]]))
    indx_scene = get_indx(
        csv_task["event_type"],
        task_beh.index,
        sound_indx,
        "scene",
        stop_indx=stop_indx,
    )
    indx_image = get_indx(
        csv_task["event_type"],
        task_beh.index,
        sound_indx,
        "[A-C]",
        stop_indx=indx_scene.values,
    )
    indx_response_to_sound = get_indx(
        csv_task["event_type"],
        task_beh.index,
        sound_indx,
        "response",
        stop_indx=indx_image.values,
    )
    indx_response_to_image = get_indx(
        csv_task["event_type"],
        task_beh.index,
        indx_image.values,
        "response",
        stop_indx=indx_scene.values,
    )
    task_beh["symbol_stim_id"] = csv_task.loc[indx_image.values, "stim_id"].values
    task_beh["symbol"] = csv_task.loc[indx_image.values, "event_type"].values

    # responses
    # to sound onset
    intersection_sound = sound_indx.intersection(indx_response_to_sound.index)
    task_beh["response_to_sound"] = "n/a"
    task_beh.loc[indx_response_to_sound.index, "response_to_sound"] = csv_task.loc[
        indx_response_to_sound, "event_type"
    ].values
    response_time = (
        csv_task.loc[indx_response_to_sound, "onset"].values
        - csv_task.loc[intersection_sound, "onset"].values
    )
    response_time = response_time.astype(float).round(3)
    task_beh["response_to_sound_time"] = "n/a"
    task_beh.loc[indx_response_to_sound.index, "response_to_sound_time"] = response_time

    # to image onset
    intersection_image = indx_image.index.intersection(indx_response_to_image.index)
    intersection_image = indx_image[intersection_image].values
    task_beh["response_to_image"] = "n/a"
    task_beh.loc[indx_response_to_image.index, "response_to_image"] = csv_task.loc[
        indx_response_to_image, "event_type"
    ].values
    response_time = (
        csv_task.loc[indx_response_to_image, "onset"].values
        - csv_task.loc[intersection_image, "onset"].values
    )
    response_time = response_time.astype(float).round(3)
    task_beh["response_to_image_time"] = "n/a"
    task_beh.loc[indx_response_to_image.index, "response_to_image_time"] = response_time

    # re-code response
    task_beh.loc[
        task_beh["response_to_sound"].str.contains("left"), "response_to_sound"
    ] = "yes"
    task_beh.loc[
        task_beh["response_to_sound"].str.contains("right"), "response_to_sound"
    ] = "no"
    task_beh.loc[
        task_beh["response_to_sound"].str.contains("other"), "response_to_sound"
    ] = "other"

    task_beh.loc[
        task_beh["response_to_image"].str.contains("left"), "response_to_image"
    ] = "yes"
    task_beh.loc[
        task_beh["response_to_image"].str.contains("right"), "response_to_image"
    ] = "no"
    task_beh.loc[
        task_beh["response_to_image"].str.contains("other"), "response_to_image"
    ] = "other"

    task_beh.reset_index(drop=True, inplace=True)

    task_beh["trial_nr"] = [i for i in range(1, task_beh.shape[0] + 1)]
    task_beh.rename(columns={"event_type": "sound"}, inplace=True)
    task_beh = task_beh[
        [
            "trial_nr",
            "sound",
            "sound_stim_id",
            "symbol",
            "symbol_stim_id",
            "response_to_sound",
            "response_to_sound_time",
            "response_to_image",
            "response_to_image_time",
        ]
    ]
    return task_beh


def beh_json():
    jsonstring = {
        "TaskName": "Test task",
        "Instructions": "",
        "TaskDescription": "",
        "InstitutionName": "Universitaet Hamburg",
        "InstitutionAddress": "Hamburg, DE",
        "InstitutionalDepartmentName": "Department of Cognitive Psychology",
        "trial_nr": {
            "LongName": "Number of the trial",
            "Description": "Trials contain the presentation of "
            "sound (S1, S2, or S3) followed by symbol (A1, A2, B1, B2, C1, or C2).",
        },
        "sound": {
            "LongName": "Type of the sound condition",
            "Description": "",
            "Levels": {
                "S1": "",
                "S2": "",
                "S3": "",
            },
        },
        "sound_stim_id": {
            "LongName": "Stimulus id of the sound",
            "Description": "Indicates the location of the stimulus file "
            "in the code-psychtoolbox directory.",
        },
        "symbol": {
            "LongName": "Type of the symbol presented with the sound",
            "Description": "",
            "Levels": {
                "A1": "",
                "A2": "CS-",
                "B1": "",
                "B2": "CS+",
                "C1": "",
                "C2": "",
            },
        },
        "symbol_stim_id": {
            "LongName": "Stimulus id of the symbol image",
            "Description": "Indicates the location of the stimulus file "
            "in the code-psychtoolbox directory.",
        },
        "response_to_sound": {
            "LongName": "",
            "Description": "Response indicating shock expectancy (see instructions). "
            "First response after the sound onset until symbol image onset",
            "Levels": {
                "yes": "Pressing left arrow key",
                "no": "Pressing right arrow key",
                "other": "Pressing other key than left / right arrow key",
            },
        },
        "response_to_sound_time": {
            "LongName": "",
            "Description": "Response time (in seconds) computed as "
            "the difference between the onset of the sound and "
            "the onset of the first response recorded after the sound but before the symbol image onset. ",
        },
        "response_to_image": {
            "LongName": "",
            "Description": "Response indicating shock expectancy (see instructions). "
            "First response after the symbol image onset until scene image onset",
            "Levels": {
                "yes": "Pressing left arrow key",
                "no": "Pressing right arrow key",
                "other": "Pressing other key than left / right arrow key",
            },
        },
        "response_to_image_time": {
            "LongName": "",
            "Description": "Response time (in seconds) computed as "
            "the difference between the onset of the symbol image and "
            "the onset of the first response recorded after the symbol image but before the scene image onset. ",
        },
        "StimulusPresentation": {
            "OperatingSystem": "Windows 7 (Version 6.1)",
            "SoftwareName": "Psychtoolbox under Matlab 64-bit, version 9.3.0.713579 (R2017b)",
            "SoftwareVersion": "3.0.18",
            "SoftwareRRID": "SCR_002881",
            "Code": "bids::code-psychtoolbox",
        },
    }
    return jsonstring
