#!/usr/local/bin/python

from argparse import ArgumentParser
import json
import logging
import os


def main():
    parser = ArgumentParser(prog="bids_assessment_questions", description="", epilog="")
    parser.add_argument("destdir", type=str, help="data output directory")
    parser.add_argument("logdir", type=str, help="log directory")
    args = parser.parse_args()

    FILEOUT = os.path.join(args.destdir, "free_text_questions.json")

    # prepare the log for debugging
    logfile = os.path.join(args.logdir, "free_text_questions.log")
    logging.basicConfig(
        filename=logfile, encoding="utf-8", filemode="w", level=logging.DEBUG
    )

    jsonstring = {
        "task_with_pairs_rule_description": {
            "Description": "Please describe in your own words what the rule was in the first task. What were the combinations between sounds and symbols? If you do not know what to answer, please write this down as well.",
            "Response": "free text",
        },
        "task_with_pairs_strategy_description": {
            "Description": "What strategy did you use to learn and memorize combinations between sounds and symbols in the first task? If you did not use a strategy, please write this down as well.",
            "Response": "free text",
        },
        "tasks_with_shocks_rule_description": {
            "Description": "Please describe in your own words what the rule was in the tasks with shocks. When was the shock given? If you do not know what to answer, please write this down as well.",
            "Response": "free text",
        },
        "task_with_shocks_strategy_description": {
            "Description": "In the tasks with shocks, what did you think about when you had to decide whether a shock might come? Did you try to predict the shock in advance, i.e., that the shock might occur when the symbol (or sound) ended? If you do not know what to answer, please write this down as well.",
            "Response": "free text",
        },
    }

    logging.info("Saving free text questions into assessment/ json file")
    with open(FILEOUT, "w", encoding="utf-8") as f:
        json.dump(jsonstring, f, ensure_ascii=False, indent=4)

    logging.info("Finished")


main()
