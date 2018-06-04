#!/usr/bin/env python3

import json
import matplotlib.pyplot as mplot
import numpy as np
from argparse import ArgumentParser

class Character():
    '''
    Data class to store character dialogue data
    '''
    def __init__(self, name, lines, episodes):
        '''
        name: name of the character
        lines: [] of line counts for each season
        episodes: [] of line counts for each season

        lines and episodes are len=10 (9 seasons plus 0-index)
        '''
        self.name = name
        self.lines = lines
        self.episodes = episodes
        self.lines_per_episode = [self.lines[i]/self.episodes[i] if self.episodes[i] != 0 else 0
            for i in range(len(self.episodes))]

    @property
    def total_lines(self):
        return sum(self.lines)

    @property
    def total_episodes(self):
        return sum(self.episodes)

    @property
    def total_lines_per_episode(self):
        return sum(self.lines_per_episode)


def parseArgs():
    '''
    Commandline argument parsing
    '''
    ap = ArgumentParser(description = "Plot The Office character dialogue stats.")
    ap.add_argument('input_file', help="JSON with character dialogue info")
    return ap.parse_args()


def parseData(json_path):
    '''
    Read JSON file of the format
        { character: { season: { episode: line count } } }
    Parse into and return a list of Characters
    '''
    with open(json_path) as json_fp:
        dialogue = json.load(json_fp)

    characters = []

    for speaker, seasons in dialogue.items():
        line_counts = [0] * 10
        episode_counts = [0] * 10
        for season, episodes in seasons.items():
            line_counts[int(season)] = sum(map(int, episodes.values()))
            episode_counts[int(season)] = len(episodes)
        characters.append(Character(speaker, line_counts, episode_counts))

    return characters


def stackedBarByCharacter(names, data, outfile, *, title=None, xticks=None, bar_height=0.8, colors=None, dpi=200, font_size=6):
    '''
    Plot a horizontal-stacked-bar chart of character info
    '''
    num_seasons = data.shape[1]-1
    y_pos = np.arange(len(names))
    seasons = np.arange(1, num_seasons+1)
    if not colors:
        colors = ("", "brown", "yellow", "blue", "limegreen", "darkorange", "aqua", "purple", "red", "black")

    plots = [mplot.barh(y_pos, data[:, s], bar_height, data[:, 0:s].sum(1), color=colors[s]) for s in seasons]

    if mplot.title:
        mplot.title(title)
    if xticks is not None:
        mplot.xticks(xticks, fontsize=font_size)
    mplot.yticks(y_pos, names, fontsize=font_size)
    mplot.legend((p[0] for p in plots), ("Season {}".format(s) for s in seasons), fontsize=font_size)
    mplot.savefig(outfile, orientation="landscape", dpi=dpi)
    mplot.close()


def barByCharacter(names, data, outfile, *, title=None, xticks=None, bar_height=0.8, colors=None, dpi=200, font_size=6):
    '''
    Plot a horizontal-bar chart of character info
    '''
    y_pos = np.arange(len(names))

    mplot.barh(y_pos, data, bar_height)

    mplot.title(title)
    mplot.yticks(y_pos, names, fontsize=font_size)
    if xticks is not None:
        mplot.xticks(xticks, fontsize=font_size)
    mplot.savefig(outfile, orientation="landscape", dpi=dpi)
    mplot.close()


def main(json_path):
    '''
    Parse JSON; format and plot it
    '''
    character_data = parseData(json_path)
    names = np.array([char.name for char in character_data])
    lines = np.array([char.lines for char in character_data])
    episodes = np.array([char.episodes for char in character_data])
    lines_per_episode = np.array([char.lines_per_episode for char in character_data])

    # dialogue lines
    order = lines.sum(axis=1).argsort()
    stackedBarByCharacter(names[order], lines[order], "the-office-lines.png", title="Lines of dialogue", xticks=np.arange(0, 13001, 1000))

    # episodes
    order = episodes.sum(axis=1).argsort()
    stackedBarByCharacter(names[order], episodes[order], "the-office-episodes.png", title="Episodes with dialogue")

    # lines per episode (per season)
    order = lines_per_episode.sum(axis=1).argsort()
    stackedBarByCharacter(names[order], lines_per_episode[order], "the-office-lines-per-episode-seasonal.png", title="Seasonal average lines of dialogue per episode")

    # lines per episode (overall)
    olpe = lines.sum(axis=1) / episodes.sum(axis=1)
    order = olpe.argsort()
    barByCharacter(names[order], olpe[order], "the-office-lines-per-episode-overall.png", title="Overall average lines of dialogue per episode")

    # stdev of lines-per-episode
    lpe_std = lines_per_episode.std(axis=1)
    order = lpe_std.argsort()
    barByCharacter(names[order], lpe_std[order], "the-office-lines-per-episode-std.png", title="Standard deviation of lines of dialogue per episode")


if __name__ == "__main__":
    args = parseArgs()
    main(args.input_file)

