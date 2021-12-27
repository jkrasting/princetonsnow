#!/usr/bin/env python

""" Utility to work with JSON formatted snow observations """

import json
import os
import re
import sys


def load_json(fname):
    """Loads a JSON file into memory"""

    assert os.path.exists(fname), "File not found."

    with open(fname, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
    json_file.close()

    return json_data


def create_event():
    """Creates a snow event"""

    result = {}

    # event start date
    start_date = input("Start date of event (YYYY-MM-DD): ")
    if start_date != "":
        result["start_date"] = start_date

        end_date = input("Optional -- end date of event (YYYY-MM-DD): ")
        if end_date != "":
            result["end_date"] = end_date

        obs = None
        while obs != "":
            obs = input("Enter an observation (site value): ")
            if obs != "":
                if len(obs.split(" ")) == 2:
                    site, value = obs.split(" ")
                    if value.replace(".", "").isnumeric():
                        value = float(value)
                    result[site] = value
                    if site == "gfdl":
                        obs = ""
                else:
                    pattern = re.compile("[^A-Za-z0-9. ]+")
                    obs = pattern.sub(" ", obs)
                    obs = re.sub(" +", " ", obs)
                    obs = obs.split(" ")
                    assert (len(obs) % 2) == 0, "Multi-obs entry must be even."
                    for x in range(0, len(obs), 2):
                        site = obs[x]
                        value = obs[x + 1]
                        if value.replace(".", "").isnumeric():
                            value = float(value)
                        result[site] = value
                        print(f"    - {site}: {value}")
                    obs = ""

        comment = input("Optional -- enter a comment: ")
        if comment != "":
            result["comment"] = comment
    else:
        result = None

    return result


def summarize_events(event_list):
    """Prints summary text for a season"""
    total = 0.0
    for _event in event_list:
        values = [x for x in _event.values() if isinstance(x, float)]
        if len(values) > 0:
            mean = sum(values) / len(values)
            mean = round(mean, 1)
        else:
            mean = 0.0
        total += mean
        print(f" * {_event['start_date']} - {mean}")
    total = round(total, 1)
    print("------------------")
    print(f"Total: {total}")


if __name__ == "__main__":
    FNAME = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else None
    events = load_json(FNAME) if FNAME is not None else []
    if not isinstance(events, list):
        events = [events]
    numevents = len(events)

    event = {}
    while event is not None:
        try:
            event = create_event()
        except Exception as e:
            print(e)
            print("Try again ...")
        if event is not None:
            events.append(event)
        print("\n")

    if len(events) > 0:
        summarize_events(events)

    if len(events) > numevents:
        write = input("Write file to disk?  (Y/n): ")
        if write == "Y":
            if FNAME is None:
                FNAME = input("Enter a file name: ")
            with open(FNAME, "w", encoding="utf-8") as f:
                json.dump(events, f, ensure_ascii=False, indent=4)
            f.close()

sys.exit()
