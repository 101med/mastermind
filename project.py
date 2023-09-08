import argparse
import curses
import os
import random

# import subprocess
import textwrap
from tabulate import tabulate


# class SmallTerminal(Exception):
#     """Exception raised when the terminal's coordinates are less then 21x50."""
#
#     pass


class ExitHelp(Exception):
    pass


class GameOver(Exception):
    """Exception raised when the game is over."""

    pass


class InvalidCode(ValueError):
    """Exception raised when an invalid code is made or set."""

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
        self.validate_code(code)

        self._code = code

    @property
    def current_guess(self) -> list[int]:
        """Get the current guess."""
        return [int(n) for n in self._code_pegs[self.current_round]]

    @current_guess.setter
    def current_guess(self, guess: list[int]) -> None:
        """Set the current guess and check if the game is won or lost."""
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
        """Provide feedback for a guess."""
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
        """Get a formated data for displaying the board correctly."""
        return {
            "": self._rounds,
            "Code": self._code_pegs + ["...."] * (self.ROUNDS - len(self._code_pegs)),
            "Pegs": self._feedback_pegs
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
            self.data,
            headers="keys",
            tablefmt="pretty",
            numalign="center",
        )

    def validate_code(self, code: list[int]) -> None:
        """Validate a code guess."""
        if len(code) != self.PEGS:
            raise InvalidCode(f"Enter exactly {self.PEGS} numbers.")

        for n in code:
            if n not in self.NUMBERS:
                raise InvalidCode("Use numbers between 1 and 6.")

        if len(set(code)) != self.PEGS:
            raise InvalidCode("Do not repeat numbers.")


# def main(LINES: int, COLS: int) -> None:
def main() -> None:
    _parse = argparse.ArgumentParser(
        prog="mastermind.py", description="Mastermind, A Classic Board Game in Curses."
    )
    _parse.add_argument(
        "-c",
        "--cheat",
        help="store game's code in $TMPDIR/mastermind.txt",
        action="store_true",
    )

    args = _parse.parse_args()
    try:
        stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        BOARD_Y, BOARD_X = (14, 21)
        HINT_Y, HINT_X = (4, 40)
        INPUT_Y, INPUT_X = (1, 5)
        HELP_Y, HELP_X = (61, 45)

        BOARD_BEG_Y = (curses.LINES - (BOARD_Y + HINT_Y)) // 2
        BOARD_BEG_X = (curses.COLS - 21 + 1) // 2
        HINT_BEG_Y = BOARD_BEG_Y + BOARD_Y + 1
        HINT_BEG_X = (curses.COLS - HINT_X) // 2
        HELP_BEG_X = (curses.COLS - HELP_X) // 2

        board_window = curses.newwin(BOARD_Y, BOARD_X, BOARD_BEG_Y, BOARD_BEG_X)
        hint_window = curses.newwin(HINT_Y, HINT_X, HINT_BEG_Y, HINT_BEG_X)
        input_window = curses.newwin(INPUT_Y, INPUT_X, 1, 1)
        help_pad = curses.newpad(HELP_Y, HELP_X)

        input_window.keypad(True)
        help_pad.keypad(True)

        CHEAT = True if args.cheat else False

        play_game(
            stdscr,
            board_window,
            hint_window,
            input_window,
            help_pad,
            BOARD_BEG_Y,
            BOARD_BEG_X,
            HINT_X,
            HELP_Y,
            HELP_X,
            HELP_BEG_X,
            CHEAT,
        )

    finally:
        input_window.keypad(False)
        help_pad.keypad(False)

        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()


def play_game(
    stdscr: curses.window,
    board_window: curses.window,
    hint_window: curses.window,
    input_window: curses.window,
    help_pad: curses.window,
    BOARD_BEG_Y: int,
    BOARD_BEG_X: int,
    HINT_X: int,
    HELP_Y: int,
    HELP_X: int,
    HELP_BEG_X: int,
    CHEAT: bool,
) -> None:
    """Game loop."""
    board = Board()

    stdscr.clear()
    stdscr.box()
    stdscr.refresh()

    while True:
        try:
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
                    board.current_guess = make_guess(
                        input_window, help_pad, HELP_Y, HELP_X, HELP_BEG_X
                    )
                    break
                except InvalidCode as e:
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

        except ExitHelp:
            continue


def make_guess(
    input_window: curses.window,
    help_pad: curses.window,
    HELP_Y: int,
    HELP_X: int,
    HELP_BEG_X: int,
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

        elif key == "h":
            help_menu(help_pad, HELP_Y, HELP_X, HELP_BEG_X)
            raise ExitHelp

        elif key == "\n":
            return guess

        else:
            continue


def help_menu(
    help_pad: curses.window,
    HELP_Y: int,
    HELP_X: int,
    HELP_BEG_X: int,
) -> None:
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
        +------------------------------------------+        
        """
    )
    headers_coordinate = (
        (0, 20, 4),
        (1, 1, 11),
        (6, 1, 17),
        (15, 1, 7),
        (20, 1, 16),
        (29, 1, 10),
        (38, 1, 10),
        (47, 1, 9),
    )
    curser_position = 0

    help_pad.erase()
    help_pad.addstr(help_menu_text)

    for header_coordinate in headers_coordinate:
        help_pad.chgat(*header_coordinate, curses.A_BOLD)

    help_pad.refresh(0, 0, 1, HELP_BEG_X, curses.LINES - 2, HELP_BEG_X + HELP_X)

    while True:
        key = help_pad.getkey()

        if key.upper() in ("KEY_DOWN", "J") and curser_position < (
            HELP_Y - curses.LINES - 1
        ):
            curser_position += 1

        elif key.upper() in ("KEY_UP", "K") and curser_position > 0:
            curser_position -= 1

        elif key.upper() == "Q":
            help_pad.erase()
            help_pad.refresh(0, 0, 1, HELP_BEG_X, curses.LINES - 2, HELP_BEG_X + HELP_X)
            break

        else:
            continue

        help_pad.refresh(
            curser_position, 0, 1, HELP_BEG_X, curses.LINES - 2, HELP_BEG_X + HELP_X
        )


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
    # try:
    #     LINES, COLS = map(
    #         int,
    #         subprocess.check_output(
    #             r"printf 'lines\ncols' | tput -S", shell=True, text=True
    #         ).splitlines(),
    #     )
    #
    #     if LINES < 21 or COLS < 50:
    #         raise SmallTerminal
    #
    #     main(LINES, COLS)
    # except SmallTerminal:
    #     print(
    #         "Please resize your terminal to a minimum size of 21x50 or larger to fully enjoy the game.",
    #         f"Current: {LINES}x{COLS}.",
    #         sep="\n",
    #     )
    #     exit(1)
