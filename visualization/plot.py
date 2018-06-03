#!/usr/bin/env python3

from argparse import ArgumentParser
from collections import namedtuple
import json
import matplotlib.pyplot as mplot

Character = namedtuple("Character", ("name", "lines", "episodes"))

def parseArgs():
    ap = ArgumentParser(description = "Plot The Office character dialogue stats.")
    ap.add_argument('input_file', help="JSON with character dialogue info")
    return ap.parse_args()

def parseData(json_path):
    with open(json_path) as json_fp:
        dialogue = json.load(json_fp)

    characters = []

    for speaker, seasons in dialogue.items():
        lineCounts = [0] * 10
        episodeCounts = [0] * 10
        for season, episodes in seasons.items():
            lineCounts[int(season)] = sum(map(int, episodes.values()))
            episodeCounts[int(season)] = len(episodes)
        characters.append(Character(speaker, lineCounts, episodeCounts))

    return characters

def main(json_path):
    characters = parseData(json_path)
    print(characters)


if __name__ == "__main__":
    args = parseArgs()
    main(args.input_file)
