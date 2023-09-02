#!/usr/bin/env python3

import argparse
import curses
import os
from board import *


def main() -> None:
    stdscr.clear()
    stdscr.box()
    stdscr.refresh()

    start_game()


def start_game():
    ...


def play_game():
    ...


def make_guess():
    ...


def game_over():
    ...


def display_hint():
    ...


def cheat():
    ...


def arg_parse():
    ...


def init_windows():
    ...


if __name__ == "__main__":
    try:
        stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        
        ...

        main()
    finally:
        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()
