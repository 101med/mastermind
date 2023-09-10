#!/usr/bin/env python3

import curses
import textwrap


def main():
    init_interface()
    show_help_menu()


def init_interface() -> None:
    title_text = "+MasterMind+"
    instructions_text = "0-9 Guess. Enter Confirm. H Toggle help. Q quit."

    title_text_beg_x = (curses.COLS - len(title_text)) // 2
    instructions_text_beg_x = (curses.COLS - len(instructions_text)) // 2

    MAIN.border("|", "|", "-", "-", "+", "+", "+", "+")

    stdscr.addstr(0, title_text_beg_x, title_text)
    stdscr.chgat(0, title_text_beg_x + 1, len(title_text) - 2, curses.A_BOLD)

    stdscr.addstr(curses.LINES - 1, instructions_text_beg_x, instructions_text)
    stdscr.chgat(curses.LINES - 1, instructions_text_beg_x + 0, 3, curses.A_BOLD)
    stdscr.chgat(curses.LINES - 1, instructions_text_beg_x + 11, 5, curses.A_BOLD)
    stdscr.chgat(curses.LINES - 1, instructions_text_beg_x + 26, 1, curses.A_BOLD)
    stdscr.chgat(curses.LINES - 1, instructions_text_beg_x + 41, 1, curses.A_BOLD)

    stdscr.refresh()


def show_help_menu() -> None:
    help_menu_text = textwrap.dedent(
        """\
+-------------------Help-------------------+
| Objective:                               |
| ----------                               |
| - Your aim is to guess a 4-digit code in |
| 10 turns or less.                        |
|                                          |
| Code Parameters:                         |
| ----------------                         |
| - The code consists of four unique       |
| numbers between 1 and 6.                 |
|                                          |
| Examples:                                |
| - Valid Codes: 1234, 3456, 4312, etc.    |
| - Invalid Codes: 0123, 1111, 6789, etc.  |
|                                          |
| Turns:                                   |
| ------                                   |
| - You have a maximum of 10               |
| turns to guess the code.                 |
|                                          |
| Making a Guess:                          |
| ---------------                          |
| - In each turn, use the following        |
| keyboard keys:                           |
|                                          |
|   - 0-9: Enter a code combination.       |
|   - Return/Enter: Confirm your guess.    |
|   - q: Quit or restart the game.         |
|                                          |
| Feedback:                                |
| ---------                                |
| - After each guess, you'll receive       |
| feedback:                                |
|                                          |
|   - O: Correct number and position.      |
|   - X: Correct number, wrong position.   |
|   - _: Wrong number.                     |
|                                          |
| Examples:                                |
| +--------+-------+----------+            |
| | Code   | Guess | Feedback |            |
| +--------+-------+----------+            |
| | 1234   | 1234  | OOOO     |            |
| | 1234   | 1243  | OOXX     |            |
| | 1234   | 1256  | OX__     |            |
| +--------+-------+----------+            |
|                                          |
| Winning:                                 |
| --------                                 |
| - Successfully guessing the 4-digit code |
| within 10 turns results in a win.        |
|                                          |
| - Failing to do so means you lose, and   |
| the correct code is revealed.            |
|                                          |
| - You will be prompted to either restart |
| the game or quit.                        |
+------------------------------------------+"""
    )
    headers_coordinate = (
        (0, 20, 4),
        (1, 1, 11),
        (6, 1, 17),
        (15, 1, 7),
        (20, 1, 16),
        (29, 1, 10),
        (47, 1, 9),
    )
    curser_position = 0

    HELP.erase()
    HELP.addstr(help_menu_text)

    for header_coordinate in headers_coordinate:
        HELP.chgat(*header_coordinate, curses.A_BOLD)

    HELP.refresh(0, 0, 1, HELP_BEG_X, MAIN_Y - 2, HELP_BEG_X + HELP_X)

    while True:
        key = HELP.getkey()

        if key.upper() in ("KEY_DOWN", "J") and curser_position < (HELP_Y - MAIN_Y - 1):
            curser_position += 1

        elif key.upper() in ("KEY_UP", "K") and curser_position > 0:
            curser_position -= 1

        elif key.upper() in ("Q", "H"):
            HELP.erase()
            HELP.noutrefresh(0, 0, 1, HELP_BEG_X, MAIN_Y - 2, HELP_BEG_X + HELP_X)
            break

        elif key == "KEY_PPAGE":
            curser_position = 0

        elif key == "KEY_NPAGE":
            curser_position = HELP_Y - MAIN_Y - 1

        else:
            continue

        HELP.refresh(curser_position, 0, 1, HELP_BEG_X, MAIN_Y - 2, HELP_BEG_X + HELP_X)


if __name__ == "__main__":
    try:
        stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        MAIN_Y, MAIN_X = (curses.LINES - 1, curses.COLS)
        MAIN_BEG_Y = (curses.LINES - MAIN_Y) // 2
        MAIN_BEG_X = (curses.COLS - MAIN_X) // 2
        MAIN = stdscr.subwin(MAIN_Y, MAIN_X, MAIN_BEG_Y, MAIN_BEG_X)

        HELP_Y, HELP_X = (61, 45)
        HELP_BEG_Y = (MAIN_Y - HELP_Y + 1) // 2
        HELP_BEG_X = (MAIN_X - HELP_X + 1) // 2
        HELP = curses.newpad(HELP_Y, HELP_X)

        HELP.keypad(True)

        main()
    finally:
        if "HELP" in locals():
            HELP.keypad(False)

        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()
