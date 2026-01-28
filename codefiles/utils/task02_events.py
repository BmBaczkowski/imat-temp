#!/usr/local/bin/python

import json
import numpy as np
import os
import pandas as pd


def clean_csv_responses(filename):
    if not os.path.getsize(filename) > 0:
        csv_responses = pd.DataFrame(
            columns=["event_type", "timestamp", "stim_id", "duration", "value"]
        )
        return csv_responses
    else:
        csv_responses = pd.read_csv(filename)
        csv_responses = csv_responses[csv_responses.pressed == 1]
        csv_responses = csv_responses[["keyName", "timeStamp"]]
        csv_responses.rename(
            columns={"keyName": "event_type", "timeStamp": "timestamp"}, inplace=True
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
                    "response_leftarrow",
                    "response_rightarrow",
                ]
            ),
            "event_type",
        ] = "response_other"
        csv_responses["stim_id"] = "n/a"
        csv_responses["duration"] = "n/a"
        csv_responses["value"] = "n/a"
        csv_responses.reset_index(drop=True, inplace=True)
        return csv_responses


def clean_csv_task(filename):
    csv_task = pd.read_csv(filename, index_col=False)
    events = csv_task[["condition", "condition_timestamp", "texture"]].copy(deep=True)
    events.rename(
        columns={
            "condition": "event_type",
            "condition_timestamp": "timestamp",
            "texture": "stim_id",
        },
        inplace=True,
    )
    events["duration"] = 5.0
    indx_shock = csv_task.loc[csv_task["shock"] == True].index
    events = events.assign(value=lambda events: events["event_type"] * 10)
    events.loc[indx_shock, "value"] = 100
    new_row = pd.DataFrame("n/a", index=[25], columns=events.columns)
    new_row["timestamp"] = events.at[25, "timestamp"] + 5 + 15 + 0.05
    new_row["event_type"] = "pause"
    events = pd.concat([events, new_row]).sort_index()
    shocks = csv_task[["condition_timestamp", "texture", "shock"]].copy(deep=True)
    shocks.rename(
        columns={
            "shock": "event_type",
            "condition_timestamp": "timestamp",
            "texture": "stim_id",
        },
        inplace=True,
    )
    shocks.replace({True: "US", False: np.nan}, inplace=True)
    shocks.dropna(inplace=True)
    shocks["stim_id"] = "n/a"
    shocks["timestamp"] = shocks["timestamp"].add(4.8)
    shocks["duration"] = 0.2
    shocks["value"] = 1
    events = pd.concat([events, shocks])
    events = events.sort_values(by=["timestamp"])
    imgs1 = csv_task[["condition_timestamp", "image1"]].copy(deep=True)
    imgs1["event_type"] = "scene"
    imgs1.rename(
        columns={"condition_timestamp": "timestamp", "image1": "stim_id"}, inplace=True
    )
    imgs1["duration"] = 5.0
    imgs1["value"] = 94
    imgs1["timestamp"] = imgs1["timestamp"].add(5)
    events = pd.concat([events, imgs1])
    events = events.sort_values(by=["timestamp"])
    imgs2 = csv_task[["condition_timestamp", "image2"]].copy(deep=True)
    imgs2["event_type"] = "scene"
    imgs2.rename(
        columns={"condition_timestamp": "timestamp", "image2": "stim_id"}, inplace=True
    )
    imgs2["duration"] = 5.0
    imgs2["value"] = 94
    imgs2["timestamp"] = imgs2["timestamp"].add(5 + 5)
    events = pd.concat([events, imgs2])
    events = events.sort_values(by=["timestamp"])
    imgs3 = csv_task[["condition_timestamp", "image3"]].copy(deep=True)
    imgs3["event_type"] = "scene"
    imgs3.rename(
        columns={"condition_timestamp": "timestamp", "image3": "stim_id"}, inplace=True
    )
    imgs3["duration"] = 5.0
    imgs3["value"] = 94
    imgs3["timestamp"] = imgs3["timestamp"].add(5 + 5 + 5)
    imgs3.dropna(inplace=True)
    events = pd.concat([events, imgs3])
    events = events.sort_values(by=["timestamp"])

    events["stim_id"] = events["stim_id"].apply(
        lambda x: x
        if "n/a" in x
        else ("UPennNID/%s" % x if "jpg" in x else "symbols-01/%s" % x)
    )
    return events


def cat_task_responses(task, responses):
    df = pd.concat([task, responses])
    df = df.sort_values(by=["timestamp"])
    df["onset"] = df["timestamp"] - df["timestamp"].min()
    df["onset"] = df["onset"].round(3)
    df.reset_index(drop=True, inplace=True)
    indx_pause = df.loc[df["event_type"] == "pause"].index
    # add bogus onset of the pause (it will be removed later anyway)
    df.loc[indx_pause, "onset"] = df.loc[indx_pause - 1, "onset"].values.round(0) + 0.1
    df = df[["onset", "duration", "event_type", "value", "stim_id"]]
    return df


def correct_onset(df):
    indx_state = df.loc[df["event_type"].astype(str).str.contains("2|4")].index
    df.onset = df.onset - df.at[indx_state[0], "onset"]
    df.onset = df.onset.astype(float).round(3)
    return df


def split_df(df):
    indx_block = df.loc[df["event_type"] == "pause"].index
    block1 = df.iloc[: indx_block[0], :].copy(deep=True)
    block2 = df.iloc[indx_block[0] + 1 :, :].copy(deep=True)

    block1 = correct_onset(block1)
    block2 = correct_onset(block2)

    return (block1, block2)


def events_json():
    jsonstring = {
        "onset": {
            "Description": "Onset (in seconds) of the event based on "
            "Psychtoolbox VBLTimestamp when a stimulus is presented "
            "and Psychtoolbox GetSecs when a response is recorded. "
            "Therefore, minimal delay when the stimulus is actually "
            "presented is possible. For such events as 'US' "
            "and 'scene' onsets were not recorded and therefore "
            "they are approximated by adding their intended duration "
            "to the onset of the proceeding stimulus event such as "
            "'2' or '4', respectively.",
        },
        "duration": {
            "Description": "Duration (in seconds) of the event as planned "
            "(the actual duration might be slighlty longer)",
        },
        "event_type": {
            "LongName": "Type of the event",
            "Description": "Type of the event including stimulus presentation and button presses (responses)",
            "Levels": {
                "2": "Condition type A2 / CS- ",
                "4": "Condition type B2 / CS+ ",
                "US": "shock",
                "scene": "Presentation of a scene image in between the presentation of the symbol image",
                "response_leftarrow": "Response indicating shock expectancy.",
                "response_rightarrow": "Response indicating no shock expectancy.",
                "response_other": "Pressing a different key on the keyboard "
                "than left / right arrows.",
            },
        },
        "value": {
            "LongName": "Marker value associated with the event",
            "Description": "Marker recorded in the biopac and eye-tracking data",
            "Levels": {
                "1": "US onset",
                "20": "Condition type A2 / CS- onset",
                "40": "Condition type B2 / CS+ onset",
                "94": "Scene image onset",
                "100": "Condition type B2 / CS+ onset followed by the shock",
            },
        },
        "stim_id": {
            "LongName": "Stimulus id",
            "Description": "Indicates the location of the stimulus file "
            "in the code-psychtoolbox directory and "
            "the assignment of the symbol image to "
            "the condition type",
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
