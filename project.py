import curses, sys, random
from tabulate import tabulate
from pyfiglet import Figlet


def main():
    play_game()


def play_game() -> None:
    ROUNDS = 10

    while True:
        code = random.sample(range(1, 7), 4)
        cheat(code)
        data = {
            "": [f"{r:02}" for r in range(1, ROUNDS + 1)],
            "pegs": ["...." for _ in range(ROUNDS)],
            "code": ["...." for _ in range(ROUNDS)],
        }

        rounds(code, data)


def cheat(code) -> None:
    with open("/tmp/mastermind.txt", "w") as f:
        f.write("".join(map(str, code)) + "\n")


def rounds(code, data) -> None:
    ROUNDS = 10

    def game_over(win=False) -> None:
        hint_window.clear()
        if win:
            hint_window.addstr(0, 0, "Congratulations!", curses.A_BOLD)
            hint_window.addstr(1, 0, f"You won, your score is {ROUNDS - r}/{ROUNDS}.")
        else:
            hint_window.addstr(0, 0, "Oops!", curses.A_BOLD)
            hint_window.addstr(
                1, 0, f"You lost, the code was {''.join(map(str, code))}."
            )
            hint_window.chgat(1, 23, 4, curses.A_BOLD)

        hint_window.addstr(4, 0, "Press any key to restart, q to quit", curses.A_BLINK)

        hint_window.noutrefresh()

        curses.doupdate()

        if guess_window.getkey() == "q":
            stdscr.clear()
            stdscr.addstr(
                (curses.LINES - 1) // 2, (curses.COLS - 10) // 2, "Goodbye :)"
            )
            stdscr.refresh()

            curses.napms(500)
            sys.exit()

    stdscr.clear()

    stdscr.addstr(1, 23, "Pegs key:", curses.A_BOLD)
    stdscr.addstr(2, 23, "O: Correct number and position.")
    stdscr.addstr(3, 23, "X: Correct number, wrong position.")
    stdscr.addstr(4, 23, "_: Incorrect number.")
    stdscr.addstr(6, 23, "Help:", curses.A_BOLD)
    stdscr.addstr(7, 23, "Return: confirm guess.")
    stdscr.addstr(8, 23, "q: Restart or quit game.")

    stdscr.noutrefresh()

    r = 0
    while True:
        board_window.clear()
        hint_window.clear()
        guess_window.clear()

        board_window.addstr(0, 0, draw_board(data))
        guess_window.mvwin(r + 4, 15)

        board_window.noutrefresh()
        hint_window.noutrefresh()
        guess_window.refresh()

        curses.doupdate()

        guess = []
        while True:
            try:
                key = guess_window.getkey()

                if key.isdecimal() and len(guess) < 4:
                    guess.append(int(key))

                elif key == "KEY_BACKSPACE" and len(guess) > 0:
                    guess.pop()

                elif key == "\n":
                    validate_guess(guess)
                    break

                elif key == "q":
                    game_over(win=False)
                    return

                else:
                    continue

                guess_window.clear()
                guess_window.addstr("".join(map(str, guess)))
                guess_window.refresh()

            except ValueError as ve:
                guess.clear()

                hint_window.clear()
                guess_window.clear()

                hint_window.addstr(0, 0, "Hint:", curses.A_BOLD)
                hint_window.addstr(1, 0, str(ve))

                hint_window.noutrefresh()
                guess_window.refresh()

                curses.doupdate()

        data["pegs"][r] = key_pegs(code, guess)
        data["code"][r] = "".join(map(str, guess))

        if code == guess:
            game_over(win=True)
            return

        elif r >= 9:
            game_over(win=False)
            return
        else:
            r += 1


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


if __name__ == "__main__":
    try:
        stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        # curses.curs_set(0)

        board_window = stdscr.subwin(15, 21, 1, 1)
        hint_window = stdscr.subwin(5, 40, 10, 23)
        guess_window = curses.newwin(1, 5)

        guess_window.keypad(True)

        main()

    finally:
        if "guess_window" in locals():
            guess_window.keypad(False)

        curses.echo()
        curses.nocbreak()
        # curses.curs_set(1)

        curses.endwin()
