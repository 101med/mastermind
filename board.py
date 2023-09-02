import random
from tabulate import tabulate

NUMBERS = range(1, 7)
PEGS = 4
ROUNDS = 10


class Board:
    """Represents the game board for a Mastermind-style game."""

    def __init__(self) -> None:
        """Initialize the game board."""
        self.reset()

    def reset(self) -> None:
        """Reset board's values to start a new game."""
        self._code = random.sample(NUMBERS, PEGS)
        self._rounds = tuple(f"{r:02}" for r in range(1, ROUNDS + 1))
        self._pegs = ["...."] * ROUNDS
        self._guesses = ["...."] * ROUNDS
        self._round = 0

    @property
    def code(self) -> list[int]:
        """Get the secret code as a list of integers."""
        return self._code

    @property
    def pegs(self) -> list[str]:
        """Get the list of feedback pegs for each round."""
        return self._pegs

    @property
    def guesses(self) -> list[str]:
        """Get the list of player guesses for each round."""
        return self._guesses

    @property
    def round(self) -> int:
        """Get the current round number."""
        return self._round

    @property
    def rounds(self) -> tuple[str]:
        """Get the formatted round numbers as a tuple of strings."""
        return self._rounds

    def __key_pegs(self, guess) -> str:
        """
        Calculate the key pegs for a given guess.

        Returns:
            str: Key pegs:
                - "O": correct number and spot.
                - "X": correct number wrong spot.
                - "_": Invalid number.

        Example:
            code: [1,2,3,4]
            guess: [4,6,3,1]
            output: "OXX_"

        """
        pegs = [
            "O" if guess[n] == self._code[n] else "X" if guess[n] in self._code else "_"
            for n in range(PEGS)
        ]

        pegs.sort(key=lambda peg: ("O" not in peg, "X" not in peg, peg))

        return "".join(pegs)

    @property
    def current_guess(self) -> str:
        """Get the current player's guess for the current round."""
        return self._guesses[self._round]

    @current_guess.setter
    def current_guess(self, s: str) -> None:
        """
        Set the current player's guess for the current round.

        Args:
            s (str): A string representing the player's guess.

        Raises:
            ValueError: If the guess is not valid.
        """
        guess = [int(n) for n in s if n.isdecimal()]

        if len(guess) != len(s):
            raise ValueError("Numbers only")

        if len(guess) != PEGS:
            raise ValueError("Enter exactly 4 numbers.")

        for n in guess:
            if n not in NUMBERS:
                raise ValueError("Use numbers between 1 and 6.")

        if len(set(guess)) != PEGS:
            raise ValueError("Do not repeat numbers.")

        self._guesses[self.round] = "".join(map(str, guess))
        self._pegs[self.round] = self.__key_pegs(guess)

    def next_round(self) -> None:
        """Move to the next round of the game if available."""
        if self._round < 9:
            self._round += 1
        else:
            raise Exception("Game Over.")

    def draw(self) -> str:
        """
        Generate a formatted representation of the game board.

        Returns:
            +----+------+------+
            |    | pegs | code |
            +----+------+------+
            | 01 | .... | .... |
            | 02 | .... | .... |
            | 03 | .... | .... |
            | 04 | .... | .... |
            | 05 | .... | .... |
            | 06 | .... | .... |
            | 07 | .... | .... |
            | 08 | .... | .... |
            | 09 | .... | .... |
            | 10 | .... | .... |
            +----+------+------+
        """
        return tabulate(
            {
                "": self._rounds,
                "pegs": self._pegs,
                "code": self._guesses,
            },
            headers="keys",
            tablefmt="pretty",
            numalign="center",
        )
