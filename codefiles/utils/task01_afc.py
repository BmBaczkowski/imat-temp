#!/usr/local/bin/python

import numpy as np
import pandas as pd
import json


def get_afc(csv_task_filename):
    csv_task_orig = pd.read_csv(csv_task_filename)

    imgs = csv_task_orig.copy(deep=True)
    imgs = imgs[imgs["condition"] < 8]
    imgs = imgs[["condition", "texture"]]
    imgs_dict = dict(imgs.values)
    imgs_dict = {x: "symbols-01/%s" % y for (x, y) in imgs_dict.items()}

    sounds = csv_task_orig.copy(deep=True)
    sounds = sounds[sounds["condition"] < 8]
    sounds = sounds[["sound", "soundfile"]]
    sounds_dict = dict(sounds.values)
    sounds_dict = {x: "sounds-02/%s" % y for (x, y) in sounds_dict.items()}

    afc_task = csv_task_orig.copy(deep=True)
    afc_task = afc_task[(afc_task["condition"] > 8) & (afc_task["condition"] < 999)]
    afc_task.rename(
        columns={
            "condition": "trial_type",
            "q_option_left": "afc_option_left",
            "q_option_center": "afc_option_center",
            "q_option_right": "afc_option_right",
            "q_response": "response",
            "q_response_time": "response_time",
        },
        inplace=True,
    )
    afc_task["response_time"] = afc_task["response_time"].round(3)
    afc_task.reset_index(drop=True, inplace=True)
    afc_task["afc_source"] = afc_task["sound"]
    afc_task["afc_source_stim_id"] = (
        afc_task["afc_source"].astype(int).apply(lambda x: sounds_dict[x])
    )
    afc_task["afc_option_left_stim_id"] = afc_task["afc_option_left"].apply(
        lambda x: imgs_dict[x]
    )
    afc_task["afc_option_center_stim_id"] = afc_task["afc_option_center"].apply(
        lambda x: imgs_dict[x]
    )
    afc_task["afc_option_right_stim_id"] = afc_task["afc_option_right"].apply(
        lambda x: imgs_dict[x]
    )

    # add trial nr of the afc and the associative task
    afc_task["trial_nr_seq"] = "n/a"
    afc_task["trial_nr"] = "n/a"

    sound_indx = csv_task_orig.loc[csv_task_orig["sound"].notna()].index
    csv_task_orig["trial_nr"] = "n/a"
    i = 0
    for count, val in enumerate(sound_indx):
        if count == (len(sound_indx) - 1):
            vec = csv_task_orig.loc[sound_indx[count] :].index
            csv_task_orig.loc[vec, "trial_nr"] = i + 1
            i = i + 1
            continue
        vec = csv_task_orig.loc[sound_indx[count] : sound_indx[count + 1]].index
        csv_task_orig.loc[vec, "trial_nr"] = i + 1
        i = i + 1
    # re-count within blocks
    indx_block = []
    indx_block.append(csv_task_orig.loc[csv_task_orig["block"] == 2].index[0])
    indx_block.append(csv_task_orig.loc[csv_task_orig["block"] == 3].index[0])
    csv_task_orig["block1"] = csv_task_orig.index < indx_block[0]
    csv_task_orig["block2"] = (csv_task_orig.index > indx_block[0]) & (
        csv_task_orig.index < indx_block[1]
    )
    csv_task_orig["block3"] = csv_task_orig.index > indx_block[1]

    indx_block2 = csv_task_orig["block2"].idxmax()
    indx_block3 = csv_task_orig["block3"].idxmax()

    csv_task_orig.loc[csv_task_orig["block2"], "trial_nr"] = (
        csv_task_orig.loc[csv_task_orig["block2"], "trial_nr"]
        - csv_task_orig.loc[indx_block2, "trial_nr"]
        + 1
    )

    csv_task_orig.loc[csv_task_orig["block3"], "trial_nr"] = (
        csv_task_orig.loc[csv_task_orig["block3"], "trial_nr"]
        - csv_task_orig.loc[indx_block3, "trial_nr"]
        + 1
    )

    csv_task_orig = csv_task_orig[
        (csv_task_orig["condition"] > 8) & (csv_task_orig["condition"] < 999)
    ]

    trial_nr = csv_task_orig["trial_nr"]
    afc_task["trial_nr_seq"] = trial_nr.values
    new_trial_indx = np.where(np.diff(trial_nr) < 0)[0]
    new_trial_nr = pd.concat(
        [
            pd.Series(list(range(1, new_trial_indx[0] + 2))),
            pd.Series(list(range(1, np.diff(new_trial_indx)[0] + 1))),
            pd.Series(list(range(1, afc_task.index[-1] - new_trial_indx[1] + 1))),
        ]
    )
    afc_task["trial_nr"] = new_trial_nr.values

    # responses
    correct_response = afc_task["trial_type"].astype(str).str[0].astype(int)
    afc_task.fillna("n/a", inplace=True)
    indx_left = afc_task.loc[afc_task["response"].str.fullmatch("left")].index
    indx_center = afc_task.loc[afc_task["response"].str.fullmatch("center")].index
    indx_right = afc_task.loc[afc_task["response"].str.fullmatch("right")].index
    choice_response = afc_task.loc[indx_left, "afc_option_left"]
    choice_response = pd.concat(
        [choice_response, afc_task.loc[indx_center, "afc_option_center"]]
    )
    choice_response = pd.concat(
        [choice_response, afc_task.loc[indx_right, "afc_option_right"]]
    )
    choice_response.sort_index(inplace=True)
    afc_task["response_type"] = choice_response.eq(correct_response)
    afc_task.loc[afc_task["response"] == "n/a", "response_type"] = "n/a"
    afc_task.replace({True: "correct", False: "incorrect"}, inplace=True)

    # re-code stim values
    afc_task["afc_source"] = afc_task["afc_source"].replace({1: "S1", 2: "S2", 3: "S3"})
    afc_task["afc_option_left"] = afc_task["afc_option_left"].replace(
        {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2"}
    )
    afc_task["afc_option_center"] = afc_task["afc_option_center"].replace(
        {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2"}
    )
    afc_task["afc_option_right"] = afc_task["afc_option_right"].replace(
        {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2"}
    )

    indx_block = []
    indx_block.append(afc_task.loc[afc_task["block"] == 2].index[0])
    indx_block.append(afc_task.loc[afc_task["block"] == 3].index[0])

    block1 = afc_task.loc[afc_task.index < indx_block[0]]
    block2 = afc_task.loc[
        (afc_task.index >= indx_block[0]) & (afc_task.index < indx_block[1])
    ]
    block3 = afc_task.loc[afc_task.index >= indx_block[1]]

    col_order = [
        "trial_nr",
        "trial_nr_seq",
        "trial_type",
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
    block1 = block1[col_order]
    block2 = block2[col_order]
    block3 = block3[col_order]
    return (block1, block2, block3)


def afc_json():
    jsonstring = {
        "TaskName": "Three-alternative forced choice task (during associative learning)",
        "Instructions": "",
        "TaskDescription": "",
        "InstitutionName": "Universitaet Hamburg",
        "InstitutionAddress": "Hamburg, DE",
        "InstitutionalDepartmentName": "Department of Cognitive Psychology",
        "trial_nr": {
            "LongName": "Number of the trial",
            "Description": "It is the ordinal number of afc trials only",
        },
        "trial_nr_seq": {
            "LongName": "Number of the trial based on the associative learning task. ",
            "Description": "Trial number is based on the associative learning task. "
            "Trial begins with a sound and is followed by a picture. "
            "Therefore, the number does not indicate the number of "
            "an afc trial.",
        },
        "trial_type": {
            "LongName": "Type of the 3-afc question",
            "Description": (
                "Trial type consists of 3 digitis. "
                "The first digit indicates the correct answer, "
                "second and third digitis indicate lures."
            ),
            "Unit": "Three-digit number",
        },
        "afc_source": {
            "LongName": "Type of the sound condition",
            "Description": ("Sound that is played"),
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
            "Description": (
                "Response time (in seconds) computed as "
                "the difference between afc onset and "
                "the first subsequent response"
            ),
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
