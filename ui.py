import curses
import textwrap
from constants import MAX_ROUNDS
from exceptions import Help, GameOver
from tabulate import tabulate


class GameUI:
    def __init__(self, stdscr: curses.window) -> None:
        self.stdscr = stdscr
        self._init_ui()

    def _init_ui(self) -> None:
        curses.curs_set(0)

        self.MAIN_Y, self.MAIN_X = (curses.LINES - 1, curses.COLS)
        self.MAIN_BEG_Y = (curses.LINES - self.MAIN_Y) // 2
        self.MAIN_BEG_X = (curses.COLS - self.MAIN_X) // 2

        self.BOARD_Y, self.BOARD_X = (14, 21)
        self.BOARD_BEG_Y = (self.MAIN_Y - self.BOARD_Y) // 2
        self.BOARD_BEG_X = (self.MAIN_X - self.BOARD_X + 1) // 2

        self.HINT_Y, self.HINT_X = (7, 40)
        self.HINT_BEG_Y = (self.MAIN_Y - self.HINT_Y) // 2
        self.HINT_BEG_X = (self.MAIN_X - self.HINT_X) // 2

        self.INPUT_Y, self.INPUT_X = (1, 5)
        self.INPUT_BEG_Y = 1
        self.INPUT_BEG_X = 1

        self.HELP_Y, self.HELP_X = (40, 45)
        self.HELP_BEG_Y = self.MAIN_BEG_Y + 1
        self.HELP_BEG_X = (self.MAIN_X - self.HELP_X + 1) // 2

        self.main_window = self.stdscr.subwin(
            self.MAIN_Y, self.MAIN_X, self.MAIN_BEG_Y, self.MAIN_BEG_X
        )

        self.board_window = curses.newwin(
            self.BOARD_Y, self.BOARD_X, self.BOARD_BEG_Y, self.BOARD_BEG_X
        )

        self.hint_window = curses.newwin(
            self.HINT_Y, self.HINT_X, self.HINT_BEG_Y, self.HINT_BEG_X
        )

        self.input_window = curses.newwin(
            self.INPUT_Y, self.INPUT_X, self.INPUT_BEG_Y, self.INPUT_BEG_X
        )

        self.help_pad = curses.newpad(self.HELP_Y, self.HELP_X)

        self.input_window.keypad(True)
        self.help_pad.keypad(True)

    def show_static_menu(self) -> None:
        title = "+MasterMind+"
        keys_help = "0-9 Guess. Enter Confirm. H Toggle help. Q quit."

        title_beg_x = (curses.COLS - len(title)) // 2
        keys_help_beg_x = (curses.COLS - len(keys_help)) // 2

        self.main_window.border("|", "|", "-", "-", "+", "+", "+", "+")

        self.stdscr.addstr(0, title_beg_x, title)
        self.stdscr.chgat(0, title_beg_x + 1, len(title) - 2, curses.A_BOLD)

        self.stdscr.addstr(curses.LINES - 1, keys_help_beg_x, keys_help)
        self.stdscr.chgat(curses.LINES - 1, keys_help_beg_x + 0, 3, curses.A_BOLD)
        self.stdscr.chgat(curses.LINES - 1, keys_help_beg_x + 11, 5, curses.A_BOLD)
        self.stdscr.chgat(curses.LINES - 1, keys_help_beg_x + 26, 1, curses.A_BOLD)
        self.stdscr.chgat(curses.LINES - 1, keys_help_beg_x + 41, 1, curses.A_BOLD)

        self.stdscr.refresh()

    def show_board(
        self, guess_pegs: list[str], feedback_pegs: list[str], current_round: int
    ) -> None:
        self.hint_window.erase()
        self.board_window.erase()
        self.input_window.erase()

        self.board_window.addstr(self.board(guess_pegs, feedback_pegs))
        self.input_window.noutrefresh()
        self.input_window.mvwin(
            self.BOARD_BEG_Y + current_round + 3, self.BOARD_BEG_X + 7
        )

        self.hint_window.noutrefresh()
        self.board_window.refresh()

    def show_hint(self, message: ValueError) -> None:
        hint_message = f"Hint: {str(message)}"
        hint_message_beg_y = (self.HINT_Y - 1) // 2
        hint_message_beg_x = (self.HINT_X - len(hint_message)) // 2

        self.hint_window.erase()

        self.hint_window.border("|", "|", "-", "-", "+", "+", "+", "+")

        self.hint_window.addstr(hint_message_beg_y, hint_message_beg_x, hint_message)
        self.hint_window.chgat(hint_message_beg_y, hint_message_beg_x, 5, curses.A_BOLD)

        self.hint_window.getkey()

    def show_help(self):
        help_content = textwrap.dedent(
            """\
                +-------------------HELP-------------------+
                |                                          |
                | - The objective is to crack a code by    |
                | creating a guess that combines numbers   |
                | within the 1 to 6 range. Ensure that     |
                | each number is used only once.           |
                |                                          |
                | - player have a maximum of 10 attempts   |
                | to break the code.                       |
                |                                          |
                | - After making a valid guess, player     |
                | will receive feedback:                   |
                |                                          |
                |  - O: Correct number and position.       |
                |  - X: Correct number, wrong position.    |
                |  - _: Number is not part of the code.    |
                |                                          |
                | - Examples:                              |
                | +------+-------+----------+              |
                | | Code | Guess | Feedback |              |
                | +------+-------+----------+              |
                | | 1234 | 1234  | OOOO     |              |
                | | 6245 | 1234  | OX__     |              |
                | +------+-------+----------+              |
                |                                          |
                | - Note: The feedback provided does not   |
                | necessarily follow the order of the code |
                | or guess (O > X > _).                    |
                |                                          |
                | - Whether player successfully break the  |
                | code or fail to do so, the game ends,    |
                | displaying a game over menu.             |
                |                                          |
                | - In either case, player have the        |
                | option to restart or exit the game.      |
                |                                          |
                | - Enjoy the game!                        |
                |                                          |
                +------------------------------------------+"""
        )

        curser_position = 0
        CURSER_POSITION_MAX = self.HELP_Y - self.MAIN_Y + 1

        self.help_pad.erase()
        self.help_pad.addstr(help_content)

        self._refresh_help_pad()

        while True:
            key = self.help_pad.getkey()

            if (
                key.upper() in ("KEY_DOWN", "J")
                and curser_position < CURSER_POSITION_MAX
            ):
                curser_position += 1

            elif key.upper() in ("KEY_UP", "K") and curser_position > 0:
                curser_position -= 1

            elif key == "KEY_PPAGE":
                curser_position = 0

            elif key == "KEY_NPAGE":
                curser_position = CURSER_POSITION_MAX

            elif key.upper() in ("Q", "H", "\n"):
                self.help_pad.erase()
                self._refresh_help_pad()
                break

            else:
                continue

            self._refresh_help_pad(curser_position)

    def _refresh_help_pad(self, position: int = 0) -> None:
        self.help_pad.refresh(
            position,
            0,
            self.HELP_BEG_Y,
            self.HELP_BEG_X,
            self.MAIN_Y - 2,
            self.HELP_BEG_X + self.HELP_X,
        )

    def show_game_over(
        self,
        code: list[int],
        guess_pegs: list[str],
        feedback_pegs: list[str],
        current_round: int,
        player_won: bool,
    ) -> None:
        if player_won:
            score = "{:02}/{}".format(MAX_ROUNDS - current_round, MAX_ROUNDS)

            header = "Congratulations!"
            message = f"You won, your score is {score}"
            bold_text_lenght = 5
        else:
            code_str = "".join(map(str, code))

            header = "Oops!"
            message = f"You lost, the code was: {code_str}"
            bold_text_lenght = 4

        footer_text = "Press any key to restart (q to quit)"

        header_beg_y = ((self.HINT_Y - 1) // 2) - 1
        header_beg_x = (self.HINT_X - len(header)) // 2

        message_beg_y = header_beg_y + 2
        message_beg_x = (self.HINT_X - len(message)) // 2

        footer_beg_y = self.MAIN_Y - 2
        footer_beg_x = (curses.COLS - len(footer_text)) // 2

        self.board_window.erase()
        self.hint_window.erase()

        self.board_window.addstr(self.board(guess_pegs, feedback_pegs), curses.A_DIM)

        self.hint_window.border("|", "|", "-", "-", "+", "+", "+", "+")

        self.hint_window.addstr(header_beg_y, header_beg_x, header, curses.A_BOLD)

        self.hint_window.addstr(message_beg_y, message_beg_x, message)
        self.hint_window.chgat(
            4,
            message_beg_x + len(message) - bold_text_lenght,
            bold_text_lenght,
            curses.A_BOLD,
        )

        self.board_window.refresh()
        self.hint_window.refresh()

        self.stdscr.addstr(footer_beg_y, footer_beg_x, footer_text, curses.A_BLINK)

        if self.stdscr.getkey().upper() == "Q":
            exit(0)

        # Clear the footer text without clearing the whole window.
        self.stdscr.addstr(footer_beg_y, footer_beg_x, " " * len(footer_text))
        self.stdscr.refresh()

    def handle_user_input(self) -> list[int]:
        guess = []
        while True:
            key = self.input_window.getkey()

            if key.isdecimal() and len(guess) < 4:
                guess.append(int(key))
                self.input_window.addch(key)

            elif key in ("KEY_BACKSPACE", "\x7f", "\b") and len(guess) > 0:
                guess.pop()
                self.input_window.delch(0, len(guess))

            elif key.upper() == "Q":
                raise GameOver

            elif key.upper() == "H":
                raise Help

            elif key == "\n":
                return guess

            else:
                continue

    @staticmethod
    def board(guess_pegs: list[str], feedback_pegs: list[str]) -> str:
        return tabulate(
            {
                "": [f"{r:02}" for r in range(1, MAX_ROUNDS + 1)],
                "Code": guess_pegs + ["...."] * (MAX_ROUNDS - len(guess_pegs)),
                "Pegs": feedback_pegs + ["...."] * (MAX_ROUNDS - len(feedback_pegs)),
            },
            headers="keys",
            tablefmt="pretty",
            numalign="center",
        )
