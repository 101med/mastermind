#!/usr/bin/env python3

import argparse
import curses
import random
import os
import textwrap
from tabulate import tabulate


class InvalidCode(ValueError):
    pass


class Help(Exception):
    pass


class GameOver(Exception):
    pass


class Board:
    NUMBERS = range(1, 7)
    ROUNDS = 10
    PEGS = 4

    def __init__(self, stdscr, cheats=False) -> None:
        self.rounds = tuple(f"{r:02}" for r in range(1, self.ROUNDS + 1))
        self.cheats = cheats

        self.stdscr: curses.window = stdscr

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

        self.HELP_Y, self.HELP_X = (40, 45)
        self.HELP_BEG_Y = self.MAIN_BEG_Y + 1
        self.HELP_BEG_X = (self.MAIN_X - self.HELP_X) // 2

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

        self.help_pad = curses.newpad(self.HELP_Y, self.HELP_X)

        self.input_window.keypad(True)
        self.help_pad.keypad(True)

        curses.curs_set(0)

    def reset(self) -> None:
        self._code = random.sample(self.NUMBERS, self.PEGS)
        self.code_pegs = []
        self.feedback_pegs = []
        self.current_round = 0
        self.player_won = False

        if self.cheats:
            self.reveal_code()

    @property
    def code(self) -> list[int]:
        return self._code

    @code.setter
    def code(self, code) -> None:
        self.validate_code(code)

        self._code = code


    def validate_code(self, code: list[int]) -> None:
        if len(code) != self.PEGS:
            raise InvalidCode(f"Enter exactly {self.PEGS} numbers.")

        for n in code:
            if n not in self.NUMBERS:
                raise InvalidCode("Use numbers between 1 and 6.")

        if len(set(code)) != self.PEGS:
            raise InvalidCode("Do not repeat numbers.")

    @property
    def current_guess(self) -> list[int]:
        return [int(n) for n in self.code_pegs[self.current_round]]

    @current_guess.setter
    def current_guess(self, guess: list[int]) -> None:
        self.validate_code(guess)
        self.code_pegs.append("".join(map(str, guess)))
        self.feedback_pegs.append("".join(self.feedback(guess)))

        if guess == self._code:
            self.player_won = True
            raise GameOver

        elif self.current_round < self.ROUNDS - 1:
            self.current_round += 1

        else:
            raise GameOver

    def feedback(self, code: list[int]) -> list[str]:
        self.validate_code(code)

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
    def data(self) -> dict:
        guesses = self.code_pegs + ["...."] * (self.ROUNDS - len(self.code_pegs))
        feedbacks = self.feedback_pegs + ["...."] * (
            self.ROUNDS - len(self.feedback_pegs)
        )

        return {
            "": self.rounds,
            "Code": guesses,
            "Pegs": feedbacks,
        }

    def draw(self) -> str:
        return tabulate(
            self.data,
            headers="keys",
            tablefmt="pretty",
            numalign="center",
        )

    def reveal_code(self) -> None:
        tmpfile = os.path.join(os.environ.get("TMPDIR", "/tmp"), "mastermind_code.txt")

        with open(tmpfile, "w") as f:
            f.write("".join(map(str, self._code)) + "\n")

    def loop(self) -> None:
        self.init_interface()

        while True:
            self.reset()

            while True:
                try:
                    self.show_board()
                    self.current_guess = self.handel_guess_input()
                except InvalidCode as e:
                    self.show_hint(e)
                except Help:
                    self.show_help()
                except GameOver:
                    self.game_over()

    def init_interface(self) -> None:
        title_text = "+MasterMind+"
        keys_text = "0-9 Guess. Enter Confirm. H Toggle help. Q quit."

        title_text_beg_x = (curses.COLS - len(title_text)) // 2
        keys_text_beg_x = (curses.COLS - len(keys_text)) // 2

        self.main_window.border("|", "|", "-", "-", "+", "+", "+", "+")

        self.stdscr.addstr(0, title_text_beg_x, title_text)
        self.stdscr.chgat(0, title_text_beg_x + 1, len(title_text) - 2, curses.A_BOLD)

        self.stdscr.addstr(curses.LINES - 1, keys_text_beg_x, keys_text)
        self.stdscr.chgat(curses.LINES - 1, keys_text_beg_x + 0, 3, curses.A_BOLD)
        self.stdscr.chgat(curses.LINES - 1, keys_text_beg_x + 11, 5, curses.A_BOLD)
        self.stdscr.chgat(curses.LINES - 1, keys_text_beg_x + 26, 1, curses.A_BOLD)
        self.stdscr.chgat(curses.LINES - 1, keys_text_beg_x + 41, 1, curses.A_BOLD)

        self.stdscr.refresh()

    def show_board(self) -> None:
        self.hint_window.erase()
        self.board_window.erase()
        self.input_window.erase()

        self.board_window.addstr(self.draw())
        self.input_window.noutrefresh()
        self.input_window.mvwin(
            self.BOARD_BEG_Y + (self.current_round) + 3, self.BOARD_BEG_X + 7
        )

        self.hint_window.noutrefresh()
        self.board_window.refresh()

    def handel_guess_input(self) -> list[int]:
        guess = []
        while True:
            key = self.input_window.getkey()

            if key.isdecimal() and len(guess) < 4:
                guess.append(int(key))
                self.input_window.addch(key)

            elif key in ("KEY_BACKSPACE", "\x7f", "\b") and len(guess) > 0:
                guess.pop()
                self.input_window.delch(0, len(guess))

            elif key.upper() == "Q":
                raise GameOver

            elif key.upper() == "H":
                raise Help

            elif key == "\n":
                return guess

            else:
                continue

    def show_hint(self, message: ValueError) -> None:
        hint_text = f"Hint: {str(message)}"
        hint_text_beg_y = (self.HINT_Y - 1) // 2
        hint_text_beg_x = (self.HINT_X - len(hint_text)) // 2

        self.hint_window.erase()

        self.hint_window.border("|", "|", "-", "-", "+", "+", "+", "+")

        self.hint_window.addstr(hint_text_beg_y, hint_text_beg_x, hint_text)
        self.hint_window.chgat(hint_text_beg_y, hint_text_beg_x, 5, curses.A_BOLD)

        self.hint_window.getkey()

    def show_help(self) -> None:
        help_text = textwrap.dedent(
            """\
    +-------------------HELP-------------------+
    |                                          |
    | - The objective is to crack a code by    |
    | creating a guess that combines numbers   |
    | within the 1 to 6 range. Ensure that     |
    | each number is used only once.           |
    |                                          |
    | - player have a maximum of 10 attempts   |
    | to break the code.                       |
    |                                          |
    | - After making a valid guess, player     |
    | will receive feedback:                   |
    |                                          |
    |  - O: Correct number and position.       |
    |  - X: Correct number, wrong position.    |
    |  - _: Number is not part of the code.    |
    |                                          |
    | - Examples:                              |
    | +------+-------+----------+              |
    | | Code | Guess | Feedback |              |
    | +------+-------+----------+              |
    | | 1234 | 1234  | OOOO     |              |
    | | 6245 | 1234  | OX__     |              |
    | +------+-------+----------+              |
    |                                          |
    | - Note: The feedback provided does not   |
    | necessarily follow the order of the code |
    | or guess (O > X > _).                    |
    |                                          |
    | - Whether player successfully break the  |
    | code or fail to do so, the game ends,    |
    | displaying a game over menu.             |
    |                                          |
    | - In either case, player have the        |
    | option to restart or exit the game.      |
    |                                          |
    | - Enjoy the game!                        |
    |                                          |
    +------------------------------------------+"""
        )

        curser_position = 0
        CURSER_POSITION_MAX = self.HELP_Y - self.MAIN_Y + 1

        self.help_pad.erase()
        self.help_pad.addstr(help_text)

        self.help_pad.refresh(
            0,
            0,
            self.HELP_BEG_Y,
            self.HELP_BEG_X,
            self.MAIN_Y - 2,
            self.HELP_BEG_X + self.HELP_X,
        )

        while True:
            key = self.help_pad.getkey()

            if (
                key.upper() in ("KEY_DOWN", "J")
                and curser_position < CURSER_POSITION_MAX
            ):
                curser_position += 1

            elif key.upper() in ("KEY_UP", "K") and curser_position > 0:
                curser_position -= 1

            elif key == "KEY_PPAGE":
                curser_position = 0

            elif key == "KEY_NPAGE":
                curser_position = CURSER_POSITION_MAX

            elif key.upper() in ("Q", "H"):
                self.help_pad.erase()
                self.help_pad.refresh(
                    0,
                    0,
                    self.HELP_BEG_Y,
                    self.HELP_BEG_X,
                    self.MAIN_Y - 2,
                    self.HELP_BEG_X + self.HELP_X,
                )
                break

            else:
                continue

            self.help_pad.refresh(
                curser_position,
                0,
                self.HELP_BEG_Y,
                self.HELP_BEG_X,
                self.MAIN_Y - 2,
                self.HELP_BEG_X + self.HELP_X,
            )

    def game_over(self) -> None:
        if self.player_won:
            score = "{:02}/{}".format(self.ROUNDS - self.current_round, self.ROUNDS)

            header_text = "Congratulations!"
            message_text = f"You won, your score is {score}"
        else:
            code_str = "".join(map(str, self._code))

            header_text = "Oops!"
            message_text = f"You lost, the code was: {code_str}"

        footer_text = "Press any key to restart (q to quit)"

        header_text_beg_x = (self.HINT_X - len(header_text)) // 2
        header_text_beg_y = ((self.HINT_Y - 1) // 2) - 1

        message_text_beg_x = (self.HINT_X - len(message_text)) // 2
        message_text_beg_y = header_text_beg_y + 2

        footer_text_beg_x = (curses.COLS - len(footer_text)) // 2
        footer_text_beg_y = self.MAIN_Y - 2

        self.board_window.erase()
        self.hint_window.erase()

        self.board_window.addstr(self.draw(), curses.A_DIM)

        self.hint_window.border("|", "|", "-", "-", "+", "+", "+", "+")

        self.hint_window.addstr(
            header_text_beg_y, header_text_beg_x, header_text, curses.A_BOLD
        )

        self.hint_window.addstr(message_text_beg_y, message_text_beg_x, message_text)
        self.hint_window.chgat(
            4, message_text_beg_x + len(message_text) - 4, 4, curses.A_BOLD
        )

        self.board_window.refresh()
        self.hint_window.refresh()

        self.stdscr.addstr(
            footer_text_beg_y, footer_text_beg_x, footer_text, curses.A_BLINK
        )

        if self.stdscr.getkey() == "q":
            exit(0)

        # Clear the footer text without clearing the whole window.
        self.stdscr.addstr(footer_text_beg_y, footer_text_beg_x, " " * len(footer_text))
        self.stdscr.refresh()

        self.reset()


def main(stdscr):
    board = Board(stdscr, cheats=args.cheats)
    board.loop()


if __name__ == "__main__":
    _parse = argparse.ArgumentParser(
        description="Classic board-game MasterMind in the terminal."
    )
    _parse.add_argument(
        "-c",
        "--cheats",
        help="store game's code in $TMPDIR/mastermind.txt",
        action="store_true",
    )

    args = _parse.parse_args()
    curses.wrapper(main)
