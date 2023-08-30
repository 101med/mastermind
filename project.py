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
    stdscr.addstr(1, 22, "Help:", curses.A_BOLD)
    stdscr.addstr(2, 22, "O: Correct n and spot.")
    stdscr.addstr(3, 22, "X: Correct n, wrong spot.")
    stdscr.addstr(4, 22, "_: Incorrect number.")
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

        if CHEATS:
            cheat(code)

        play_game(code, board_data)


def play_game(code: list, data: dict) -> None:
    current_round = 0

    while True:
        BOARD.erase()
        HINT.erase()
        GUESS.erase()

        BOARD.addstr(draw_board(data))
        GUESS.mvwin(current_round + 3, 14)

        BOARD.refresh()
        HINT.refresh()
        GUESS.refresh()

        if current_round >= 10:
            game_over(won=False, code=code)
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
                    game_over(won=False, code=code)
                    return
                elif key == "\n":
                    validate_guess(guess)
                    break
                else:
                    continue

                GUESS.erase()
                GUESS.addstr("".join(map(str, guess)))
                GUESS.refresh()
            except ValueError as ve:
                guess.clear()

                HINT.erase()
                GUESS.erase()
                HINT.addstr(0, 0, "Hint:", curses.A_BOLD)
                HINT.addstr(1, 0, str(ve))
                HINT.refresh()
                GUESS.refresh()

        data["pegs"][current_round] = keys_peg(code, guess)
        data["code"][current_round] = "".join(map(str, guess))

        if guess == code:
            game_over(won=True, r=current_round)
            return
        else:
            current_round += 1


def game_over(won=False, code=[1, 2, 3, 4], r=9) -> None:
    HINT.erase()
    BOARD.bkgd(curses.A_DIM)

    if won:
        HINT.addstr(0, 0, "Congratulations!", curses.A_BOLD)
        HINT.addstr(1, 0, f"You won, your score is {ROUNDS - r}/{ROUNDS}.")
        HINT.chgat(1, 23, 5, curses.A_BOLD)
    else:
        HINT.addstr(0, 0, "Oops!", curses.A_BOLD)
        HINT.addstr(1, 0, f"You lost, the code was {''.join(map(str, code))}.")
        HINT.chgat(1, 23, 4, curses.A_BOLD)

    HINT.addstr(3, 0, "Press any key to restart, q to quit", curses.A_BLINK)

    BOARD.refresh()
    HINT.refresh()

    if GUESS.getkey() == "q":
        stdscr.clear()
        stdscr.addstr(2, 4, "Goodbye :)")
        stdscr.refresh()
        curses.napms(500)
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


def draw_board(data: dict) -> str:
    return tabulate(
        data,
        headers="keys",
        tablefmt="pretty",
        numalign="center",
    )


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
        curses.curs_set(0)

        BOARD = curses.newwin(14, 21, 0, 0)
        HINT = curses.newwin(4, 40, 6, 22)
        GUESS = curses.newwin(1, 5, 0, 0)

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
