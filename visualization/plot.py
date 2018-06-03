#!/usr/bin/env python3

import json
import matplotlib.pyplot as mplot
import numpy as np
from argparse import ArgumentParser

class Character():
    def __init__(self, name, lines, episodes):
        self.name = name
        self.lines = lines
        self.episodes = episodes

    @property
    def total_lines(self):
        return sum(self.lines)

    @property
    def total_episodes(self):
        return sum(self.episodes)


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
    characters.sort(key=lambda char: char.total_lines, reverse=True)
    characters = characters[:5]
    #print(characters)

    num_seasons = 9
    bar_height = 0.8
    seasons = np.arange(1, num_seasons+1)
    y_pos = np.arange(len(characters))
    plots = []
    for i, char in enumerate(characters):
        print("[{}] {}:".format(i, char.name))
        for season in seasons:
            plots.append(mplot.barh(y_pos, char.lines[season], bar_height, char.lines[season-1]))
            print(season, end="...")
        print()

    mplot.title("Number of dialogue lines per character")
    mplot.ylabel("Character")
    mplot.yticks(y_pos, map(lambda char: char.name, characters))
    mplot.xlabel("Lines of dialogue")
    #mplot.xticks(np.arange(0,70001, 500))
    mplot.legend(map(lambda p: p[0], plots), map(lambda s: "Season {}".format(s), seasons))
    print("axes")

    mplot.savefig("the-office-lines.png", orientation="landscape", dpi=200)
    print("saved")
    mplot.close()
    print("closed")


if __name__ == "__main__":
    args = parseArgs()
    main(args.input_file)

