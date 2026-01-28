#!/usr/local/bin/python

import os
import sys


def show_usage(name):
    print("Usage: ", name, "destdir\n")
    return sys.exit()


# read in parameters
n = len(sys.argv)
if n < 2:
    name = sys.argv[0]
    show_usage(os.path.basename(name))

# content of the bids ignore file
bidsignore = (
    "# directories ignored by BIDS validator\n"
    ".gitignore\n"
    ".git/\n"
    "logfiles/\n"
    "assessment/\n"
    "phenotype/\n"
    "code-psychtoolbox/\n"
    "code-source2raw/\n"
)

# content of CHANGES
CHANGES = "Revision history\n\n" "1.0.0 yyyy-mm-dd\n\n" " - Initial release\n"

destdir = sys.argv[1]
bidsignore_file = os.path.join(destdir, ".bidsignore")
changes_file = os.path.join(destdir, "CHANGES")
readme_file = os.path.join(destdir, "README.md")
license_file = os.path.join(destdir, "LICENSE")
logfile = os.path.join(destdir, "logfiles", "bids_init.log")

with open(bidsignore_file, "w", encoding="utf-8") as f:
    f.write(bidsignore)
with open(changes_file, "w", encoding="utf-8") as f:
    f.write(CHANGES)
with open(readme_file, "w", encoding="utf-8") as f:
    f.write("")
with open(license_file, "w", encoding="utf-8") as f:
    f.write("")
with open(logfile, "w", encoding="utf-8") as f:
    f.write("Data structure initiated\n")
