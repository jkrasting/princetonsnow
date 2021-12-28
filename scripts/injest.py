#!/usr/bin/env python

""" Utility to work with JSON formatted snow observations """

import datetime
import json
import os
import re
import sys


def days_since_oct1(date_string):
    """Calculates the number of days since 1-Oct"""
    event_date = tuple([int(x) for x in date_string.split("-")])
    event_date = datetime.datetime(*event_date)
    ref_year = (
        event_date.year if event_date.month in [10, 11, 12] else event_date.year - 1
    )
    ref_date = datetime.datetime(ref_year, 10, 1)
    return (event_date - ref_date).days


def fix_missing_season_date(event):
    """Adds days since Oct 1 to older json files"""
    if "day_of_season" not in event.keys():
        event["day_of_season"] = days_since_oct1(event["start_date"])
    return event


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
    dates = input("Start date of event (YYYY-MM-DD): ")

    if dates != "":
        dates = dates.split(",")
        start_date = dates[0]

        end_date = dates[1] if len(dates) == 2 else ""

        result["day_of_season"] = days_since_oct1(start_date)
        result["start_date"] = start_date

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
                    obs = [x for x in obs if len(x) > 0]
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
        print(f" * {_event['start_date']} ({_event['day_of_season']}) - {mean}")
    total = round(total, 1)
    print("------------------")
    print(f"Total: {total}")


if __name__ == "__main__":
    FNAME = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else None
    events = load_json(FNAME) if FNAME is not None else []
    if not isinstance(events, list):
        events = [events]
    numevents = len(events)

    events = [fix_missing_season_date(x) for x in events]

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
