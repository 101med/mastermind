#!/usr/bin/env python3

import argparse
import curses
import os
import random
from constants import MAX_ROUNDS, NUM_PEGS, POSSIBLE_DIGITS
from exceptions import Help, InvalidCode, GameOver
from ui import GameUI


def main(stdscr):
    ui = GameUI(stdscr)
    ui.show_static_menu()

    while True:
        code = random.sample(POSSIBLE_DIGITS, NUM_PEGS)
        guess_pegs = []
        feedback_pegs = []
        current_round = 0
        player_won = False

        if args.cheats:
            reveal_code(code)

        while True:
            try:
                ui.show_board(guess_pegs, feedback_pegs, current_round)
                guess = ui.handle_user_input()

                validate_code(guess)

                guess_pegs.append("".join(map(str, guess)))
                feedback_pegs.append("".join(feedback(code, guess)))

                if code == guess:
                    player_won = True
                    raise GameOver

                elif current_round + 1 < MAX_ROUNDS:
                    current_round += 1

                else:
                    raise GameOver

            except InvalidCode as e:
                ui.show_hint(e)

            except Help:
                ui.show_help()

            except GameOver:
                ui.show_game_over(
                    code, guess_pegs, feedback_pegs, current_round, player_won
                )
                break


def validate_code(code: list[int]) -> None:
    if len(code) != NUM_PEGS:
        raise InvalidCode(f"Enter exactly {NUM_PEGS} numbers.")

    for n in code:
        if n not in POSSIBLE_DIGITS:
            raise InvalidCode("Use numbers between 1 and 6.")

    if len(set(code)) != NUM_PEGS:
        raise InvalidCode("Do not repeat numbers.")


def feedback(code: list[int], guess: list[int]) -> list[str]:
    pegs = []
    for i in range(NUM_PEGS):
        if guess[i] == code[i]:
            pegs.append("O")
        elif guess[i] in code:
            pegs.append("X")
        else:
            pegs.append("_")

    pegs.sort(key=lambda item: ("O" not in item, "X" not in item, item))

    return pegs


def reveal_code(code: list[int]) -> None:
    tmpfile = os.path.join(os.environ.get("TMPDIR", "/tmp"), "mastermind_code.txt")

    with open(tmpfile, "w") as f:
        f.write("".join(map(str, code)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Classic board-game MasterMind in the terminal."
    )
    parser.add_argument(
        "-c",
        "--cheats",
        help="store game's code in $TMPDIR/mastermind.txt",
        action="store_true",
    )
    args = parser.parse_args()

    try:
        stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        main(stdscr)
    finally:
        if "stdscr" in locals():
            stdscr.keypad(False)

        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()
