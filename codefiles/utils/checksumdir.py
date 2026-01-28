#!/usr/local/bin/python

from argparse import ArgumentParser
from dirhash import dirhash
import json
import os


def compare(dirnames, hashstrs):
    n_match = []
    for dirname, hashstr in zip(dirnames, hashstrs):
        checksum = dirhash(dirname, algorithm="md5", ignore=[".*"])
        if checksum == hashstr:
            n_match.append(True)
        else:
            n_match.append(False)
    return n_match


def main():
    parser = ArgumentParser(
        prog="checksumdir",
        description="Check the md5 hash of directory(-ies)",
        epilog="",
    )

    parser.add_argument("dir", nargs="+", type=str, help="directory to check")
    parser.add_argument("--hash", nargs="+", type=str, help="hash to check against")
    parser.add_argument(
        "--log-output-dir",
        action="store",
        type=str,
        help="directory to output successful check",
    )
    args = parser.parse_args()

    if args.hash is None:
        for dirname in args.dir:
            checksum = dirhash(dirname, algorithm="md5", ignore=[".*"])
            print(dirname, checksum)
        parser.exit(message="Print dir hash to stdout and exit\n")

    if not len(args.dir) == len(args.hash):
        parser.error("Number of dirs and hashes not equal")

    n_match = compare(args.dir, args.hash)
    result = dict(zip(args.dir, n_match))
    json_obj = json.dumps(result, indent=4)
    if not sum(result.values()) == len(args.dir):
        print(json_obj)
        parser.error("Hash does not match")
    if args.log_output_dir is None:
        print(json_obj)
        parser.exit()
    with open(
        os.path.join(args.log_output_dir, "checksumdir.log"), "w", encoding="utf-8"
    ) as f:
        f.write("Source data match\n")
    parser.exit(message="Result written to a file\n")


main()
