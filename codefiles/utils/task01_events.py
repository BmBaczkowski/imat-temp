#!/usr/local/bin/python

import json
import numpy as np
import pandas as pd


def clean_csv_responses(filename, block):
    csv_responses = pd.read_csv(filename)
    csv_responses = csv_responses[csv_responses.pressed == 1]
    csv_responses = csv_responses[["keyName", "timeStamp"]]
    csv_responses.rename(
        columns={
            "keyName": "event_type",
            "timeStamp": "timestamp",
        },
        inplace=True,
    )
    csv_responses.replace(
        ["DownArrow", "UpArrow", "LeftArrow", "RightArrow"],
        [
            "response_downarrow",
            "response_uparrow",
            "response_leftarrow",
            "response_rightarrow",
        ],
        inplace=True,
    )
    csv_responses.loc[
        ~csv_responses.event_type.isin(
            [
                "response_downarrow",
                "response_leftarrow",
                "response_rightarrow",
            ]
        ),
        "event_type",
    ] = "response_other"
    csv_responses["stim_id"] = "n/a"
    csv_responses.reset_index(drop=True, inplace=True)
    csv_responses["block"] = block
    return csv_responses


def clean_csv_task(filename):
    csv_task = pd.read_csv(filename)
    csv_task_questions = csv_task.copy(deep=True)
    csv_task_questions = csv_task_questions[
        (csv_task_questions["condition"] > 8) & (csv_task_questions["condition"] < 999)
    ]
    csv_task_questions["event_type"] = "afc"
    csv_task_questions["stim_id"] = "n/a"
    csv_task_questions = csv_task_questions[
        ["block", "condition_timestamp", "event_type", "stim_id"]
    ]
    csv_task_questions.rename(
        columns={"condition_timestamp": "timestamp"}, inplace=True
    )
    csv_task_questions.reset_index(drop=True, inplace=True)
    # events (images)
    csv_task_imgs = csv_task.copy(deep=True)
    csv_task_imgs = csv_task_imgs[csv_task_imgs["condition"] < 9]
    csv_task_imgs = csv_task_imgs[
        ["block", "condition", "condition_timestamp", "texture"]
    ]
    csv_task_imgs["condition"] = csv_task_imgs["condition"].replace(
        {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2", 8: "fixation_cross"}
    )
    csv_task_imgs.rename(
        columns={
            "condition": "event_type",
            "condition_timestamp": "timestamp",
            "texture": "stim_id",
        },
        inplace=True,
    )
    csv_task_imgs["stim_id"] = csv_task_imgs["stim_id"].apply(
        lambda x: x if pd.isna(x) else "symbols-01/%s" % x
    )
    csv_task_imgs.fillna("n/a", inplace=True)
    csv_task_imgs.reset_index(drop=True, inplace=True)
    # events (sounds)
    csv_task_sounds = csv_task.copy(deep=True)
    csv_task_sounds = csv_task_sounds[csv_task_sounds["sound"].notna()]
    csv_task_sounds = csv_task_sounds[
        ["block", "sound", "sound_timestamp", "soundfile"]
    ]
    csv_task_sounds["sound"] = csv_task_sounds["sound"].replace(
        {1: "S1", 2: "S2", 3: "S3"}
    )
    csv_task_sounds.rename(
        columns={
            "sound": "event_type",
            "sound_timestamp": "timestamp",
            "soundfile": "stim_id",
        },
        inplace=True,
    )

    csv_task_sounds["stim_id"] = csv_task_sounds["stim_id"].apply(
        lambda x: x if pd.isna(x) else "sounds-02/%s" % x
    )

    # add name of the sound file where missing (afc trials)
    matchcons = csv_task_sounds.drop_duplicates(subset=["event_type", "stim_id"])
    matchcons = matchcons[matchcons["stim_id"].notna()]
    csv_task_sounds["stim_id"] = csv_task_sounds["event_type"].apply(
        lambda x: x
        if not "S" in x
        else matchcons.loc[matchcons["event_type"] == x, "stim_id"].values[0]
    )

    csv_task_sounds.fillna("n/a", inplace=True)
    csv_task_sounds.reset_index(drop=True, inplace=True)
    df = pd.concat([csv_task_questions, csv_task_imgs, csv_task_sounds])
    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def cat_task_responses(task, responses):
    df = pd.concat([task, responses])
    df = df.sort_values(by="timestamp")
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df["event_type"] = df["event_type"].astype(str)
    df["onset"] = df.timestamp  # corrected block-wise in the next step
    df["duration"] = "n/a"
    df.loc[df["event_type"].str.contains("S"), ["duration"]] = 10.0
    df.loc[df["event_type"].str.contains("[A-C]"), ["duration"]] = 5.0
    task = task.sort_values(by="timestamp")
    task.reset_index(drop=True, inplace=True)
    indx_afc = task.loc[task["event_type"] == "afc"].index
    afc_onset = task.loc[indx_afc, "timestamp"]
    state_8_onset = task.loc[indx_afc + 1, "timestamp"]
    afc_duration = state_8_onset.values - afc_onset.values
    afc_duration = afc_duration.round(3)
    indx_state8 = task.loc[task["event_type"] == "fixation_cross"].index
    indx_state8 = indx_state8[:-1]
    state8_duration = (
        task.loc[indx_state8 + 1, "timestamp"].values
        - task.loc[indx_state8, "timestamp"].values
    )
    state8_duration = state8_duration.round(1)
    # find new indicies
    indx_afc = df.loc[df["event_type"].str.fullmatch("afc")].index
    indx_state8 = df.loc[df["event_type"].str.fullmatch("fixation_cross")].index
    indx_state8 = indx_state8[:-1]
    df.loc[indx_afc, "duration"] = afc_duration
    df.loc[indx_state8, "duration"] = state8_duration
    df.drop(columns=["timestamp"], inplace=True)
    # correct duration of fixation cross before the next block
    # otherwise, it likely reflects the duration of the pause
    nindx = np.where(df.loc[indx_state8, "duration"] > 5)[0]
    df.loc[indx_state8[nindx], "duration"] = "n/a"
    df["value"] = "n/a"
    df.loc[df["event_type"].str.fullmatch("S1"), "value"] = "82"
    df.loc[df["event_type"].str.fullmatch("S2"), "value"] = "84"
    df.loc[df["event_type"].str.fullmatch("S3"), "value"] = "86"
    df.loc[df["event_type"].str.fullmatch("A1"), "value"] = "10"
    df.loc[df["event_type"].str.fullmatch("A2"), "value"] = "20"
    df.loc[df["event_type"].str.fullmatch("B1"), "value"] = "30"
    df.loc[df["event_type"].str.fullmatch("B2"), "value"] = "40"
    df.loc[df["event_type"].str.fullmatch("C1"), "value"] = "50"
    df.loc[df["event_type"].str.fullmatch("C2"), "value"] = "60"
    df.loc[df["event_type"].str.fullmatch("fixation_cross"), "value"] = "80"
    df.loc[df["event_type"].str.fullmatch("afc"), "value"] = "92"
    df = df[["block", "onset", "duration", "event_type", "value", "stim_id"]]
    return df


def correct_onset(df):
    indx_state = df.loc[df["event_type"].str.contains("[1-7]")].index
    df.onset = df.onset - df.at[indx_state[0], "onset"]
    df.onset = df.onset.round(3)
    return df


def split_df(df):
    indx_block = []
    indx_block.append(df.loc[df["block"] == 2].index[0])
    indx_block.append(df.loc[df["block"] == 3].index[0])
    df.drop(columns=["block"], inplace=True)
    block1 = df.iloc[: indx_block[0], :].copy(deep=True)
    block2 = df.iloc[indx_block[0] + 1 : indx_block[1], :].copy(deep=True)
    block3 = df.iloc[indx_block[1] + 1 :, :].copy(deep=True)

    block1 = correct_onset(block1)
    block2 = correct_onset(block2)
    block3 = correct_onset(block3)

    return (block1, block2, block3)


def events_json():
    jsonstring = {
        "onset": {
            "Description": (
                "Onset (in seconds) of the event based on "
                "Psychtoolbox VBLTimestamp when a stimulus is "
                "presented and Psychtoolbox GetSecs when a "
                "response is recorded. Therefore, minimal delay "
                "when the stimulus is actually presented "
                "is possible."
            ),
        },
        "duration": {
            "Description": (
                "Duration (in seconds) of the event as planned "
                "(the actual duration might be slighlty longer). "
                "Duration of the afc includes the presentation of "
                "the options (until button press or max 5 s) and "
                "the visual feedback to the button press (which lasts 500 ms) "
                "and is then followed by a next event, i.e., fixation cross"
            ),
        },
        "event_type": {
            "LongName": "Type of the event",
            "Description": (
                "Type of the event including stimulus presentation, "
                "3-alternative forced choice, or button press"
            ),
            "Levels": {
                "S1": "Sound condition 1",
                "S2": "Sound condition 2",
                "S3": "Sound condition 3",
                "A1": "Image condition 1 associated with S1",
                "A2": "Image condition 2 associated with S1",
                "B1": "Image condition 1 associated with S2",
                "B2": "Image condition 2 associated with S2",
                "C1": "Image condition 1 associated with S3",
                "C2": "Image condition 2 associated with S3",
                "fixation_cross": "",
                "response_downarrow": (
                    "Response indicating the center option in the alternative forced choice"
                ),
                "response_leftarrow": (
                    "Response indicating the left option in the alternative forced choice"
                ),
                "response_rightarrow": (
                    "Response indicating the right option in the alternative forced choice"
                ),
                "response_other": (
                    "Pressing a different key on the keyboard than an arrow key"
                ),
                "afc": "3 alternative forced choice",
            },
        },
        "value": {
            "LongName": "Marker value associated with the event",
            "Description": ("Marker recorded in the biopac and eye-tracking data"),
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
            },
        },
        "stim_id": {
            "LongName": "Stimulus id",
            "Description": (
                "Indicates the location of the stimulus file "
                "in the code-psychtoolbox directory and "
                "the assignment of the sound and the symbol image to "
                "the condition type"
            ),
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
