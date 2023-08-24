import curses, random, sys
from pyfiglet import Figlet
from tabulate import tabulate


def main(stdscr) -> None:
    start_menu(stdscr)
    ...


def cheat(code: list) -> None:
    with open("/tmp/mastermind.txt", "w") as f:
        f.write("".join(map(str, code)) + "\n")


def clear_windows(*windows) -> None:
    for w in windows:
        w.clear()


def refresh_windows(*windows) -> None:
    for w in windows:
        w.refresh()


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


def key_pegs(code: list, guess: list) -> str:
    PEGS = 4
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


def exit_game(stdscr) -> None:
    y, x = stdscr.getmaxyx()
    message = "Goodbye :)"

    curses.curs_set(0)

    if stdscr.getkey() == "q":
        stdscr.clear()
        stdscr.addstr((y - 1) // 2, (x - len(message)) // 2, message)
        stdscr.refresh()
        curses.napms(1000)
        sys.exit()

    curses.curs_set(1)


def start_menu(stdscr) -> None:
    y, x = stdscr.getmaxyx()
    TITLE: list = Figlet("rectangles").renderText("MasterMind").splitlines()
    TITLE_Y, TITLE_X = (6, 43)
    rules = [
        "1. Guess a 4-digit number from 1 to 6.",
        "2. Unique digits for each combination.",
        "3. 10 attempts only to crack the code.",
    ]
    message = "Press any key to start, q to quit"

    stdscr.clear()

    for i, item in enumerate(TITLE):
        stdscr.addstr((((y - 1) // 2) - (12 // 2)) + i, (x - len(item)) // 2, item)

    current_y, current_x = stdscr.getyx()
    stdscr.addstr(current_y + 1, current_x - TITLE_X, "Rules:", curses.A_BOLD)

    current_y = stdscr.getyx()[0]
    for r, rule in enumerate(rules, 1):
        stdscr.addstr(current_y + r, (x - len(rule)) // 2, rule)

    current_y = stdscr.getyx()[0]
    stdscr.addstr(current_y + 3, (x - len(message)) // 2, message, curses.A_BLINK)

    stdscr.refresh()

    exit_game(stdscr)


def play_game(stdscr, board_window, help_window, hint_window, guess_window) -> None:
    ...


if __name__ == "__main__":
    curses.wrapper(main)
