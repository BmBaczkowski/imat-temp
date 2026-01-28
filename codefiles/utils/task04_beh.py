#!/usr/local/bin/python

import json
import numpy as np
import os
import pandas as pd


def find_trial_type(row):
    source = row["afc_source"]
    options = row[["afc_option_left", "afc_option_center", "afc_option_right"]].values
    options = list(options)
    if source == 1:
        if 1 in options:
            options.remove(1)
            trial_type = "11" + str(options[0]) + str(options[1])
        elif 2 in options:
            options.remove(2)
            trial_type = "12" + str(options[0]) + str(options[1])
    elif source == 2:
        if 3 in options:
            options.remove(3)
            trial_type = "23" + str(options[0]) + str(options[1])
        elif 4 in options:
            options.remove(4)
            trial_type = "24" + str(options[0]) + str(options[1])
    elif source == 3:
        if 5 in options:
            options.remove(5)
            trial_type = "35" + str(options[0]) + str(options[1])
        elif 6 in options:
            options.remove(6)
            trial_type = "36" + str(options[0]) + str(options[1])
    return trial_type


def find_trial_type_(row):
    source = row["afc_source"]
    options = row[["afc_option_left", "afc_option_center", "afc_option_right"]].values
    options = list(options)
    if 1 in options and 2 in options:
        trial_type = "non-base"
    elif 3 in options and 4 in options:
        trial_type = "non-base"
    elif 5 in options and 6 in options:
        trial_type = "non-base"
    else:
        trial_type = "base"
    return trial_type


def get_beh(filename):
    if not os.path.getsize(filename):
        csv_task = pd.DataFrame()
        return csv_task

    csv_task = pd.read_csv(filename, index_col=False)
    csv_task.rename(
        columns={
            "trial": "trial_nr",
            "sound": "afc_source",
            "conditionLeft": "afc_option_left",
            "conditionCenter": "afc_option_center",
            "conditionRight": "afc_option_right",
            "soundfile": "afc_source_stim_id",
            "pictureLeft": "afc_option_left_stim_id",
            "pictureCenter": "afc_option_center_stim_id",
            "pictureRight": "afc_option_right_stim_id",
            "decision": "response",
            "decisionRt": "response_time",
        },
        inplace=True,
    )

    csv_task["response"].replace([1, 2, 3], ["left", "center", "right"], inplace=True)
    csv_task["trial_scheme"] = csv_task.apply(lambda x: find_trial_type(x), axis=1)
    csv_task["trial_type"] = csv_task.apply(lambda x: find_trial_type_(x), axis=1)
    correct_response = csv_task["trial_scheme"].astype(str).str[1].astype(int)
    indx_left = csv_task.loc[csv_task["response"].str.fullmatch("left")].index
    indx_center = csv_task.loc[csv_task["response"].str.fullmatch("center")].index
    indx_right = csv_task.loc[csv_task["response"].str.fullmatch("right")].index
    choice_response = csv_task.loc[indx_left, "afc_option_left"]
    choice_response = pd.concat(
        [choice_response, csv_task.loc[indx_center, "afc_option_center"]]
    )
    choice_response = pd.concat(
        [choice_response, csv_task.loc[indx_right, "afc_option_right"]]
    )
    choice_response.sort_index(inplace=True)
    csv_task["response_type"] = choice_response.eq(correct_response)
    csv_task.replace({True: "correct", False: "incorrect"}, inplace=True)
    csv_task["response_time"] = csv_task["response_time"].round(3)
    csv_task["afc_source_stim_id"] = csv_task["afc_source_stim_id"].apply(
        lambda x: "sounds-02/%s" % x
    )
    csv_task["afc_option_left_stim_id"] = csv_task["afc_option_left_stim_id"].apply(
        lambda x: "symbols-01/%s" % x
    )
    csv_task["afc_option_center_stim_id"] = csv_task["afc_option_center_stim_id"].apply(
        lambda x: "symbols-01/%s" % x
    )
    csv_task["afc_option_right_stim_id"] = csv_task["afc_option_right_stim_id"].apply(
        lambda x: "symbols-01/%s" % x
    )
    csv_task = csv_task[
        [
            "trial_nr",
            "trial_type",
            "trial_scheme",
            "afc_source",
            "afc_source_stim_id",
            "afc_option_left",
            "afc_option_left_stim_id",
            "afc_option_center",
            "afc_option_center_stim_id",
            "afc_option_right",
            "afc_option_right_stim_id",
            "response",
            "response_time",
            "response_type",
        ]
    ]
    csv_task["afc_source"] = csv_task["afc_source"].replace({1: "S1", 2: "S2", 3: "S3"})
    csv_task["afc_option_left"] = csv_task["afc_option_left"].replace(
        {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2"}
    )
    csv_task["afc_option_center"] = csv_task["afc_option_center"].replace(
        {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2"}
    )
    csv_task["afc_option_right"] = csv_task["afc_option_right"].replace(
        {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2"}
    )

    csv_task.loc[csv_task["trial_type"] == "non-base", "response_type"] = "n/a"
    return csv_task


def beh_json():
    jsonstring = {
        "TaskName": "Three-alternative forced choice task (post)",
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
            "LongName": "Type of the 3-afc question",
            "Description": "",
            "Levels": {
                "base": "there are two lures (only one option is paired with the sound)",
                "non-base": "there is one lure (two options are paired with the sound)",
            },
        },
        "trial_scheme": {
            "LongName": "Type of the 3-afc question",
            "Description": "Trial type consists of 4 digitis. "
            "The first digit indicates the sound type. "
            "The other three digitis indicate options. "
            "If it is a base question, then "
            "the second digit indicates the correct answer (symbol), "
            "third and fourth digits indicate lures (symbols).",
            "Unit": "Four-digit number",
        },
        "afc_source": {
            "LongName": "Sound condition",
            "Description": "",
            "Levels": {
                "S1": "",
                "S2": "",
                "S3": "",
            },
        },
        "afc_source_stim_id": {
            "LongName": "Stimulus id of the sound",
            "Description": (
                "Indicates the location of the stimulus file "
                "in the code-psychtoolbox directory"
            ),
        },
        "afc_option_left": {
            "LongName": "Option in the 3-afc presented on the left",
            "Description": "",
            "Levels": {
                "A1": "",
                "A2": "",
                "B1": "",
                "B2": "",
                "C1": "",
                "C2": "",
            },
        },
        "afc_option_left_stim_id": {
            "LongName": "Stimulus id of the picture presented on the left as an option",
            "Description": (
                "Indicates the location of the stimulus file "
                "in the code-psychtoolbox directory"
            ),
        },
        "afc_option_center": {
            "LongName": "Option in the 3-afc presented in the center",
            "Description": "",
            "Levels": {
                "A1": "",
                "A2": "",
                "B1": "",
                "B2": "",
                "C1": "",
                "C2": "",
            },
        },
        "afc_option_center_stim_id": {
            "LongName": "Stimulus id of the picture presented in the center as an option",
            "Description": (
                "Indicates the location of the stimulus file "
                "in the code-psychtoolbox directory"
            ),
        },
        "afc_option_right": {
            "LongName": "Option in the 3-afc presented on the right",
            "Description": "",
            "Levels": {
                "A1": "",
                "A2": "",
                "B1": "",
                "B2": "",
                "C1": "",
                "C2": "",
            },
        },
        "afc_option_right_stim_id": {
            "LongName": "Stimulus id of the picture presented on the right as an option",
            "Description": (
                "Indicates the location of the stimulus file "
                "in the code-psychtoolbox directory"
            ),
        },
        "response": {
            "LongName": "",
            "Description": "Indicates which option was chosen",
            "Levels": {
                "left": "option on the left chosen",
                "center": "option in the center chosen",
                "right": "option on the right chosen",
                "other": (
                    "invalid button press "
                    "(none of the left, down, right arrow keys was pressed"
                ),
            },
        },
        "response_time": {
            "LongName": "",
            "Description": "Response time (in seconds)",
        },
        "response_type": {
            "LongName": "",
            "Description": "Indicates whether the response was correct",
            "Levels": {
                "correct": "Response matched the location of the correct option",
                "incorrect": "Response does not match the location of the correct option",
            },
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
