#!/usr/bin/env python3

import argparse
import curses
import os
import random
from tabulate import tabulate

NUMBERS = range(1, 7)
PEGS = 4
ROUNDS = 10


class Board:
    """Represents the game board for a Mastermind-style game."""

    def __init__(self) -> None:
        """Initialize the game board."""
        self.reset()

    def reset(self) -> None:
        """Reset board's values to start a new game."""
        self._code = random.sample(NUMBERS, PEGS)
        self._rounds = tuple(f"{r:02}" for r in range(1, ROUNDS + 1))
        self._pegs = ["...."] * ROUNDS
        self._guesses = ["...."] * ROUNDS
        self._round = 0

    @property
    def code(self) -> list[int]:
        """Get the secret code as a list of integers."""
        return self._code

    @property
    def pegs(self) -> list[str]:
        """Get the list of feedback pegs for each round."""
        return self._pegs

    @property
    def guesses(self) -> list[str]:
        """Get the list of player guesses for each round."""
        return self._guesses

    @property
    def round(self) -> int:
        """Get the current round number."""
        return self._round

    @property
    def rounds(self) -> tuple[str]:
        """Get the formatted round numbers as a tuple of strings."""
        return self._rounds

    def __key_pegs(self, guess) -> str:
        """Calculate the key pegs for a given guess."""
        pegs = [
            "O" if guess[n] == self._code[n] else "X" if guess[n] in self._code else "_"
            for n in range(PEGS)
        ]

        pegs.sort(key=lambda peg: ("O" not in peg, "X" not in peg, peg))

        return "".join(pegs)

    @property
    def current_guess(self) -> str:
        """Get the current player's guess for the current round."""
        return self._guesses[self._round]

    @current_guess.setter
    def current_guess(self, s: list[int]) -> None:
        """Set the current player's guess for the current round."""

        if len(s) != PEGS:
            raise ValueError("Enter exactly 4 numbers.")

        for n in s:
            if n not in NUMBERS:
                raise ValueError("Use numbers between 1 and 6.")

        if len(set(s)) != PEGS:
            raise ValueError("Do not repeat numbers.")

        self._guesses[self.round] = "".join(map(str, s))
        self._pegs[self.round] = self.__key_pegs(s)

    def next_round(self) -> None:
        """Move to the next round of the game if available."""
        if self._round < 9:
            self._round += 1
        else:
            raise Exception("Game Over.")

    def draw(self) -> str:
        """
        Generate a formatted representation of the game board.

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
            {
                "": self._rounds,
                "pegs": self._pegs,
                "code": self._guesses,
            },
            headers="keys",
            tablefmt="pretty",
            numalign="center",
        )


def main() -> None:
    stdscr.clear()
    stdscr.box()
    stdscr.refresh()

    start_game()


def start_game() -> None:
    board = Board()

    while True:
        if CHEATS:
            cheat(board.code)

        play_game(board)


def play_game(board) -> None:
    """Play rounds of the game until a player wins, quits, or the game is completed."""
    while True:
        try:
            BOARD.erase()
            HINT.erase()
            GUESS.erase()

            BOARD.addstr(board.draw())
            GUESS.noutrefresh()
            GUESS.mvwin(BOARD_BEG_Y + (board.round + 3), BOARD_BEG_X + 14)

            BOARD.refresh()
            HINT.refresh()

            while True:
                try:
                    board.current_guess = make_guess()
                    break
                except ValueError as ve:
                    display_hint(ve)

            if board.current_guess == board.code:
                game_over(board, won=True)
                return
            else:
                board.next_round()

        except Exception:
            game_over(board, won=False)
            return


def make_guess() -> list[int]:
    guess = []
    while True:
        key = GUESS.getkey()

        if key.isdecimal() and len(guess) < 4:
            guess.append(int(key))
            GUESS.addch(key)

        elif key in ("KEY_BACKSPACE", "\x7f") and len(guess) > 0:
            guess.pop()
            GUESS.delch(0, len(guess))
        elif key == "q":
            raise Exception("Game over")

        elif key == "\n":
            return guess

        else:
            continue


def game_over(board, won=False) -> None:
    try:
        if won:
            header, message = (
                "Congratulations!",
                f"You won, your score is {(ROUNDS - board.round):02}/{ROUNDS}.",  # 29 cols
            )
        else:
            header, message = (
                "Oops!",
                f"You lost, the code was {''.join(map(str, board.code))}.",  # 28 cols
            )
    finally:
        footer = "Press any key to restart, q to quit"

    x = (HINT_X - len(message)) // 2

    BOARD.erase()
    HINT.erase()

    BOARD.addstr(board.draw(), curses.A_DIM)
    HINT.addstr(0, (HINT_X - len(header)) // 2, header, curses.A_BOLD)
    HINT.addstr(1, x, message)
    HINT.chgat(1, x + 23, 4 if len(message) == 28 else 5, curses.A_BOLD)
    HINT.addstr(3, (HINT_X - len(footer)) // 2, footer, curses.A_BLINK)

    BOARD.refresh()
    HINT.refresh()

    if GUESS.getkey() == "q":
        exit(0)

    board.reset()


def display_hint(s: ValueError) -> None:
    hint = "{} {}".format("Hint:", str(s))
    x = (HINT_X - len(hint)) // 2
    GUESS.erase()
    HINT.erase()

    HINT.addstr(0, x, hint)
    HINT.chgat(0, x, 5, curses.A_BOLD)

    HINT.refresh()


def cheat(code: list[int]) -> None:
    tmpfile = os.path.join(os.environ.get("TMPDIR", "/tmp"), "mastermind_code.txt")

    with open(tmpfile, "w") as f:
        f.write("".join(map(str, code)) + "\n")


def arg_parse() -> argparse.Namespace:
    """Parse command line arguments."""
    p = argparse.ArgumentParser()
    p.add_argument(
        "-c",
        "--cheats",
        help="store game's code in $TMPDIR/mastermind.txt",
        action="store_true",
    )

    return p.parse_args()


if __name__ == "__main__":
    args = arg_parse()
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
        GUESS_Y, GUESS_X = (1, 5)

        BOARD_BEG_Y = (curses.LINES - (BOARD_Y + HINT_Y)) // 2
        BOARD_BEG_X = (curses.COLS - 21 + 1) // 2
        HINT_BEG_Y = BOARD_BEG_Y + BOARD_Y + 1
        HINT_BEG_X = (curses.COLS - HINT_X) // 2

        BOARD = curses.newwin(BOARD_Y, BOARD_X, BOARD_BEG_Y, BOARD_BEG_X)
        HINT = curses.newwin(HINT_Y, HINT_X, HINT_BEG_Y, HINT_BEG_X)
        GUESS = curses.newwin(GUESS_Y, GUESS_X, 1, 1)

        GUESS.keypad(True)

        if args.cheats:
            CHEATS = True
        else:
            CHEATS = False

        main()

    finally:
        if "GUESS" in locals():
            GUESS.keypad(False)

        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()
