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

from utils.utils_recode import replace_json_list, replace_df

parser = ArgumentParser(prog="recode_ids", description="", epilog="")
parser.add_argument("key", type=str, help="Json file with a key")
parser.add_argument("n", type=int, help="total number of participants")
parser.add_argument("bidsdir", type=str, help="data directory with bids files")
parser.add_argument("logdir", type=str, help="log directory")
args = parser.parse_args()

# logfile
logfilename = os.path.join(args.logdir, "recodeids.log")
mylogs = logging.getLogger()
mylogs.setLevel(logging.NOTSET)

logfile = logging.FileHandler(logfilename, mode="w")
logfile.setLevel(logging.CRITICAL)
stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
stream.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))

mylogs.addHandler(logfile)
mylogs.addHandler(stream)


jsonfile = open(args.key)
subjectkey = json.load(jsonfile)
subjectkey = {k: subjectkey[k] for k in list(subjectkey)[: args.n]}
indx = [int(val[-3:]) for val in subjectkey.values()]
indx = np.argsort(indx)

# assessment
free_text_filename = os.path.join(args.bidsdir, "assessment", "free_text_data.json")
free_text = open(free_text_filename)
free_text = replace_json_list(free_text, subjectkey, indx)
with open(free_text_filename, "w", encoding="utf-8") as f:
    json.dump(free_text, f, ensure_ascii=False, indent=4)

# logbook
logbook_filename = os.path.join(args.bidsdir, "assessment", "logbook.json")
logbook = open(logbook_filename)
logbook = replace_json_list(logbook, subjectkey, indx)
with open(logbook_filename, "w", encoding="utf-8") as f:
    json.dump(logbook, f, ensure_ascii=False, indent=4)

# participants
pp_filename = os.path.join(args.bidsdir, "participants.tsv")
df = pd.read_csv(pp_filename, sep="\t")
df = replace_df(df, subjectkey)
df.to_csv(pp_filename, sep="\t", index=False)

# assessment/ratings_tasks_with_pairs
seq_filename = os.path.join(args.bidsdir, "assessment", "ratings_tasks_with_pairs.tsv")
df = pd.read_csv(seq_filename, sep="\t")
df = replace_df(df, subjectkey, sort_by=["participant_id", "task_id"])
df.to_csv(seq_filename, sep="\t", index=False)

# assessment/ratings_tasks_with_shocks
shock_filename = os.path.join(
    args.bidsdir, "assessment", "ratings_tasks_with_shocks.tsv"
)
df = pd.read_csv(shock_filename, sep="\t")
df = replace_df(df, subjectkey, sort_by=["participant_id"])
df.to_csv(shock_filename, sep="\t", index=False)

# phenotype/ius
ius_filename = os.path.join(args.bidsdir, "phenotype", "ius.tsv")
df = pd.read_csv(ius_filename, sep="\t")
df = replace_df(df, subjectkey, sort_by=["participant_id", "ui_item"])
df.to_csv(ius_filename, sep="\t", index=False)

# phenotype/stai
stai_filename = os.path.join(args.bidsdir, "phenotype", "stai_trait.tsv")
df = pd.read_csv(stai_filename, sep="\t")
df = replace_df(df, subjectkey, sort_by=["participant_id", "stai_trait_item"])
df.to_csv(stai_filename, sep="\t", index=False)

# beh dirs
old_list_of_dirs = glob.glob(os.path.join(args.bidsdir, "sub-r*"))
for dirname in old_list_of_dirs:
    shutil.rmtree(dirname)

list_of_files = glob.glob(os.path.join(args.bidsdir, "sub*", "beh", "*"))
list_of_files.sort()
new_list_of_files = json.dumps(list_of_files)
for orig_sub in subjectkey.keys():
    new_list_of_files = new_list_of_files.replace(orig_sub, subjectkey[orig_sub])
new_list_of_files = json.loads(new_list_of_files)
indx = np.argsort(new_list_of_files)
for count, i in enumerate(indx):
    fname1 = list_of_files[i]
    fname2 = new_list_of_files[i]
    os.makedirs(os.path.dirname(fname2), exist_ok=True)
    mylogs.debug("%s -> %s" % (fname1, fname2))
    shutil.copyfile(fname1, fname2)

list_of_dirs = glob.glob(os.path.join(args.bidsdir, "sub-1*"))
for dirname in list_of_dirs:
    shutil.rmtree(dirname)

# update timestamps to dependencies

os.utime(os.path.join(args.bidsdir, "logfiles", "participants.log"))
os.utime(os.path.join(args.bidsdir, "logfiles", "ius.log"))
os.utime(os.path.join(args.bidsdir, "logfiles", "stai_trait.log"))
os.utime(os.path.join(args.bidsdir, "logfiles", "free_text_data.log"))
os.utime(os.path.join(args.bidsdir, "logfiles", "ratings_tasks_with_pairs.log"))
os.utime(os.path.join(args.bidsdir, "logfiles", "ratings_tasks_with_shocks.log"))
os.utime(os.path.join(args.bidsdir, "logfiles", "logbook.log"))
os.utime(os.path.join(args.bidsdir, "logfiles", "beh_dir_maker.log"))
os.utime(os.path.join(args.bidsdir, "logfiles", "beh_task-04.log"))
os.utime(os.path.join(args.bidsdir, "logfiles", "beh_task-03.log"))
os.utime(os.path.join(args.bidsdir, "logfiles", "beh_task-02.log"))
os.utime(os.path.join(args.bidsdir, "logfiles", "beh_task-01.log"))
os.utime(os.path.join(args.bidsdir, "logfiles", "smi.log"))
os.utime(os.path.join(args.bidsdir, "logfiles", "biopac.log"))
mylogs.info("Remove sub-1*/ dirs")

# log info
mylogs.critical("Recode subject ids")
