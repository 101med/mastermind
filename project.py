import os
import argparse
import curses
import random
from tabulate import tabulate

NUMBERS = range(1, 7)
PEGS = 4
ROUNDS = 10


def main() -> None:
    stdscr.clear()
    stdscr.box()
    # stdscr.addstr(1, 22, "Help:", curses.A_BOLD)
    # stdscr.addstr(2, 22, "O: Correct n and spot.")
    # stdscr.addstr(3, 22, "X: Correct n, wrong spot.")
    # stdscr.addstr(4, 22, "_: Incorrect number.")
    stdscr.refresh()

    start_game()


def cheat(code: list) -> None:
    tmpdir = os.environ.get("TMPDIR", "/tmp")

    with open(os.path.join(tmpdir, "mastermind_code.txt"), "w") as f:
        f.write("".join(map(str, code)) + "\n")


def start_game() -> None:
    while True:
        code = random.sample(NUMBERS, PEGS)
        board_data = {
            "": [f"{r:02}" for r in range(1, ROUNDS + 1)],
            "pegs": ["...." for _ in range(ROUNDS)],
            "code": ["...." for _ in range(ROUNDS)],
        }

        if cheats:
            cheat(code)

        play_game(code, board_data)


def play_game(code: list, data: dict) -> None:
    current_round = 0

    while True:
        HINT.erase()
        GUESS.erase()

        GUESS.refresh()
        GUESS.mvwin(BOARD.getbegyx()[0] + (current_round + 3), BOARD.getbegyx()[1] + 14)
        display_board(data)
        HINT.refresh()

        if current_round >= 10:
            game_over(won=False, code=code, data=data)
            return

        guess = []
        while True:
            try:
                key: str = GUESS.getkey()

                if key.isdecimal() and len(guess) < 4:
                    guess.append(int(key))
                elif key == "KEY_BACKSPACE" and len(guess) > 0:
                    guess.pop()
                elif key == "q":
                    game_over(won=False, code=code, data=data)
                    return
                elif key == "\n":
                    validate_guess(guess)
                    break
                else:
                    continue

                GUESS.erase()
                GUESS.addstr("".join(map(str, guess)))
            except ValueError as ve:
                guess.clear()

                GUESS.erase()
                display_hint(ve)

        data["pegs"][current_round] = keys_peg(code, guess)
        data["code"][current_round] = "".join(map(str, guess))

        if guess == code:
            game_over(won=True, r=current_round, data=data)
            return
        else:
            current_round += 1


def display_hint(s) -> None:
    hint = "Hint:" + " " + str(s)
    hint_centerd_x = (HINT.getmaxyx()[1] - len(hint)) // 2

    HINT.erase()
    HINT.addstr(0, hint_centerd_x, hint)
    HINT.chgat(0, hint_centerd_x, 5, curses.A_BOLD)
    HINT.refresh()


def display_board(data: dict, end=False) -> None:
    BOARD.erase()
    BOARD.addstr(
        tabulate(
            data,
            headers="keys",
            tablefmt="pretty",
            numalign="center",
        ),
        curses.A_NORMAL if not end else curses.A_DIM,
    )
    BOARD.refresh()


def game_over(won=False, code=[1, 2, 3, 4], r=9, data={}) -> None:
    try:
        if won:
            header = "Congratulations!"
            message = f"You won, your score is {ROUNDS - r}/{ROUNDS}."  # 29 cols
        else:
            header = "Oops!"
            message = f"You lost, the code was {''.join(map(str, code))}."  # 28 cols
    finally:
        footer = "Press any key to restart, q to quit"

    message_centerd_x = (40 - len(message)) // 2

    HINT.erase()

    display_board(data, end=True)

    HINT.addstr(0, (40 - len(header)) // 2, header, curses.A_BOLD)
    HINT.addstr(1, message_centerd_x, message)
    HINT.chgat(
        1,
        message_centerd_x + 23,
        4 if len(message) == 28 else 5,
        curses.A_BOLD,
    )
    HINT.addstr(
        3,
        (HINT.getmaxyx()[1] - len(footer)) // 2,
        footer,
        curses.A_BLINK,
    )

    BOARD.refresh()
    HINT.refresh()

    if GUESS.getkey() == "q":
        exit()

    BOARD.bkgd(curses.A_NORMAL)


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Curses Mastermind game")
    parser.add_argument(
        "-c",
        "--cheats",
        action="store_true",
        help="Enable cheats (code stored in ${TMPDIR}/mastermind_code.txt)",
    )
    args = parser.parse_args()

    try:
        stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        # curses.curs_set(0)

        BOARD = curses.newwin(
            14, 21, (curses.LINES - (14 + 4)) // 2, (curses.COLS - 21) // 2
        )
        HINT = curses.newwin(
            4, 40, BOARD.getbegyx()[0] + (14 + 1), (curses.COLS - 40) // 2
        )
        GUESS = curses.newwin(1, 5, 1, 1)

        GUESS.keypad(True)

        if args.cheats:
            cheats = True
        else:
            cheats = False

        main()

    finally:
        if "GUESS" in locals():
            GUESS.keypad(False)

        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()
