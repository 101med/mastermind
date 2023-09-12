#!/usr/bin/env python3

import curses


class Screen:
    def __init__(self, stdscr: curses.window, lines: int, cols: int) -> None:
        self.stdscr = stdscr
        self.LINES = lines
        self.COLS = cols


class Window(Screen):
    def __init__(
        self, stdscr: curses.window, lines: int, cols: int, y=None, x=None
    ) -> None:
        super().__init__(stdscr, lines, cols)

        self.Y = y if y is not None else ((curses.LINES - 1) - self.LINES) // 2
        self.X = x if x is not None else (curses.COLS - self.COLS) // 2
        self.window = curses.newwin(self.LINES, self.COLS, self.Y, self.X)

    @property
    def border(self) -> list[str]:
        return ["|", "|", "-", "-", "+", "+", "+", "+"]


class Pad(Screen):
    def __init__(self, stdscr: curses.window, lines: int, cols: int) -> None:
        super().__init__(stdscr, lines, cols)
        self.window = curses.newwin(self.LINES, self.COLS)


class BoardWindow(Window):
    def __init__(self, stdscr: curses.window, lines: int, cols: int) -> None:
        super().__init__(stdscr, lines, cols)

    def show_board(self) -> None:
        ...

    def _draw(self) -> str:
        ...


class InputWindow(Window):
    def __init__(self, stdscr: curses.window, lines: int, cols: int) -> None:
        super().__init__(stdscr, lines, cols)

    def handel_input(self) -> list[int]:
        ...


class HintWindow(Window):
    def __init__(self, stdscr: curses.window, lines: int, cols: int) -> None:
        super().__init__(stdscr, lines, cols)

    def show_message(self, message: ValueError) -> None:
        ...

    def show_game_over(self) -> None:
        ...


class HelpPad(Pad):
    def __init__(self, stdscr: curses.window, lines: int, cols: int) -> None:
        super().__init__(stdscr, lines, cols)

    def scroll(self) -> None:
        ...


def main(stdscr):
    MAIN = Window(stdscr, lines=curses.LINES - 1, cols=curses.COLS)
    BOARD = BoardWindow(stdscr, lines=15, cols=21)
    HINT = HintWindow(stdscr, lines=7, cols=40)
    HELP = HelpPad(stdscr, lines=40, cols=46)
    INPUT = InputWindow(stdscr, lines=1, cols=5)
    MAIN.window.border(*MAIN.border)
    BOARD.window.border(*BOARD.border)
    HINT.window.border(*MAIN.border)
    INPUT.window.bkgd(curses.A_REVERSE)
    MAIN.window.refresh()
    BOARD.window.refresh()
    HINT.window.refresh()
    INPUT.window.getch()


if __name__ == "__main__":
    curses.wrapper(main)
