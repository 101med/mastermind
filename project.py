#!/usr/bin/env python3

import argparse
import curses
import os
import random
from tabulate import tabulate


class GameOver(Exception):
    """Exception raised when the game is over."""
    pass


class InvalidGuess(ValueError):
    """Exception raised when an invalid guess is made."""
    pass


class Board:
    """Class representing the game board."""
    ROUNDS = 10
    NUMBERS = range(1, 7)
    PEGS = 4

    def __init__(self) -> None:
        """Initialize a new game board."""
        self._rounds = tuple(f"{r:02}" for r in range(1, self.ROUNDS + 1))
        self.reset()

    def reset(self) -> None:
        """Reset the game board for a new game."""
        self._code = random.sample(self.NUMBERS, self.PEGS)
        self._code_pegs = []
        self._feedback_pegs = []
        self.current_round = 0
        self.player_won = False

    @property
    def code(self):
        """Get the secret code."""
        return self._code

    @code.setter
    def code(self, code):
        """Set the secret code."""
        self.__validate_code(code)

        self._code = code

    @property
    def current_guess(self) -> list[int]:
        """Get the current guess."""
        return [int(n) for n in self._code_pegs[self.current_round]]

    @current_guess.setter
    def current_guess(self, guess: list[int]) -> None:
        """Set the current guess and check if the game is won or lost."""
        self.__validate_code(guess)

        self._code_pegs.append("".join(map(str, guess)))
        self._feedback_pegs.append("".join(self.__feedback(guess)))

        if guess == self._code:
            self.player_won = True
            raise GameOver

        elif self.current_round < self.ROUNDS - 1:
            self.current_round += 1

        else:
            raise GameOver

    def __feedback(self, code: list[int]) -> list[str]:
        """Provide feedback for a guess."""
        self.__validate_code(code)

        feedback_pegs = []
        try:
            for i in range(self.PEGS):
                if code[i] == self._code[i]:
                    feedback_pegs.append("O")
                elif code[i] in self._code:
                    feedback_pegs.append("X")
                else:
                    feedback_pegs.append("_")
        finally:
            feedback_pegs.sort(
                key=lambda item: ("O" not in item, "X" not in item, item)
            )

        return feedback_pegs

    @property
    def __data(self) -> dict:
        """Get a formated data for displaying the board correctly."""
        return {
            "": self._rounds,
            "code": self._code_pegs + ["...."] * (self.ROUNDS - len(self._code_pegs)),
            "pegs": self._feedback_pegs
            + ["...."] * (self.ROUNDS - len(self._feedback_pegs)),
        }

    def draw(self) -> str:
        """
        Generate a representation of the game board.

        Returns:
            +----+------+------+
            |    | pegs | code |
            +----+------+------+
            | 01 | .... | .... |
            | 02 | .... | .... |
            | 03 | .... | .... |
            | 04 | .... | .... |
            | 05 | .... | .... |
            | 06 | .... | .... |
            | 07 | .... | .... |
            | 08 | .... | .... |
            | 09 | .... | .... |
            | 10 | .... | .... |
            +----+------+------+
        """
        return tabulate(
            self.__data,
            headers="keys",
            tablefmt="pretty",
            numalign="center",
        )

    def __validate_code(self, code: list[int]) -> None:
        """Validate a code guess."""
        if len(code) != self.PEGS:
            raise InvalidGuess(f"Enter exactly {self.PEGS} numbers.")

        for n in code:
            if n not in self.NUMBERS:
                raise InvalidGuess("Use numbers between 1 and 6.")

        if len(set(code)) != self.PEGS:
            raise InvalidGuess("Do not repeat numbers.")


def main() -> None:
    _parse = argparse.ArgumentParser()
    _parse.add_argument(
        "-c",
        "--cheat",
        help="store game's code in $TMPDIR/mastermind.txt",
        action="store_true",
    )

    args = _parse.parse_args()
    try:
        stdscr = curses.initscr()

        if curses.LINES < 21 or curses.COLS < 50:
            print("Resize your terminal to play the game (21x50 or more)")
            exit(1)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        BOARD_Y, BOARD_X = (14, 21)
        HINT_Y, HINT_X = (4, 40)
        INPUT_Y, INPUT_X = (1, 5)

        BOARD_BEG_Y = (curses.LINES - (BOARD_Y + HINT_Y)) // 2
        BOARD_BEG_X = (curses.COLS - 21 + 1) // 2
        HINT_BEG_Y = BOARD_BEG_Y + BOARD_Y + 1
        HINT_BEG_X = (curses.COLS - HINT_X) // 2

        board_window = curses.newwin(BOARD_Y, BOARD_X, BOARD_BEG_Y, BOARD_BEG_X)
        hint_window = curses.newwin(HINT_Y, HINT_X, HINT_BEG_Y, HINT_BEG_X)
        input_window = curses.newwin(INPUT_Y, INPUT_X, 1, 1)

        input_window.keypad(True)

        CHEAT = True if args.cheat else False

        play_game(
            stdscr,
            board_window,
            hint_window,
            input_window,
            BOARD_BEG_Y,
            BOARD_BEG_X,
            HINT_X,
            CHEAT,
        )

    finally:
        if "input_window" in locals():
            input_window.keypad(False)

        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()


def play_game(
    stdscr: curses.window,
    board_window: curses.window,
    hint_window: curses.window,
    input_window: curses.window,
    BOARD_BEG_Y: int,
    BOARD_BEG_X: int,
    HINT_X: int,
    CHEAT: bool,
) -> None:
    """Play the game loop."""
    board = Board()

    stdscr.clear()
    stdscr.box()
    stdscr.refresh()

    while True:
        if CHEAT:
            cheat(board.code)

        board_window.erase()
        hint_window.erase()
        input_window.erase()

        board_window.addstr(board.draw())
        input_window.noutrefresh()
        input_window.mvwin(BOARD_BEG_Y + (board.current_round) + 3, BOARD_BEG_X + 7)

        board_window.refresh()
        hint_window.refresh()

        while True:
            try:
                board.current_guess = make_guess(input_window)
                break
            except InvalidGuess as e:
                hint = f"Hint: {str(e)}"
                hint_x = (HINT_X - len(hint)) // 2

                input_window.erase()
                hint_window.erase()

                hint_window.addstr(0, hint_x, hint)
                hint_window.chgat(0, hint_x, 5, curses.A_BOLD)

                hint_window.refresh()

            except GameOver:
                game_over(
                    board,
                    board_window,
                    hint_window,
                    input_window,
                    HINT_X,
                )
                break


def make_guess(
    input_window: curses.window,
) -> list[int]:
    """Get the player's guess"""
    guess = []
    while True:
        key = input_window.getkey()

        if key.isdecimal() and len(guess) < 4:
            guess.append(int(key))
            input_window.addch(key)

        elif key in ("KEY_BACKSPACE", "\x7f") and len(guess) > 0:
            guess.pop()
            input_window.delch(0, len(guess))

        elif key == "q":
            raise GameOver

        elif key == "\n":
            return guess

        else:
            continue


def game_over(
    board: Board,
    board_window: curses.window,
    hint_window: curses.window,
    input_window: curses.window,
    HINT_X: int,
) -> None:
    """Handle the end of the game."""
    if board.player_won:
        header = "Congratulations!"
        message = f"You won, your score is {(board.ROUNDS - board.current_round):02}/{board.ROUNDS}."  # 29 cols
    else:
        header = "Oops!"
        message = f"You lost, the code was {''.join(map(str, board._code))}."  # 28 cols

    footer = "Press any key to restart, q to quit"
    hint_x = (HINT_X - len(message)) // 2

    board_window.erase()
    hint_window.erase()

    board_window.addstr(board.draw(), curses.A_DIM)
    hint_window.addstr(0, (HINT_X - len(header)) // 2, header, curses.A_BOLD)
    hint_window.addstr(1, hint_x, message)
    hint_window.chgat(1, hint_x + 23, 4 if len(message) == 28 else 5, curses.A_BOLD)
    hint_window.addstr(3, (HINT_X - len(footer)) // 2, footer, curses.A_BLINK)

    board_window.refresh()
    hint_window.refresh()

    if input_window.getkey() == "q":
        exit(0)

    board.reset()


def cheat(
    code: list[int],
) -> None:
    """Enabels cheats by writing the secret code to a file."""
    tmpfile = os.path.join(os.environ.get("TMPDIR", "/tmp"), "mastermind_code.txt")

    with open(tmpfile, "w") as f:
        f.write("".join(map(str, code)) + "\n")


if __name__ == "__main__":
    main()
