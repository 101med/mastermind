#!/usr/bin/env python3

import argparse
import curses
import os
import random
import textwrap
from tabulate import tabulate


POSSIBLE_DIGITS = range(1, 7)
MAX_ROUNDS = 10
NUM_PEGS = 4
BORDER = ["|", "|", "-", "-", "+", "+", "+", "+"]


class InvalidCode(ValueError):
    pass


class Help(Exception):
    pass


class GameOver(Exception):
    pass


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
        self.pad = curses.newpad(self.LINES, self.COLS)


class GameUI:
    def __init__(self, stdscr: curses.window) -> None:
        curses.curs_set(0)

        self.stdscr = stdscr
        self.MAIN = Window(stdscr, lines=curses.LINES - 1, cols=curses.COLS)
        self.BOARD = Window(stdscr, lines=15, cols=21)
        self.INPUT = Window(stdscr, lines=1, cols=5, y=1, x=1)
        self.HINT = Window(stdscr, lines=7, cols=40)
        self.HELP = Pad(stdscr, lines=40, cols=46)

        self.INPUT.window.keypad(True)
        self.HELP.pad.keypad(True)

    def show_menu(self) -> None:
        title = "+MASTERMIND+"
        keys = "0-9 Guess. Enter Confirm. H Toggle help. Q quit."

        title_x = (curses.COLS - len(title)) // 2
        keys_x = (curses.COLS - len(keys)) // 2

        self.stdscr.addstr(curses.LINES - 1, keys_x, keys)
        self.stdscr.chgat(curses.LINES - 1, keys_x + 0, 3, curses.A_BOLD)
        self.stdscr.chgat(curses.LINES - 1, keys_x + 11, 5, curses.A_BOLD)
        self.stdscr.chgat(curses.LINES - 1, keys_x + 26, 1, curses.A_BOLD)
        self.stdscr.chgat(curses.LINES - 1, keys_x + 41, 1, curses.A_BOLD)

        self.MAIN.window.border(*BORDER)

        self.MAIN.window.addstr(0, title_x, title)
        self.MAIN.window.chgat(0, title_x + 1, len(title) - 2, curses.A_BOLD)

        self.stdscr.refresh()
        self.MAIN.window.refresh()

    def show_board(self, guess: list[str], feedback: list[str], round: int) -> None:
        self.HINT.window.erase()
        self.BOARD.window.erase()
        self.INPUT.window.erase()

        self.BOARD.window.addstr(self.board(guess, feedback))
        self.INPUT.window.noutrefresh()
        self.INPUT.window.mvwin(self.BOARD.Y + round + 3, self.BOARD.X + 7)

        self.HINT.window.noutrefresh()
        self.BOARD.window.refresh()

    def show_hint(self, message: ValueError) -> None:
        hint = f"Hint: {str(message)}"
        hint_y = (self.HINT.LINES - 1) // 2
        hint_x = (self.HINT.COLS - len(hint)) // 2

        self.HINT.window.erase()

        self.HINT.window.border(*BORDER)

        self.HINT.window.addstr(hint_y, hint_x, hint)
        self.HINT.window.chgat(hint_y, hint_x, 5, curses.A_BOLD)

        self.HINT.window.getkey()

    def show_help(self):
        help_content = textwrap.dedent(
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

        cursor_pos = 0
        CURSOR_POS_MAX = self.HELP.LINES - self.MAIN.LINES + 1

        self.HELP.pad.erase()
        self.HELP.pad.addstr(help_content)

        self._refresh_help_pad()

        while True:
            key = self.HELP.pad.getkey()

            if key.upper() in ("KEY_DOWN", "J") and cursor_pos < CURSOR_POS_MAX:
                cursor_pos += 1

            elif key.upper() in ("KEY_UP", "K") and cursor_pos > 0:
                cursor_pos -= 1

            elif key == "KEY_PPAGE":
                cursor_pos = 0

            elif key == "KEY_NPAGE":
                cursor_pos = CURSOR_POS_MAX

            elif key.upper() in ("Q", "H", "\n"):
                self.HELP.pad.erase()
                self._refresh_help_pad()
                break

            else:
                continue

            self._refresh_help_pad(cursor_pos)

    def _refresh_help_pad(self, position: int = 0) -> None:
        self.HELP.pad.refresh(
            # position,
            # 0,
            # 1,
            # (self.HELP.LINES - self.MAIN.LINES) // 2,
            # self.MAIN.LINES - 2,
            # self.HELP.COLS,
        )

    def show_game_over(
        self,
        code: list[int],
        guess: list[str],
        feedback: list[str],
        round: int,
        player_won: bool,
    ) -> None:
        if player_won:
            score = "{:02}/{}".format(MAX_ROUNDS - round, MAX_ROUNDS)

            header = "Congratulations!"
            message = f"You won, your score is {score}"
            bold_text_lenght = 5
        else:
            code_str = "".join(map(str, code))

            header = "Oops!"
            message = f"You lost, the code was: {code_str}"
            bold_text_lenght = 4

        footer = "Press any key to restart (q to quit)"

        header_y = ((self.HINT.LINES - 1) // 2) - 1
        header_x = (self.HINT.COLS - len(header)) // 2

        message_y = header_y + 2
        message_x = (self.HINT.COLS - len(message)) // 2

        footer_y = self.MAIN.LINES - 2
        footer_x = (curses.COLS - len(footer)) // 2

        self.BOARD.window.erase()
        self.HINT.window.erase()

        self.BOARD.window.addstr(self.board(guess, feedback), curses.A_DIM)

        self.HINT.window.border(*BORDER)

        self.HINT.window.addstr(header_y, header_x, header, curses.A_BOLD)

        self.HINT.window.addstr(message_y, message_x, message)
        self.HINT.window.chgat(
            4,
            message_x + len(message) - bold_text_lenght,
            bold_text_lenght,
            curses.A_BOLD,
        )

        self.BOARD.window.refresh()
        self.HINT.window.refresh()

        self.stdscr.addstr(footer_y, footer_x, footer, curses.A_BLINK)

        if self.stdscr.getkey().upper() == "Q":
            exit(0)

        # Clear the footer text without clearing the whole window.
        self.stdscr.addstr(footer_y, footer_x, " " * len(footer))
        self.stdscr.refresh()

    def handle_user_input(self) -> list[int]:
        guess = []
        while True:
            key = self.INPUT.window.getkey()

            if key.isdecimal() and len(guess) < 4:
                guess.append(int(key))
                self.INPUT.window.addch(key)

            elif key in ("KEY_BACKSPACE", "\x7f", "\b") and len(guess) > 0:
                guess.pop()
                self.INPUT.window.delch(0, len(guess))

            elif key.upper() == "Q":
                raise GameOver

            elif key.upper() == "H":
                raise Help

            elif key == "\n":
                return guess

            else:
                continue

    @staticmethod
    def board(guess: list[str], feedback: list[str]) -> str:
        return tabulate(
            {
                "": [f"{r:02}" for r in range(1, MAX_ROUNDS + 1)],
                "Code": guess + ["...."] * (MAX_ROUNDS - len(guess)),
                "Pegs": feedback + ["...."] * (MAX_ROUNDS - len(feedback)),
            },
            headers="keys",
            tablefmt="pretty",
            numalign="center",
        )


def main(stdscr):
    ui = GameUI(stdscr)
    ui.show_menu()

    while True:
        code = random.sample(POSSIBLE_DIGITS, NUM_PEGS)
        guess_pegs = []
        feedback_pegs = []
        current_round = 0
        player_won = False

        if args.cheats:
            reveal_code(code)

        while True:
            try:
                ui.show_board(guess_pegs, feedback_pegs, current_round)
                guess = ui.handle_user_input()

                validate_code(guess)

                guess_pegs.append("".join(map(str, guess)))
                feedback_pegs.append("".join(feedback(code, guess)))

                if code == guess:
                    player_won = True
                    raise GameOver

                elif current_round + 1 < MAX_ROUNDS:
                    current_round += 1

                else:
                    raise GameOver

            except InvalidCode as e:
                ui.show_hint(e)

            except Help:
                ui.show_help()

            except GameOver:
                ui.show_game_over(
                    code, guess_pegs, feedback_pegs, current_round, player_won
                )
                break


def validate_code(code: list[int]) -> None:
    if len(code) != NUM_PEGS:
        raise InvalidCode(f"Enter exactly {NUM_PEGS} numbers.")

    for n in code:
        if n not in POSSIBLE_DIGITS:
            raise InvalidCode("Use numbers between 1 and 6.")

    if len(set(code)) != NUM_PEGS:
        raise InvalidCode("Do not repeat numbers.")


def feedback(code: list[int], guess: list[int]) -> list[str]:
    pegs = []
    for i in range(NUM_PEGS):
        if guess[i] == code[i]:
            pegs.append("O")
        elif guess[i] in code:
            pegs.append("X")
        else:
            pegs.append("_")

    pegs.sort(key=lambda item: ("O" not in item, "X" not in item, item))

    return pegs


def reveal_code(code: list[int]) -> None:
    tmpfile = os.path.join(os.environ.get("TMPDIR", "/tmp"), "mastermind_code.txt")

    with open(tmpfile, "w") as f:
        f.write("".join(map(str, code)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Classic board-game MasterMind in the terminal."
    )
    parser.add_argument(
        "-c",
        "--cheats",
        help="store game's code in $TMPDIR/mastermind.txt",
        action="store_true",
    )
    args = parser.parse_args()

    try:
        stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        main(stdscr)
    finally:
        if "stdscr" in locals():
            stdscr.keypad(False)

        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()
