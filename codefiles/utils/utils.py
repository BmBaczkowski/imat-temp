#!/usr/local/bin/python

import os
import pandas as pd


def get_sub_info(sourcedir, destdir):
    sub_info = []
    for _, dirs, _ in os.walk(sourcedir):
        dirs.sort()
        dirs[:] = [d for d in dirs if not d[0] == "."]
        for fname in dirs:
            sub_src_dir = os.path.join(sourcedir, fname)
            sub_name = "sub-%s" % fname
            sub_dir = os.path.join(destdir, sub_name, "beh")
            sub_info.append((sub_src_dir, sub_name, sub_dir))
    return sub_info


def get_indx(df_column, indx, start_indx, keystring, stop_indx=None):
    # find the first index matching condition in the df
    # indx -- original index
    # start_indx -- index from which to start the search
    # stop_indx -- index until which to search

    if stop_indx is None:
        stop_indx = start_indx[1:].append(pd.Index([df_column.index[-1]]))

    y = pd.Series([], index=[], dtype="object")
    for count, val in enumerate(start_indx):
        vec = df_column.loc[start_indx[count] : stop_indx[count]].str.contains(
            keystring
        )
        vec.fillna(False, inplace=True)
        vec = vec[vec]
        if not vec.empty:
            y = pd.concat([y, pd.Series([vec.index[0]], index=[indx[count]])])
    return y
