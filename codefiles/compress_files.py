#!/usr/local/bin/python

from argparse import ArgumentParser
import json
import logging
import numpy as np
import os
import pandas as pd
import glob
import shutil
import pathlib
import multiprocessing


parser = ArgumentParser(prog="compress_files", description="", epilog="")
parser.add_argument("bidsdir", type=str, help="data directory with bids files")
parser.add_argument("logdir", type=str, help="log directory")
args = parser.parse_args()

# logfile
logfilename = os.path.join(args.logdir, "compress.log")
mylogs = logging.getLogger()
mylogs.setLevel(logging.NOTSET)

logfile = logging.FileHandler(logfilename, mode="w")
logfile.setLevel(logging.CRITICAL)
stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
stream.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))

mylogs.addHandler(logfile)
mylogs.addHandler(stream)


def compress(f):
    df = pd.read_csv(f, delimiter="\t", header=None)
    fout = f + ".gz"
    mylogs.debug(f)
    mylogs.debug(fout)
    df.to_csv(fout, sep="\t", header=False, index=False)
    os.remove(f)


list_of_files = glob.glob(os.path.join(args.bidsdir, "sub*", "beh", "*physio.tsv"))
list_of_files.sort()

with multiprocessing.Pool() as pool:
    pool.map(compress, list_of_files)

# log info
mylogs.critical("Compress biopac and smi files")
