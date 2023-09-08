#!/usr/bin/env python3

import curses
import random
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

    def __init__(self) -> None:
        self._rounds = tuple(f"{r:02}" for r in range(1, self.ROUNDS + 1))
        self.reset()

    def reset(self) -> None:
        self._code = random.sample(self.NUMBERS, self.PEGS)
        self._code_pegs = []
        self._feedback_pegs = []
        self.current_round = 0
        self.player_won = False

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


def main() -> None:
    title = "+MasterMind+"
    title_beg_x = (curses.COLS - len(title)) // 2

    MAIN.border("|", "|", "-", "-", "+", "+", "+", "+")
    stdscr.addstr(0, title_beg_x, title)
    stdscr.chgat(0, title_beg_x + 1, len(title) - 2, curses.A_BOLD)

    keys = "0-9 Guess. Enter Confirm. H Toggle help. Q quit."
    keys_x = (curses.COLS - len(keys)) // 2
    stdscr.addstr(
        curses.LINES - 1, keys_x, keys
    )
    stdscr.chgat(curses.LINES - 1, keys_x + 0, 3, curses.A_BOLD)
    stdscr.chgat(curses.LINES - 1, keys_x + 11, 5, curses.A_BOLD)
    stdscr.chgat(curses.LINES - 1, keys_x + 26, 1, curses.A_BOLD)
    stdscr.chgat(curses.LINES - 1, keys_x + 41, 1, curses.A_BOLD)
    stdscr.refresh()

    play_game()


def play_game() -> None:
    board = Board()
    while True:
        try:
            BOARD.erase()
            HINT.erase()
            INPUT.erase()

            BOARD.addstr(board.draw())
            INPUT.noutrefresh()
            INPUT.mvwin(BOARD_BEG_Y + (board.current_round) + 3, BOARD_BEG_X + 7)

            HINT.refresh()
            BOARD.refresh()

            board.current_guess = handle_input()

        except InvalidCode as e:
            display_hint(e)

        except GameOver:
            game_over(board)

        except Help:
            show_help_menu()


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

        elif key == "q":
            raise GameOver

        elif key == "h":
            raise Help

        elif key == "\n":
            return guess

        else:
            continue


def display_hint(e: ValueError) -> None:
    hint = f"Hint: {str(e)}"
    hint_y = (HINT_Y - 1) // 2
    hint_x = (HINT_X - len(hint)) // 2

    HINT.erase()
    HINT.border("|", "|", "-", "-", "+", "+", "+", "+")
    HINT.addstr(hint_y, hint_x, hint)
    HINT.chgat(hint_y, hint_x, 5, curses.A_BOLD)
    HINT.getkey()


def game_over(board: Board) -> None:
    if board.player_won:
        header = "Congratulations!"
        message = f"You won, your score is {(board.ROUNDS - board.current_round):02}/{board.ROUNDS}."  # 29 cols
    else:
        header = "Oops!"
        message = f"You lost, the code was {''.join(map(str, board._code))}."  # 28 cols

    footer = "Press any key to restart, q to quit"

    hint_x = (HINT_X - len(message)) // 2
    hint_y = (HINT_X - len(header)) // 2

    BOARD.erase()
    HINT.erase()

    BOARD.addstr(board.draw(), curses.A_DIM)
    HINT.border("|", "|", "-", "-", "+", "+", "+", "+")
    HINT.addstr(2, hint_y, header, curses.A_BOLD)
    HINT.addstr(4, hint_x, message)
    HINT.chgat(4, hint_x + 23, 4 if len(message) == 28 else 5, curses.A_BOLD)

    BOARD.refresh()
    HINT.refresh()

    stdscr.addstr(MAIN_Y - 3, (curses.COLS - len(footer)) // 2, footer, curses.A_BLINK)

    if stdscr.getkey() == "q":
        exit(0)

    stdscr.addstr(MAIN_Y - 3, (MAIN_X - len(footer)) // 2, " " * len(footer))
    stdscr.refresh()

    board.reset()


def show_help_menu() -> None:
    help_menu_text = textwrap.dedent(
        """\
+-------------------Help-------------------+
| Objective:                               |
| ----------                               |
| - Your aim is to guess a 4-digit code in |
| 10 turns or less.                        |
|                                          |
| Code Parameters:                         |
| ----------------                         |
| - The code consists of four unique       |
| numbers between 1 and 6.                 |
|                                          |
| Examples:                                |
| - Valid Codes: 1234, 3456, 4312, etc.    |
| - Invalid Codes: 0123, 1111, 6789, etc.  |
|                                          |
| Turns:                                   |
| ------                                   |
| - You have a maximum of 10               |
| turns to guess the code.                 |
|                                          |
| Making a Guess:                          |
| ---------------                          |
| - In each turn, use the following        |
| keyboard keys:                           |
|                                          |
|   - 0-9: Enter a code combination.       |
|   - Return/Enter: Confirm your guess.    |
|   - q: Quit or restart the game.         |
|                                          |
| Feedback:                                |
| ---------                                |
| - After each guess, you'll receive       |
| feedback:                                |
|                                          |
|   - O: Correct number and position.      |
|   - X: Correct number, wrong position.   |
|   - _: Wrong number.                     |
|                                          |
| Examples:                                |
| +--------+-------+----------+            |
| | Code   | Guess | Feedback |            |
| +--------+-------+----------+            |
| | 1234   | 1234  | OOOO     |            |
| | 1234   | 1243  | OOXX     |            |
| | 1234   | 1256  | OX__     |            |
| +--------+-------+----------+            |
|                                          |
| Winning:                                 |
| --------                                 |
| - Successfully guessing the 4-digit code |
| within 10 turns results in a win.        |
|                                          |
| - Failing to do so means you lose, and   |
| the correct code is revealed.            |
|                                          |
| - You will be prompted to either restart |
| the game or quit.                        |
+------------------------------------------+"""
    )
    headers_coordinate = (
        (0, 20, 4),
        (1, 1, 11),
        (6, 1, 17),
        (15, 1, 7),
        (20, 1, 16),
        (29, 1, 10),
        (47, 1, 9),
    )
    curser_position = 0

    HELP.erase()
    HELP.addstr(help_menu_text)

    for header_coordinate in headers_coordinate:
        HELP.chgat(*header_coordinate, curses.A_BOLD)

    HELP.refresh(0, 0, 1, HELP_BEG_X, MAIN_Y - 2, HELP_BEG_X + HELP_X)

    while True:
        key = HELP.getkey()

        if key.upper() in ("KEY_DOWN", "J") and curser_position < (HELP_Y - MAIN_Y - 1):
            curser_position += 1

        elif key.upper() in ("KEY_UP", "K") and curser_position > 0:
            curser_position -= 1

        elif key.upper() in ("Q", "H"):
            HELP.erase()
            HELP.noutrefresh(0, 0, 1, HELP_BEG_X, MAIN_Y - 2, HELP_BEG_X + HELP_X)
            break

        else:
            continue

        HELP.refresh(curser_position, 0, 1, HELP_BEG_X, MAIN_Y - 2, HELP_BEG_X + HELP_X)


if __name__ == "__main__":
    try:
        stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        MAIN = stdscr.subwin(curses.LINES - 1, curses.COLS, 0, 0)
        MAIN_Y, MAIN_X = MAIN.getmaxyx()
        BOARD_Y, BOARD_X = (14, 21)
        HINT_Y, HINT_X = (7, 40)
        INPUT_Y, INPUT_X = (1, 5)
        HELP_Y, HELP_X = (61, 45)
        BOARD_BEG_Y = (MAIN_Y - BOARD_Y) // 2
        BOARD_BEG_X = (MAIN_X - BOARD_X + 1) // 2
        HINT_BEG_Y = (MAIN_Y - HINT_Y + 1) // 2
        HINT_BEG_X = (MAIN_X - HINT_X + 1) // 2
        HELP_BEG_Y = (MAIN_Y - HELP_Y + 1) // 2
        HELP_BEG_X = (MAIN_X - HELP_X + 1) // 2

        BOARD = curses.newwin(BOARD_Y, BOARD_X, BOARD_BEG_Y, BOARD_BEG_X)
        HINT = curses.newwin(HINT_Y, HINT_X, HINT_BEG_Y, HINT_BEG_X)
        INPUT = curses.newwin(INPUT_Y, INPUT_X, 1, 1)
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
