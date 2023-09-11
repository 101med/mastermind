#!/usr/bin/env python3

import argparse
import curses
import random
import os
import textwrap
from tabulate import tabulate

POSSIBLE_DIGITS = range(1, 7)
MAX_ROUNDS = 10
NUM_PEGS = 4


class InvalidCode(ValueError):
    pass


class Help(Exception):
    pass


class GameOver(Exception):
    pass


class MasterMindGame:
    def __init__(self, cheats=False):
        self.rounds = [f"{r:02}" for r in range(1, MAX_ROUNDS + 1)]
        self.cheats = cheats
        self.reset()

    def reset(self) -> None:
        self.code = self.generate_code()
        self.code_pegs = []
        self.feedback_pegs = []
        self.current_round = 0
        self.player_won = False

    def generate_code(self) -> list[int]:
        """Generate and return the secret code"""
        return random.sample(POSSIBLE_DIGITS, NUM_PEGS)

    @property
    def current_guess(self) -> list[int]:
        return [int(n) for n in self.code_pegs[self.current_round]]

    @current_guess.setter
    def current_guess(self, guess: list[int]) -> None:
        self.make_guess(guess)

    def make_guess(self, code) -> None:
        """Process the player's guess and update the game state"""
        if len(code) != NUM_PEGS:
            raise InvalidCode(f"Enter exactly {NUM_PEGS} numbers.")

        for n in code:
            if n not in POSSIBLE_DIGITS:
                raise InvalidCode("Use numbers between 1 and 6.")

        if len(set(code)) != NUM_PEGS:
            raise InvalidCode("Do not repeat numbers.")

        self.code_pegs.append("".join(map(str, code)))
        self.feedback_pegs.append("".join(self._feedback(code)))

        if code == self.code:
            self.player_won = True
            raise GameOver

        elif self.current_round + 1 < MAX_ROUNDS:
            self.current_round += 1

        else:
            raise GameOver

    def _feedback(self, code) -> list[str]:
        pegs = []
        for i in range(NUM_PEGS):
            if code[i] == self.code[i]:
                pegs.append("O")
            elif code[i] in self.code:
                pegs.append("X")
            else:
                pegs.append("_")

        pegs.sort(key=lambda item: ("O" not in item, "X" not in item, item))

        return pegs

    def get_game_data(self) -> dict:
        guesses = self.code_pegs + ["...."] * (MAX_ROUNDS - len(self.code_pegs))
        pegs = self.feedback_pegs + ["...."] * (MAX_ROUNDS - len(self.feedback_pegs))

        return {
            "": self.rounds,
            "Code": guesses,
            "Pegs": pegs,
        }

    def reveal_code(self) -> None:
        tmpfile = os.path.join(os.environ.get("TMPDIR", "/tmp"), "mastermind_code.txt")

        with open(tmpfile, "w") as f:
            f.write("".join(map(str, self.code)) + "\n")


class MasterMindUI:
    def __init__(self, stdscr: curses.window, game: MasterMindGame):
        self.stdscr = stdscr
        self.game = game
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components (windows, coordinate, etc.)"""
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

    def show_static_ui(self) -> None:
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

    def show_board(self):
        self.hint_window.erase()
        self.board_window.erase()
        self.input_window.erase()

        self.board_window.addstr(self._draw_board())
        self.input_window.noutrefresh()
        self.input_window.mvwin(
            self.BOARD_BEG_Y + (self.game.current_round) + 3, self.BOARD_BEG_X + 7
        )

        self.hint_window.noutrefresh()
        self.board_window.refresh()

    def handle_user_input(self):
        """Handle user input (guesses, commands, etc.)"""
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

    def show_hint(self, message):
        """Display a hint message on the screen"""
        hint_text = f"Hint: {str(message)}"
        hint_text_beg_y = (self.HINT_Y - 1) // 2
        hint_text_beg_x = (self.HINT_X - len(hint_text)) // 2

        self.hint_window.erase()

        self.hint_window.border("|", "|", "-", "-", "+", "+", "+", "+")

        self.hint_window.addstr(hint_text_beg_y, hint_text_beg_x, hint_text)
        self.hint_window.chgat(hint_text_beg_y, hint_text_beg_x, 5, curses.A_BOLD)

        self.hint_window.getkey()

    def show_help(self):
        """Display the help screen"""
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

            elif key.upper() in ("Q", "H", "\n"):
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

    def show_game_over(self):
        """Display the game over screen"""
        if self.game.player_won:
            score = "{:02}/{}".format(MAX_ROUNDS - self.game.current_round, MAX_ROUNDS)

            header_text = "Congratulations!"
            message_text = f"You won, your score is {score}"
        else:
            code_str = "".join(map(str, self.game.code))

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

        self.board_window.addstr(self._draw_board(), curses.A_DIM)

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

    def _draw_board(self) -> str:
        return tabulate(
            self.game.get_game_data(),
            headers="keys",
            tablefmt="pretty",
            numalign="center",
        )

    def run(self):
        self.show_static_ui()

        while True:
            self.game.reset()

            if self.game.cheats:
                self.game.reveal_code()

            while True:
                try:
                    self.show_board()
                    self.game.current_guess = self.handle_user_input()
                except InvalidCode as e:
                    self.show_hint(e)
                except Help:
                    self.show_help()
                except GameOver:
                    self.show_game_over()
                    break


def main(stdscr):
    game = MasterMindGame(cheats=args.cheats)
    ui = MasterMindUI(stdscr, game)
    ui.run()


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

    curses.wrapper(main)
