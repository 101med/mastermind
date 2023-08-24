import curses, random, sys
from pyfiglet import Figlet
from tabulate import tabulate


def main(stdscr) -> None:
    curses.curs_set(0)
    y, x = stdscr.getmaxyx()

    start_menu(stdscr)

    board_window = curses.newwin(15, 21, (y - 15) // 2, (x - (21 + 1 + 38)) // 2)

    board_window_y, board_window_x = board_window.getbegyx()

    help_window = curses.newwin(12, 38, board_window_y, board_window_x + 22)
    hint_window = curses.newwin(3, 38, board_window_y + 16, board_window_x + 22)
    guess_window = curses.newwin(1, 5)

    guess_window.keypad(True)

    play_game(stdscr, board_window, help_window, hint_window, guess_window)


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

    if stdscr.getkey() == "q":
        message = "Goodbye :)"

        stdscr.clear()
        stdscr.addstr((y - 1) // 2, (x - len(message)) // 2, message)
        stdscr.refresh()
        curses.napms(1000)
        sys.exit()

    stdscr.clear()
    stdscr.refresh()


def play_game(stdscr, board_window, help_window, hint_window, guess_window) -> None:
    ROUNDS = 10
    y, x = stdscr.getmaxyx()
    rules = [
        "O: Correct number and position.",
        "X: Correct number, wrong position.",
        "_: Incorrect number.",
    ]
    keys = ["Return: confirm guess.", "q: restart or quit."]

    def game_over(win=False) -> None:
        clear_windows(board_window, help_window, hint_window)

        if win:
            help_window.addstr(0, 0, "Congratulation!", curses.A_BOLD)
            help_window.addstr(1, 0, f"You won, your score is {(10 - round):02}/10.")

        else:
            help_window.addstr(0, 0, "Oops!", curses.A_BOLD)
            help_window.addstr(
                1, 0, f"You lost, the code was {''.join(map(str, code))}."
            )

        help_window.addstr(3, 0, "Press any key to restart, q to quit", curses.A_BLINK)
        board_window.addstr(draw_board(board), curses.A_DIM)

        refresh_windows(board_window, help_window, hint_window)

        if help_window.getkey() == "q":
            message = "Goodbye :)"

            stdscr.clear()
            stdscr.addstr((y - 1) // 2, (x - len(message)) // 2, message)
            stdscr.refresh()
            curses.napms(1000)
            sys.exit()

    while True:
        code = random.sample(range(1, 7), 4)
        cheat(code)
        board = {
            "": [f"{r:02}" for r in range(1, ROUNDS + 1)],
            "pegs": ["...." for _ in range(ROUNDS)],
            "code": ["...." for _ in range(ROUNDS)],
        }

        help_window_x = help_window.getmaxyx()[1]

        help_window.clear()
        help_window.addstr(1, (help_window_x - 5) // 2, "Help:", curses.A_BOLD)

        help_window.addstr(2, (help_window_x - 5) // 2, "Keys:", curses.A_BOLD)
        for k, key in enumerate(keys, 3):
            help_window.addstr(k, (help_window_x - len(key)) // 2, key)

        help_window.addstr(6, (help_window_x - 5) // 2, "Pegs:", curses.A_BOLD)
        for r, rule in enumerate(rules, 7):
            help_window.addstr(r, (help_window_x - len(rule)) // 2, rule)

        help_window.box()

        help_window.refresh()

        for round in range(ROUNDS):
            board_window.clear()
            board_window.addstr(draw_board(board))
            board_window.refresh()

            guess_window.clear()
            guess_window.mvwin(
                board_window.getbegyx()[0] + 3 + round, board_window.getbegyx()[1] + 14
            )

            hint_window.clear()
            hint_window.refresh()

            guess = []
            while True:
                try:
                    key = guess_window.getkey()

                    if key.isdecimal() and len(guess) < 4:
                        guess.append(int(key))

                    elif key == "KEY_BACKSPACE" and len(guess) > 0:
                        guess.pop()

                    elif key == "q":
                        break

                    elif key == "\n":
                        validate_guess(guess)
                        break

                    else:
                        continue

                    guess_window.clear()
                    guess_window.addstr("".join(map(str, guess)))
                    guess_window.refresh()

                except ValueError as ve:
                    guess.clear()

                    clear_windows(hint_window, guess_window)

                    hint_window.addstr(0, 0, "Hint:", curses.A_BOLD)
                    hint_window.addstr(1, 0, str(ve))

                    refresh_windows(hint_window, guess_window)

            if key == "q":
                game_over()
                break

            board["pegs"][round] = key_pegs(code, guess)
            board["code"][round] = "".join(map(str, guess))

            if guess == code:
                game_over(win=True)
                break


if __name__ == "__main__":
    curses.wrapper(main)
