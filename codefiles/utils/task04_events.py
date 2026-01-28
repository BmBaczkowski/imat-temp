#!/usr/local/bin/python

import numpy as np
import pandas as pd
import json
import os


def clean_csv_task(filename):
    csv_task = pd.read_csv(filename, index_col=False)
    events = csv_task[["sound", "trialOnset", "decisionRt"]].copy(deep=True)
    events.rename(
        columns={
            "sound": "event_type",
            "trialOnset": "timestamp",
        },
        inplace=True,
    )
    events["duration"] = events["decisionRt"] + 0.25
    events = events.assign(value=lambda events: events["event_type"])
    events["event_type"] = events["event_type"].replace({1: "S1", 2: "S2", 3: "S3"})
    events["value"] = events["value"].replace({1: 82, 2: 84, 3: 86})
    events.drop(columns=["decisionRt"], inplace=True)

    events2 = csv_task[["itiOnset"]].copy(deep=True)
    events2.rename(
        columns={
            "itiOnset": "timestamp",
        },
        inplace=True,
    )
    events2["duration"] = np.nan
    events2["event_type"] = "iti"
    events2["value"] = "n/a"

    responses = csv_task[["trialOnset", "decisionRt"]].copy(deep=True)
    responses["timestamp"] = responses["trialOnset"] + responses["decisionRt"]
    responses["duration"] = np.nan
    responses["event_type"] = "response"
    responses["value"] = "n/a"
    responses.drop(columns=["trialOnset", "decisionRt"], inplace=True)

    events = pd.concat([events, events2, responses])
    events = events.sort_values(by=["timestamp"])
    events.reset_index(drop=True, inplace=True)
    sound_indx = events[events["event_type"].str.contains("S")].index
    iti_indx = events[events["event_type"] == "iti"].index
    iti_duration = (
        events.loc[sound_indx[1:], "timestamp"].values
        - events.loc[iti_indx[:-1], "timestamp"].values
    )
    iti_duration = np.append(iti_duration, np.nan)
    events.loc[iti_indx, "duration"] = iti_duration
    events["onset"] = events["timestamp"] - events["timestamp"].values[0]
    events = events[["onset", "duration", "event_type", "value"]]
    events["onset"] = events["onset"].round(3)
    events["duration"] = events["duration"].round(3)
    events.fillna("n/a", inplace=True)

    return events


def events_json():
    jsonstring = {
        "onset": {
            "Description": "Onset (in seconds) of the event based on "
            "Psychtoolbox VBLTimestamp when a stimulus is presented "
            "and Psychtoolbox GetSecs when a response is recorded. "
            "Therefore, minimal delay when the stimulus is actually "
            "presented is possible."
        },
        "duration": {
            "Description": "Duration (in seconds) of the event as planned "
            "(the actual duration might be slighlty longer)",
        },
        "event_type": {
            "LongName": "Type of the event",
            "Description": "",
            "Levels": {
                "S1": "alternative forced choice started with sound condition 1",
                "S2": "alternative forced choice started with sound condition 2",
                "S3": "alternative forced choice started with sound condition 3",
                "response": "choice response",
                "iti": "inter trial interval onset",
            },
        },
        "value": {
            "LongName": "Marker value associated with the event",
            "Description": "Marker recorded in biopac and eye-tracking data",
            "Levels": {
                "82": "Onset of sound S1",
                "84": "Onset of sound S2",
                "86": "Onset of sound S3",
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
