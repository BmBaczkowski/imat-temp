#!/usr/local/bin/python

import json
import numpy as np
import pandas as pd

from utils.utils import get_indx


def get_beh(csv_task):
    conds = csv_task.loc[
        ((csv_task["event_type"] == 2) | (csv_task["event_type"] == 4)), "event_type"
    ]
    task_beh = conds.copy(deep=True).to_frame()
    stims = csv_task.loc[conds.index, "stim_id"].copy()
    task_beh["stim_id"] = stims.copy()
    indx_us = get_indx(csv_task["event_type"], task_beh.index, task_beh.index, "US")
    task_beh["us"] = False
    task_beh.loc[indx_us.index, "us"] = True
    task_beh["us"].replace({True: "yes", False: "no"}, inplace=True)
    stop_indx = task_beh.index[1:].append(pd.Index([csv_task.index[-1]]))
    indx_scene = get_indx(
        csv_task["event_type"],
        task_beh.index,
        conds.index,
        "[scene|us]",
        stop_indx=stop_indx,
    )
    indx_response = get_indx(
        csv_task["event_type"],
        task_beh.index,
        conds.index,
        "response",
        stop_indx=indx_scene.values,
    )
    task_beh["response"] = "n/a"
    task_beh.loc[indx_response.index, "response"] = csv_task.loc[
        indx_response, "event_type"
    ].values

    # update the list based on responses that were recorded
    response_time = (
        csv_task.loc[indx_response, "onset"].values
        - csv_task.loc[indx_response.index, "onset"].values
    )
    response_time = response_time.astype(float).round(3)
    task_beh["response_time"] = "n/a"
    task_beh.loc[indx_response.index, "response_time"] = response_time

    task_beh.loc[task_beh["response"].str.contains("left"), "response"] = "yes"
    task_beh.loc[task_beh["response"].str.contains("right"), "response"] = "no"
    task_beh.loc[task_beh["response"].str.contains("other"), "response"] = "other"

    task_beh.rename(columns={"event_type": "trial_type"}, inplace=True)

    task_beh = task_beh[["trial_type", "us", "response", "response_time", "stim_id"]]

    task_beh.reset_index(drop=True, inplace=True)
    indx_block = 25
    block1 = task_beh.loc[:indx_block].copy(deep=True)
    block2 = task_beh[indx_block + 1 :].copy(deep=True)

    block1.insert(0, "trial_nr", list(range(1, len(block1) + 1)))
    block2.insert(0, "trial_nr", list(range(1, len(block2) + 1)))
    return (block1, block2)


def beh_json():
    jsonstring = {
        "TaskName": "Pavlovian delay threat conditioning task",
        "Instructions": "",
        "TaskDescription": "",
        "InstitutionName": "Universitaet Hamburg",
        "InstitutionAddress": "Hamburg, DE",
        "InstitutionalDepartmentName": "Department of Cognitive Psychology",
        "trial_nr": {
            "LongName": "Number of the trial",
            "Description": "",
        },
        "trial_type": {
            "LongName": "Type of the trial",
            "Description": "",
            "Levels": {
                "2": "Condition type A2 / CS-",
                "4": "Condition type B2 / CS+",
            },
        },
        "us": {
            "LongName": "Unconditioned stimulus applied",
            "Description": "",
            "Levels": {
                "yes": "Unconditioned stimulus applied",
                "no": "Unconditioned stimulus not applied",
            },
        },
        "response": {
            "LongName": "",
            "Description": "Response indicating shock expectancy. "
            "First response after the picture onset until US or stimulus offset (i.e., scene onset)",
            "Levels": {
                "yes": "Pressing left arrow key",
                "no": "Pressing right arrow key",
                "other": "Pressing other key than left / right arrow key",
            },
        },
        "response_time": {
            "LongName": "",
            "Description": "Response time (in seconds) computed as "
            "the difference between the onset of the picture and "
            "the onset of the first response recorded thereafter. ",
        },
        "stim_id": {
            "LongName": "Stimulus id",
            "Description": "Indicates the location of the stimulus file "
            "in the code-psychtoolbox directory.",
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
