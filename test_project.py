import pytest
from project import ROUNDS, keys_peg, validate_guess, draw_board


def main():
    test_keys_peg()
    test_validate_guess()
    test_draw_board()


def test_keys_peg():
    assert keys_peg([1, 2, 3, 4], [1, 2, 3, 4]) == "OOOO"
    assert keys_peg([1, 2, 3, 4], [4, 3, 2, 1]) == "XXXX"
    assert keys_peg([1, 2, 3, 4], [5, 2, 3, 4]) == "OOO_"
    assert keys_peg([1, 2, 3, 4], [1, 5, 6, 3]) == "OX__"


def test_validate_guess():
    with pytest.raises(ValueError):
        validate_guess([1, 2, 3])  # Less than 4 numbers

    with pytest.raises(ValueError):
        validate_guess([1, 2, 7, 4])  # Number out of range

    with pytest.raises(ValueError):
        validate_guess([1, 2, 2, 3])  # Repetition


def test_draw_board():
    """
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

    board_data = {
        "": [f"{r:02}" for r in range(1, ROUNDS + 1)],
        "pegs": ["...." for _ in range(ROUNDS)],
        "code": ["...." for _ in range(ROUNDS)],
    }

    assert board_data[""] == [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
    ]
    assert board_data["pegs"] == [
        "....",
        "....",
        "....",
        "....",
        "....",
        "....",
        "....",
        "....",
        "....",
        "....",
    ]
    assert board_data["code"] == [
        "....",
        "....",
        "....",
        "....",
        "....",
        "....",
        "....",
        "....",
        "....",
        "....",
    ]

    board = draw_board(board_data)

    raw_board = "+----+------+------+\n|    | pegs | code |\n+----+------+------+\n| 01 | .... | .... |\n| 02 | .... | .... |\n| 03 | .... | .... |\n| 04 | .... | .... |\n| 05 | .... | .... |\n| 06 | .... | .... |\n| 07 | .... | .... |\n| 08 | .... | .... |\n| 09 | .... | .... |\n| 10 | .... | .... |\n+----+------+------+"

    assert board == raw_board

    assert len(board.splitlines()) == 14

    for i in board.splitlines():
        assert len(i) == 20


if __name__ == "__main__":
    main()
