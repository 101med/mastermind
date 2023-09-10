#!/usr/bin/env python3

import argparse
import curses
import random
import os
import textwrap
from tabulate import tabulate


class GameOver(Exception):
    pass


class InvalidCode(ValueError):
    pass


class Help(Exception):
    pass


class Board:
    ROUNDS = 10
    NUMBERS = range(1, 7)
    PEGS = 4

    def __init__(self, cheats=False) -> None:
        self._rounds = tuple(f"{r:02}" for r in range(1, self.ROUNDS + 1))
        self._cheats = cheats

        self.reset()

    def reset(self) -> None:
        self._code = random.sample(self.NUMBERS, self.PEGS)
        self._code_pegs = []
        self._feedback_pegs = []
        self.current_round = 0
        self.player_won = False

        if self._cheats:
            self.reveal_code()

    @property
    def cheats(self) -> bool:
        return self._cheats

    @cheats.setter
    def cheats(self, c: bool) -> None:
        if isinstance(c, bool):
            self._cheats = c

    @property
    def code(self) -> list[int]:
        return self._code

    @code.setter
    def code(self, code: list[int]) -> None:
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
        return [int(n) for n in self._code_pegs[self.current_round]]

    @current_guess.setter
    def current_guess(self, guess: list[int]) -> None:
        self.validate_code(guess)
        self._code_pegs.append("".join(map(str, guess)))
        self._feedback_pegs.append("".join(self.feedback(guess)))

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
        guesses = self._code_pegs + ["...."] * (self.ROUNDS - len(self._code_pegs))
        feedbacks = self._feedback_pegs + ["...."] * (
            self.ROUNDS - len(self._feedback_pegs)
        )

        return {
            "": self._rounds,
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
            f.write("".join(map(str, self.code)) + "\n")


def main():
    init_interface()
    play_game()


def init_interface() -> None:
    title_text = "+MasterMind+"
    instructions_text = "0-9 Guess. Enter Confirm. H Toggle help. Q quit."

    title_text_beg_x = (curses.COLS - len(title_text)) // 2
    instructions_text_beg_x = (curses.COLS - len(instructions_text)) // 2

    MAIN.border("|", "|", "-", "-", "+", "+", "+", "+")

    stdscr.addstr(0, title_text_beg_x, title_text)
    stdscr.chgat(0, title_text_beg_x + 1, len(title_text) - 2, curses.A_BOLD)

    stdscr.addstr(curses.LINES - 1, instructions_text_beg_x, instructions_text)
    stdscr.chgat(curses.LINES - 1, instructions_text_beg_x + 0, 3, curses.A_BOLD)
    stdscr.chgat(curses.LINES - 1, instructions_text_beg_x + 11, 5, curses.A_BOLD)
    stdscr.chgat(curses.LINES - 1, instructions_text_beg_x + 26, 1, curses.A_BOLD)
    stdscr.chgat(curses.LINES - 1, instructions_text_beg_x + 41, 1, curses.A_BOLD)

    stdscr.refresh()


def play_game() -> None:
    board = Board(cheats=True if args.cheats else False)

    while True:
        try:
            refresh_board(board)
            board.current_guess = handle_input()

        except InvalidCode as e:
            show_hint(e)

        except GameOver:
            game_over(board)

        except Help:
            show_help_menu()


def refresh_board(board) -> None:
    BOARD.erase()
    HINT.erase()
    INPUT.erase()

    BOARD.addstr(board.draw())
    INPUT.noutrefresh()
    INPUT.mvwin(BOARD_BEG_Y + (board.current_round) + 3, BOARD_BEG_X + 7)

    HINT.noutrefresh()
    BOARD.refresh()


def handle_input() -> list[int]:
    guess = []
    while True:
        key = INPUT.getkey()

        if key.isdecimal() and len(guess) < 4:
            guess.append(int(key))
            INPUT.addch(key)

        elif key in ("KEY_BACKSPACE", "\x7f", "\b") and len(guess) > 0:
            guess.pop()
            INPUT.delch(0, len(guess))

        elif key.upper() == "Q":
            raise GameOver

        elif key.upper() == "H":
            raise Help

        elif key == "\n":
            return guess

        else:
            continue


def show_hint(e: ValueError) -> None:
    hint_text = f"Hint: {str(e)}"
    hint_text_beg_y = (HINT_Y - 1) // 2
    hint_text_beg_x = (HINT_X - len(hint_text)) // 2

    HINT.erase()

    HINT.border("|", "|", "-", "-", "+", "+", "+", "+")

    HINT.addstr(hint_text_beg_y, hint_text_beg_x, hint_text)
    HINT.chgat(hint_text_beg_y, hint_text_beg_x, 5, curses.A_BOLD)

    HINT.getkey()


def game_over(board: Board) -> None:
    if board.player_won:
        score = "{:02}/{}".format(board.ROUNDS - board.current_round, board.ROUNDS)

        header_text = "Congratulations!"
        message_text = f"You won, your score is {score}"
    else:
        code_str = "".join(map(str, board._code))

        header_text = "Oops!"
        message_text = f"You lost, the code was: {code_str}"

    footer_text = "Press any key to restart (q to quit)"

    header_text_beg_x = (HINT_X - len(header_text)) // 2
    header_text_beg_y = ((HINT_Y - 1) // 2) - 1

    message_text_beg_x = (HINT_X - len(message_text)) // 2
    message_text_beg_y = header_text_beg_y + 2

    footer_text_beg_x = (curses.COLS - len(footer_text)) // 2
    footer_text_beg_y = MAIN_Y - 2

    BOARD.erase()
    HINT.erase()

    BOARD.addstr(board.draw(), curses.A_DIM)

    HINT.border("|", "|", "-", "-", "+", "+", "+", "+")

    HINT.addstr(header_text_beg_y, header_text_beg_x, header_text, curses.A_BOLD)

    HINT.addstr(message_text_beg_y, message_text_beg_x, message_text)
    HINT.chgat(4, message_text_beg_x + len(message_text) - 4, 4, curses.A_BOLD)

    BOARD.refresh()
    HINT.refresh()

    stdscr.addstr(footer_text_beg_y, footer_text_beg_x, footer_text, curses.A_BLINK)

    if stdscr.getkey() == "q":
        exit(0)

    # Clear the footer text without clearing the whole window.
    stdscr.addstr(footer_text_beg_y, footer_text_beg_x, " " * len(footer_text))
    stdscr.refresh()

    board.reset()


def show_help_menu() -> None:
    help_menu_text = textwrap.dedent(
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
    CURSER_POSITION_MAX = HELP_Y - MAIN_Y + 2

    HELP.erase()
    HELP.addstr(help_menu_text)

    HELP.refresh(0, 0, HELP_BEG_Y, HELP_BEG_X, MAIN_Y - 2, HELP_BEG_X + HELP_X)

    while True:
        key = HELP.getkey()

        if key.upper() in ("KEY_DOWN", "J") and curser_position < CURSER_POSITION_MAX:
            curser_position += 1

        elif key.upper() in ("KEY_UP", "K") and curser_position > 0:
            curser_position -= 1

        elif key == "KEY_PPAGE":
            curser_position = 0

        elif key == "KEY_NPAGE":
            curser_position = CURSER_POSITION_MAX

        elif key.upper() in ("Q", "H"):
            HELP.erase()
            HELP.noutrefresh(
                0, 0, HELP_BEG_Y, HELP_BEG_X, MAIN_Y - 2, HELP_BEG_X + HELP_X
            )
            break

        else:
            continue

        HELP.refresh(
            curser_position, 0, HELP_BEG_Y, HELP_BEG_X, MAIN_Y - 2, HELP_BEG_X + HELP_X
        )


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
    try:
        stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        MAIN_Y, MAIN_X = (curses.LINES - 1, curses.COLS)
        MAIN_BEG_Y = (curses.LINES - MAIN_Y) // 2
        MAIN_BEG_X = (curses.COLS - MAIN_X) // 2
        MAIN = stdscr.subwin(MAIN_Y, MAIN_X, MAIN_BEG_Y, MAIN_BEG_X)

        BOARD_Y, BOARD_X = (14, 21)
        BOARD_BEG_Y = (MAIN_Y - BOARD_Y) // 2
        BOARD_BEG_X = (MAIN_X - BOARD_X) // 2
        BOARD = curses.newwin(BOARD_Y, BOARD_X, BOARD_BEG_Y, BOARD_BEG_X)

        HINT_Y, HINT_X = (7, 40)
        HINT_BEG_Y = (MAIN_Y - HINT_Y) // 2
        HINT_BEG_X = (MAIN_X - HINT_X) // 2
        HINT = stdscr.subwin(HINT_Y, HINT_X, HINT_BEG_Y, HINT_BEG_X)

        INPUT_Y, INPUT_X = (1, 5)
        INPUT_BEG_Y = 1
        INPUT_BEG_X = 1
        INPUT = stdscr.subwin(INPUT_Y, INPUT_X, INPUT_BEG_Y, INPUT_BEG_X)

        HELP_Y, HELP_X = (40, 45)
        HELP_BEG_Y = MAIN_BEG_Y + 1
        HELP_BEG_X = (MAIN_X - HELP_X) // 2
        HELP = curses.newpad(HELP_Y, HELP_X)

        INPUT.keypad(True)
        HELP.keypad(True)

        main()
    finally:
        if "INPUT" in locals():
            INPUT.keypad(False)

        if "HELP" in locals():
            HELP.keypad(False)

        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()
