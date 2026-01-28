#!/usr/local/bin/python

from argparse import ArgumentParser
import logging
import os
import shutil


def main():
    parser = ArgumentParser(prog="bids_ptb", description="", epilog="")
    parser.add_argument("sourcedir", type=str, help="data source directory")
    parser.add_argument("destdir", type=str, help="data output directory")
    parser.add_argument("logdir", type=str, help="log directory")
    args = parser.parse_args()

    # prepare the log for debugging
    logfile = os.path.join(args.logdir, "ptb.log")
    logging.basicConfig(
        filename=logfile, encoding="utf-8", filemode="w", level=logging.DEBUG
    )

    logging.info("Copy psychtoolbox stimulus presentation code")

    # Copy all m-files
    files_list = [f for f in os.listdir(args.sourcedir) if f.endswith("m")]
    for f in files_list:
        shutil.copyfile(os.path.join(args.sourcedir, f), os.path.join(args.destdir, f))

    # Copy assets/
    shutil.copytree(
        os.path.join(args.sourcedir, "assets"),
        os.path.join(args.destdir, "assets"),
        dirs_exist_ok=True,
    )

    # Copy symbols-01/
    shutil.copytree(
        os.path.join(args.sourcedir, "symbols-01"),
        os.path.join(args.destdir, "symbols-01"),
        ignore=shutil.ignore_patterns(".*", "*svg"),
        dirs_exist_ok=True,
    )

    # Copy UPennNID/
    shutil.copytree(
        os.path.join(args.sourcedir, "UPennNID"),
        os.path.join(args.destdir, "UPennNID"),
        ignore=shutil.ignore_patterns(".*"),
        dirs_exist_ok=True,
    )

    # Make empty subfolder sounds-02
    if not os.path.exists(os.path.join(args.destdir, "sounds-02")):
        os.mkdir(os.path.join(args.destdir, "sounds-02"))

    # Make empty subfolder SMITE/
    if not os.path.exists(os.path.join(args.destdir, "SMITE")):
        os.mkdir(os.path.join(args.destdir, "SMITE"))

    # Replace path/to/store/data
    with open(os.path.join(args.destdir, "xExperiment.m"), "r") as mfile:
        mfile_lines = mfile.readlines()
    mfile_lines[24] = "datarepo                = 'path/to/store/data'\n"
    with open(
        os.path.join(args.destdir, "xExperiment.m"), "w", encoding="utf-8"
    ) as mfile:
        mfile.writelines(mfile_lines)

    logging.info("Finished")


main()
