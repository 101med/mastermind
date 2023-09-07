import pytest
from project import *

invalid_code = [
    # 0 or numbers begger then 6
    [0, 1, 2, 3],
    [6, 7, 8, 9],
    [1, 2, 3, 7],
    # Repeating numbers
    [1, 1, 1, 1],
    [2, 2, 2, 2],
    [1, 2, 3, 3],
    # Wrong lenght
    [1],
    [1, 2],
    [1, 2, 3],
]

@pytest.mark.parametrize("code", invalid_code)
def test_invalid_feedback(code):
    board = Board()
    with pytest.raises(InvalidCode):
        board.feedback(code)

def test_feedback():
    board = Board()
    board.code = [1, 2, 3, 4]

    # Valid code.
    assert board.feedback([1, 2, 3, 4]) == ["O", "O", "O", "O"]
    assert board.feedback([5, 2, 3, 4]) == ["O", "O", "O", "_"]
    assert board.feedback([4, 3, 2, 1]) == ["X", "X", "X", "X"]
