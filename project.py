#!/usr/bin/env python3

import curses
import random


class Board:
    NUMBERS = range(1, 7)
    ROUNDS = 10
    PEGS = 4

    def __init__(self, stdscr) -> None:
        self.stdscr: curses.window = stdscr

        self._calc_coordinate()

        self.main_window = self.stdscr.subwin(
            self.MAIN_Y, self.MAIN_X, self.MAIN_BEG_Y, self.MAIN_BEG_X
        )
        self.board_window = curses.newwin(
            self.BOARD_Y, self.BOARD_X, self.BOARD_BEG_Y, self.BOARD_BEG_X
        )
        self.hint_window = curses.newwin(
            self.HINT_Y, self.HINT_X, self.HINT_BEG_Y, self.HINT_BEG_X
        )
        self.input_window = curses.newwin(
            self.INPUT_Y, self.INPUT_X, self.INPUT_BEG_Y, self.INPUT_BEG_X
        )

        self.input_window.keypad(True)

    def _calc_coordinate(self):
        self.MAIN_Y, self.MAIN_X = (curses.LINES - 1, curses.COLS)
        self.MAIN_BEG_Y = (curses.LINES - self.MAIN_Y) // 2
        self.MAIN_BEG_X = (curses.COLS - self.MAIN_X) // 2

        self.BOARD_Y, self.BOARD_X = (14, 21)
        self.BOARD_BEG_Y = (self.MAIN_Y - self.BOARD_Y) // 2
        self.BOARD_BEG_X = (self.MAIN_X - self.BOARD_X) // 2

        self.HINT_Y, self.HINT_X = (7, 40)
        self.HINT_BEG_Y = (self.MAIN_Y - self.HINT_Y) // 2
        self.HINT_BEG_X = (self.MAIN_X - self.HINT_X) // 2

        self.INPUT_Y, self.INPUT_X = (1, 5)
        self.INPUT_BEG_Y = 1
        self.INPUT_BEG_X = 1

    def reset(self) -> None:
        self.code = random.sample(self.NUMBERS, self.PEGS)

    def loop(self) -> None:
        while True:
            self.reset()

            while True:
                try:
                    show_board()
                    self.current_guess = handel_guess_input()
                except InvalidCode as e:
                    show_hint(e)
                except Help:
                    show_help()
                except GameOver:
                    game_over()


def main(stdscr):
    board = Board(stdscr)
    board.loop()


if __name__ == "__main__":
    curses.wrapper(main)
