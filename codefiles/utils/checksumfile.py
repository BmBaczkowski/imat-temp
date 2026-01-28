#!/usr/local/bin/python

from argparse import ArgumentParser
import hashlib
import json
import os


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def main():
    parser = ArgumentParser(
        prog="checksumfile", description="Check the md5 hash of a file", epilog=""
    )

    parser.add_argument("filename", type=str, help="File to check")
    parser.add_argument("--hash", type=str, help="hash to check against")
    parser.add_argument(
        "--log-output-dir",
        action="store",
        type=str,
        help="directory to output successful check",
    )
    args = parser.parse_args()

    checksum = md5(args.filename)

    if args.hash is None:
        print(checksum)
        parser.exit(message="Print hash to stdout and exit\n")

    if args.log_output_dir is None:
        parser.error(message="Directory to output check missing")
    if not args.hash == checksum:
        parser.error(message="Hash does not match")

    with open(
        os.path.join(args.log_output_dir, "checksumkeyfile.log"), "w", encoding="utf-8"
    ) as f:
        f.write("File hash matches\n")
    parser.exit(message="Result written to a file\n")


main()
