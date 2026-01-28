#!/usr/local/bin/python

import json
import numpy as np


def replace_json_list(jsonstring, subjectkey, indx):
    jsonarray = json.load(jsonstring)
    jsonstring = json.dumps(jsonarray, ensure_ascii=False)
    for char in subjectkey.keys():
        jsonstring = jsonstring.replace(char[4:], subjectkey[char][4:])
    jsonarray = np.array(json.loads(jsonstring))
    jsonarray = jsonarray[indx].tolist()
    return jsonarray


def replace_df(df, subjectkey, sort_by=["participant_id"]):
    df.replace(subjectkey, inplace=True)
    df.sort_values(by=sort_by, inplace=True)
    df.fillna("n/a", inplace=True)
    return df
