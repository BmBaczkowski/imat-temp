#!/usr/local/bin/python

from argparse import ArgumentParser
import logging
import os
import shutil
import sys

parser = ArgumentParser(prog="make_beh_subdirs", description="", epilog="")
parser.add_argument("sourcedir", type=str, help="PTB data directory")
parser.add_argument("destdir", type=str, help="BIDS data output directory")
parser.add_argument("logdir", type=str, help="logfiles directory")
args = parser.parse_args()

# init logger
logfilename = os.path.join(args.logdir, "beh_dir_maker.log")
mylogs = logging.getLogger()
mylogs.setLevel(logging.DEBUG)

logfile = logging.FileHandler(logfilename, mode="w")
logfile.setLevel(logging.INFO)
stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)

mylogs.addHandler(logfile)
mylogs.addHandler(stream)


mylogs.info("Create subject directories")
for _, dirs, _ in os.walk(args.sourcedir):
    dirs.sort()
    dirs[:] = [d for d in dirs if not d[0] == "."]
    for fname in dirs:
        sub_name = "sub-%s" % fname
        sub_dir = os.path.join(args.destdir, sub_name, "beh")
        if os.path.isdir(sub_dir):
            shutil.rmtree(sub_dir)

        logging.debug("%s:Creating subject directory" % sub_name)
        os.makedirs(sub_dir)

mylogs.info("Subject directories created")
