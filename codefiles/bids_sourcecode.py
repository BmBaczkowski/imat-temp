#!/usr/local/bin/python

from argparse import ArgumentParser
import logging
import os
import shutil


def main():
    parser = ArgumentParser(prog="bids_sourcecode", description="", epilog="")
    parser.add_argument("sourcedir", type=str, help="data source directory")
    parser.add_argument("destdir", type=str, help="data output directory")
    parser.add_argument("logdir", type=str, help="log directory")
    parser.add_argument("acronym", type=str, help="study acronym")
    args = parser.parse_args()

    # prepare the log for debugging
    logfile = os.path.join(args.logdir, "sourcecode.log")
    logging.basicConfig(
        filename=logfile, encoding="utf-8", filemode="w", level=logging.DEBUG
    )

    logging.info("Copy the code to get from source to raw data")

    # Copy the whole dir
    shutil.copytree(
        args.sourcedir,
        os.path.join(args.destdir, "code-source2raw"),
        ignore=shutil.ignore_patterns(".*", "*__pycache__*", "*swp"),
        dirs_exist_ok=True,
    )

    # Replace original acronym of the project
    with open(os.path.join(args.destdir, "code-source2raw", "Makefile"), "r") as f:
        filedata = f.read()
    filedata = filedata.replace(args.acronym, "ACRONYM")
    with open(
        os.path.join(args.destdir, "code-source2raw", "Makefile"), "w", encoding="utf-8"
    ) as f:
        f.write(filedata)

    logging.info("Finished")


main()
