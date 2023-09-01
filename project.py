import os
import argparse
import curses
import random
from tabulate import tabulate

NUMBERS = range(1, 7)
PEGS = 4
ROUNDS = 10


class Board:
    def __init__(self) -> None:
        self.code = random.sample(NUMBERS, PEGS)
        self.round = 0
        self.rounds = tuple(f"{r:02}" for r in range(1, ROUNDS + 1))
        self.pegs = ["...." for _ in range(ROUNDS)]
        self.guesses = ["...." for _ in range(ROUNDS)]
        self.data = {
            "": self.rounds,
            "pegs": self.pegs,
            "code": self.guesses,
        }


def main() -> None:
    start_game()


def start_game() -> None:
    stdscr.clear()
    stdscr.box()
    stdscr.refresh()

    while True:
        board = Board()

        if CHEATS:
            cheat(board.code)

        play_game(board)


def play_game(board) -> None:
    while True:
        if board.round == 10:
            game_over(board, won=False)
            return

        BOARD.erase()
        HINT.erase()
        GUESS.erase()

        BOARD.addstr(draw_board(board.data))

        GUESS.noutrefresh()
        GUESS.mvwin(BOARD_BEG_Y + (board.round + 3), BOARD_BEG_X + 14)

        BOARD.refresh()
        HINT.refresh()

        guess = []
        while True:
            try:
                key: str = GUESS.getkey()

                if key.isdecimal() and len(guess) < 4:
                    guess.append(int(key))
                    GUESS.addch(key)

                elif key in ("KEY_BACKSPACE", "\x7f") and len(guess) > 0:
                    guess.pop()
                    GUESS.delch(0, len(guess))

                elif key == "q":
                    game_over(board, won=False)
                    return

                elif key == "\n":
                    validate_guess(guess)
                    break

                else:
                    continue

            except ValueError as ve:
                guess.clear()

                hint = "Hint:" + " " + str(ve)
                x = (HINT_X - len(hint)) // 2

                GUESS.erase()
                HINT.erase()

                HINT.addstr(0, x, hint)
                HINT.chgat(0, x, 5, curses.A_BOLD)

                HINT.refresh()

        board.pegs[board.round] = keys_peg(board.code, guess)
        board.guesses[board.round] = "".join(map(str, guess))

        if guess == board.code:
            game_over(board, won=True)
            return

        board.round += 1


def game_over(board, won=False) -> None:
    if won:
        header = "Congratulations!"
        message = (
            f"You won, your score is {(ROUNDS - board.round):02}/{ROUNDS}."  # 29 cols
        )
    else:
        header = "Oops!"
        message = f"You lost, the code was {''.join(map(str, board.code))}."  # 28 cols

    footer = "Press any key to restart, q to quit"
    x = (HINT_X - len(message)) // 2

    BOARD.erase()
    HINT.erase()

    BOARD.addstr(draw_board(board.data), curses.A_DIM)
    HINT.addstr(0, (HINT_X - len(header)) // 2, header, curses.A_BOLD)
    HINT.addstr(1, x, message)
    HINT.chgat(1, x + 23, 4 if len(message) == 28 else 5, curses.A_BOLD)
    HINT.addstr(3, (HINT_X - len(footer)) // 2, footer, curses.A_BLINK)

    BOARD.refresh()
    HINT.refresh()

    if GUESS.getkey() == "q":
        exit()


def draw_board(data: dict[tuple, list]) -> str:
    return tabulate(
        data,
        headers="keys",
        tablefmt="pretty",
        numalign="center",
    )


def keys_peg(code: list[int], guess: list[int]) -> str:
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


def validate_guess(s: list[int]) -> None:
    if len(s) != 4:
        raise ValueError("Type in 4 numbers.")

    for n in s:
        if not n in range(1, 7):
            raise ValueError("Use numbers between 1-6.")

    if len(set(s)) != 4:
        raise ValueError("Don't repeat numbers.")


def cheat(code: list) -> None:
    file = os.path.join(os.environ.get("TMPDIR", "/tmp"), "mastermind_code.txt")

    with open(file, "w") as f:
        f.write("".join(map(str, code)) + "\n")


def arg_parse() -> argparse.Namespace:
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

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        BOARD_Y, BOARD_X = (14, 21)
        HINT_Y, HINT_X = (4, 40)
        GUESS_Y, GUESS_X = (1, 5)

        BOARD_BEG_Y = (curses.LINES - (BOARD_Y + HINT_Y)) // 2
        BOARD_BEG_X = (curses.COLS - 21) // 2
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
        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()
