#!/usr/local/bin/python

import numpy as np
import pandas as pd
import json
import os


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
    events = csv_task[["sound", "sound_timestamp", "soundfile"]].copy(deep=True)
    events.rename(
        columns={
            "sound": "event_type",
            "sound_timestamp": "timestamp",
            "soundfile": "stim_id",
        },
        inplace=True,
    )
    events["duration"] = 10.0
    events = events.assign(value=lambda events: events["event_type"])
    events["event_type"] = events["event_type"].replace({1: "S1", 2: "S2", 3: "S3"})
    events["value"] = events["value"].replace({1: 82, 2: 84, 3: 86})
    events2 = csv_task[["condition", "condition_timestamp", "texture"]].copy(deep=True)
    events2.rename(
        columns={
            "condition": "event_type",
            "condition_timestamp": "timestamp",
            "texture": "stim_id",
        },
        inplace=True,
    )
    events2["duration"] = 5.0
    events2 = events2.assign(value=lambda events2: events2["event_type"] * 10)
    events2["event_type"] = events2["event_type"].replace(
        {
            1: "A1",
            2: "A2",
            3: "B1",
            4: "B2",
            5: "C1",
            6: "C2",
        }
    )

    events = pd.concat([events, events2])
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
    events.reset_index(drop=True, inplace=True)
    events["stim_id"] = events["stim_id"].apply(
        lambda x: x
        if "n/a" in x
        else (
            "UPennNID/%s" % x
            if "jpg" in x
            else "symbols-01/%s" % x
            if "png" in x
            else "sounds-02/%s" % x
        )
    )

    return events


def cat_task_responses(task, responses):
    df = pd.concat([task, responses])
    df = df.sort_values(by=["timestamp"])
    df["onset"] = df["timestamp"] - df["timestamp"].min()
    df["onset"] = df["onset"].round(3)
    df.reset_index(drop=True, inplace=True)
    df = df[["onset", "duration", "event_type", "value", "stim_id"]]
    return df


def events_json():
    jsonstring = {
        "onset": {
            "Description": "Onset (in seconds) of the event based on "
            "Psychtoolbox VBLTimestamp when a stimulus is presented "
            "and Psychtoolbox GetSecs when a response is recorded. "
            "Therefore, minimal delay when the stimulus is actually "
            "presented is possible. For such events as "
            "'scene' onset were not recorded and therefore "
            "in this file they are approximated by adding their "
            "intended duration to the onset of the proceeding stimulus event.",
        },
        "duration": {
            "Description": "Duration (in seconds) of the event as planned "
            "(the actual duration might be slighlty longer)",
        },
        "event_type": {
            "LongName": "Type of the event",
            "Description": "Type of the event including stimulus presentation "
            "and button presses (responses)",
            "Levels": {
                "S1": "Sound condition 1",
                "S2": "Sound condition 2",
                "S3": "Sound condition 3",
                "A1": "Image condition A1 associated with S1",
                "A2": "Image condition A2 associated with S1",
                "B1": "Image condition B1 associated with S2",
                "B2": "Image condition B2 associated with S2",
                "C1": "Image condition C1 associated with S3",
                "C2": "Image condition C2 associated with S3",
                "scene": "Presentation of a scene image in between the presentation of the symbol image",
                "response_leftarrow": "Response indicating shock expectancy.",
                "response_rightarrow": "Response indicating no shock expectancy.",
                "response_other": "Pressing a different key on the keyboard "
                "than left / right arrows.",
            },
        },
        "value": {
            "LongName": "Marker value associated with the event",
            "Description": "Marker recorded in biopac and eye-tracking data",
            "Levels": {
                "1": "US onset",
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
            },
        },
        "stim_id": {
            "LongName": "Stimulus id",
            "Description": "Indicates the location of the stimulus file "
            "in the code-psychtoolbox directory",
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
