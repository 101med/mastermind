#!/usr/bin/env python3

import curses


BORDER = ["|", "|", "-", "-", "+", "+", "+", "+"]


class Screen:
    def __init__(self, stdscr: curses.window, lines: int, cols: int) -> None:
        self.stdscr = stdscr
        self.LINES = lines
        self.COLS = cols


class Window(Screen):
    def __init__(
        self, stdscr: curses.window, lines: int, cols: int, y=None, x=None
    ) -> None:
        super().__init__(stdscr, lines, cols)

        self.Y = y if y is not None else ((curses.LINES - 1) - self.LINES) // 2
        self.X = x if x is not None else (curses.COLS - self.COLS) // 2
        self.window = curses.newwin(self.LINES, self.COLS, self.Y, self.X)


class Pad(Screen):
    def __init__(self, stdscr: curses.window, lines: int, cols: int) -> None:
        super().__init__(stdscr, lines, cols)
        self.window = curses.newwin(self.LINES, self.COLS)


class GameUI:
    def __init__(self, stdscr: curses.window) -> None:
        self.MAIN = Window(stdscr, lines=curses.LINES - 1, cols=curses.COLS)
        self.BOARD = Window(stdscr, lines=15, cols=21)
        self.INPUT = Window(stdscr, lines=1, cols=5, y=1, x=1)
        self.HINT = Window(stdscr, lines=7, cols=40)
        self.HELP = Pad(stdscr, lines=40, cols=46)


def main(stdscr):
    ui = GameUI(stdscr)


if __name__ == "__main__":
    curses.wrapper(main)
