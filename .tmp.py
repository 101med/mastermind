import curses, sys, random
from tabulate import tabulate

NUMBERS = range(1, 7)
PEGS = 4
ROUNDS = 10


def main(stdscr):
    curses.curs_set(0)

    stdscr.clear()

    stdscr.addstr("Welcome to Master Mind, a code-breaking game.", curses.A_REVERSE)
    stdscr.chgat(-1, curses.A_REVERSE)
    stdscr.chgat(0, 11, 11, curses.A_BOLD | curses.A_REVERSE)

    stdscr.refresh()

    init_windows()
    start_game(stdscr)


def start_game(stdscr) -> None:
    while True:
        code = random.sample(NUMBERS, PEGS)
        board_data = {
            "": [f"{r:02}" for r in range(1, ROUNDS + 1)],
            "pegs": ["...." for _ in range(ROUNDS)],
            "code": ["...." for _ in range(ROUNDS)],
        }

        play_game(stdscr, code, board_data)


def play_game(stdscr, code: list, data: dict) -> None:
    current_round = 0
    key_pegs = [
        "O: Correct number and position.",
        "X: Correct number, wrong position.",
        "_: Incorrect number.",
    ]

    HELP.erase()
    HELP.addstr(0, 0, "Help:", curses.A_BOLD)
    for i, item in enumerate(key_pegs, 1):
        HELP.addstr(i, 0, item)
    HELP.refresh()

    while True:
        BOARD.erase()
        HINT.erase()
        GUESS.erase()

        BOARD.addstr(draw_board(data))
        GUESS.mvwin(current_round + (3 + 2), 15)

        BOARD.refresh()
        HINT.refresh()
        GUESS.refresh()

        if current_round >= 10:
            game_over(stdscr, won=False, code="".join(map(str, code)))
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
                    game_over(stdscr, won=False, code="".join(map(str, code)))
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

                HINT.addstr("Hint: " + str(ve))
                HINT.chgat(0, 0, 5, curses.A_BOLD)

                HINT.refresh()
                GUESS.refresh()

        data["pegs"][current_round] = keys_peg(code, guess)
        data["code"][current_round] = "".join(map(str, guess))

        if guess == code:
            game_over(stdscr, won=True, end_round=current_round)
            return

        else:
            current_round += 1


def keys_peg(code: list, guess: list) -> str:
    pegs = []
    for i in range(PEGS):
        if guess[i] == code[i]:
            pegs.append("O")
        elif guess[i] in code:
            pegs.append("X")
        else:
            pegs.append("_")

    return "".join(
        sorted(pegs, key=lambda item: ("O" not in item, "X" not in item, item))
    )


def validate_guess(s) -> None:
    if len(s) != 4:
        raise ValueError("Type in 4 numbers.")

    for n in s:
        if not n in range(1, 7):
            raise ValueError("Use numbers between 1 to 6.")

    if len(set(s)) != 4:
        raise ValueError("Don't repeat numbers.")


def draw_board(data: dict) -> str:
    return tabulate(
        data,
        headers="keys",
        tablefmt="pretty",
        numalign="center",
    )


def init_windows() -> None:
    global BOARD, HELP, HINT, GUESS

    BOARD = curses.newwin(14, 21, 2, 1)
    HELP = curses.newwin(5, 40, 3, 23)
    HINT = curses.newwin(6, 40, 8, 23)
    GUESS = curses.newwin(1, 5)

    GUESS.keypad(True)


def game_over(stdscr, won=False, code="XXXX", end_round=9) -> None:
    HINT.erase()

    BOARD.bkgd(curses.A_DIM)
    if won:
        HINT.addstr(0, 0, "Congratulations!", curses.A_BOLD)
        HINT.addstr(1, 0, f"You won, your score is {ROUNDS - end_round}/{ROUNDS}.")
    else:
        HINT.addstr(0, 0, "Oops!", curses.A_BOLD)
        HINT.addstr(1, 0, f"You lost, the code was {''.join(map(str, code))}.")
        HINT.chgat(1, 23, 4, curses.A_BOLD)

    HINT.addstr(4, 0, "Press any key to restart, q to quit", curses.A_BLINK)

    BOARD.refresh()
    HINT.refresh()

    if GUESS.getkey() == "q":
        stdscr.clear()
        stdscr.addstr((curses.LINES - 1) // 2, (curses.COLS - 10) // 2, "Goodbye :)")
        stdscr.refresh()
        curses.napms(500)
        sys.exit()

    BOARD.bkgd(curses.A_NORMAL)


if __name__ == "__main__":
    curses.wrapper(main)
