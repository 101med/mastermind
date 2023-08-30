import curses
import sys
import random
from tabulate import tabulate

NUMBERS = range(1, 7)
PEGS = 4
ROUNDS = 10


def main() -> None:
    stdscr.clear()
    ...
    stdscr.refresh()

    start_game()


def start_game() -> None:
    while True:
        code = random.sample(NUMBERS, PEGS)
        board_data = {
            "": [f"{r:02}" for r in range(1, ROUNDS + 1)],
            "pegs": ["...." for _ in range(ROUNDS)],
            "code": ["...." for _ in range(ROUNDS)],
        }

        play_game(code, board_data)


def play_game(code: list, data: dict) -> None:
    current_round = 0

    while True:
        BOARD.erase()
        GUESS.erase()

        BOARD.addstr(draw_board(data))
        GUESS.mvwin(current_round + 3, 14)

        BOARD.refresh()
        GUESS.refresh()

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
                ...

        data["pegs"][current_round] = keys_peg(code, guess)
        data["code"][current_round] = "".join(map(str, guess))

        current_round += 1


def game_over(won=False, code=[1, 2, 3, 4], r=9) -> None:
    ...


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
            raise ValueError("Use numbers between\n1 and 6.")

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
    try:
        stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        BOARD = curses.newwin(14, 21, 0, 0)
        GUESS = curses.newwin(1, 5, 0, 0)

        GUESS.keypad(True)

        main()
    finally:
        if "GUESS" in locals():
            GUESS.keypad(False)

        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()
