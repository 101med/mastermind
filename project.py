import os
import argparse
import curses
import random
from tabulate import tabulate


def main() -> None:
    start_game()


def start_game():
    stdscr.clear()
    stdscr.box()
    stdscr.refresh()

    while True:
        code = random.sample(NUMBERS, PEGS)
        board_data = {
            "": [f"{r:02}" for r in range(1, ROUNDS + 1)],
            "pegs": ["...." for _ in range(ROUNDS)],
            "code": ["...." for _ in range(ROUNDS)],
        }

        if CHEATS:
            cheat(code)

        play_game(code, board_data)


def play_game(code, data):
    current_round = 0

    while True:
        BOARD.erase()
        HINT.erase()

        GUESS.erase()
        GUESS.refresh()

        BOARD.addstr(draw_board(data))
        GUESS.mvwin(BOARD_BEG_Y + (current_round + 3), BOARD_BEG_X + 14)

        BOARD.refresh()
        HINT.refresh()
        GUESS.refresh()

        if current_round >= 10:
            game_over(won=False, code=code, data=data)
            return


def game_over(
    code=[1, 2, 3, 4],
    data={},
    r=9,
    won=False,
) -> None:
    if won:
        header = ""
        message = ""
    else:
        header = ""
        message = ""


def draw_board(data: dict) -> str:
    return tabulate(
        data,
        headers="keys",
        tablefmt="pretty",
        numalign="center",
    )


def keys_peg(code: list, guess: list) -> str:
    pegs = []
    for p in range(PEGS):
        if guess[p] == code[p]:
            pegs.append("O")
        elif guess[p] in code:
            pegs.append("X")
        else:
            pegs.append("_")

    return "".join(
        sorted(pegs, key=lambda item: ("O" not in item, "X" not in item, item))
    )


def validate_guess(s: list) -> None:
    if len(s) != 4:
        raise ValueError("Type in 4 numbers.")

    for n in s:
        if not n in range(1, 7):
            raise ValueError("Use numbers between 1-6.")

    if len(set(s)) != 4:
        raise ValueError("Don't repeat numbers.")


def cheat(code: list) -> None:
    tmpdir = os.environ.get("TMPDIR", "/tmp")
    if os.path.exists(tmpdir):
        with open(os.path.join(tmpdir, "mastermind_code.txt"), "w") as f:
            f.write("".join(map(str, code)) + "\n")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Curses Mastermind game.")

    parser.add_argument(
        "-c",
        "--cheat",
        action="store_true",
        help="store the game's code in $TMPDIR/mastermind_code.txt",
    )

    return parser.parse_args()


if __name__ == "__main__":
    NUMBERS = range(1, 7)
    PEGS = 4
    ROUNDS = 10

    args = parse_arguments()

    try:
        stdscr = curses.initscr()
        y, x = stdscr.getmaxyx()

        if y < 21 or x < 50:
            print("Please resize your term to 21x50 or more.")
            exit(1)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        BOARD_Y, BOARD_X = (14, 15)
        HINT_Y, HINT_X = (4, 40)
        GUESS_Y, GUESS_X = (1, 5)
        BOARD_BEG_Y = (y - (BOARD_Y + HINT_Y)) // 2
        BOARD_BEG_X = (x - (BOARD_X - 1)) // 2
        HINT_BEG_Y = BOARD_BEG_Y + BOARD_Y
        HINT_BEG_X = (x - HINT_X) // 2

        BOARD = curses.newwin(BOARD_Y, BOARD_X, BOARD_BEG_Y, BOARD_BEG_X)
        HINT = curses.newwin(HINT_Y, HINT_X, HINT_BEG_Y, HINT_BEG_X)
        GUESS = curses.newwin(GUESS_Y, GUESS_X, 1, 1)
        GUESS.keypad(True)

        CHEATS = True if args.cheats else False

        main()
    finally:
        if "GUESS" in locals():
            GUESS.keypad(False)

        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()
