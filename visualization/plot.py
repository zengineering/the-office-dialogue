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


def characterDataToArrays(character_data):
    names = np.array([char.name for char in character_data])
    lines = np.array([char.lines for char in character_data])
    episodes = np.array([char.episodes for char in character_data])
    return names, lines, episodes


def main(json_path):
    character_data = parseData(json_path)

    names, lines, episodes = characterDataToArrays(sorted(character_data, key=lambda char: char.total_lines))
    plotByCharacter(names, lines, "the-office-lines.png", title="Number of dialogue lines per character", xticks=np.arange(0, 13001, 1000))

    names, lines, episodes = characterDataToArrays(sorted(character_data, key=lambda char: char.total_episodes))
    plotByCharacter(names, episodes, "the-office-episodes.png", title="Number of dialogue episodes per character")


def plotByCharacter(names, lines, outfile, *, title=None, xticks=None, bar_height=0.8, colors=None, dpi=200, font_size=6):
    num_seasons = lines.shape[1]-1
    y_pos = np.arange(len(names))
    seasons = np.arange(1, num_seasons+1)
    if not colors:
        colors = ("", "brown", "yellow", "blue", "limegreen", "darkorange", "aqua", "purple", "red", "black")

    plots = [mplot.barh(y_pos, lines[:, s], bar_height, lines[:, 0:s].sum(1), color=colors[s]) for s in seasons]

    mplot.title(title)
    mplot.yticks(y_pos, names, fontsize=font_size)
    if xticks is not None:
        mplot.xticks(xticks, fontsize=font_size)
    mplot.legend((p[0] for p in plots), ("Season {}".format(s) for s in seasons), fontsize=font_size)
    mplot.savefig(outfile, orientation="landscape", dpi=200)
    mplot.close()


if __name__ == "__main__":
    args = parseArgs()
    main(args.input_file)

