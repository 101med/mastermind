import pytest
import os
from exceptions import InvalidCode
from project import validate_code, feedback, reveal_code


def test_validate_code() -> None:
    # Valid code:
    assert validate_code([1, 2, 3, 4]) == None
    assert validate_code([4, 1, 2, 3]) == None

    # Invalid code:
    ## Repetitions
    with pytest.raises(InvalidCode):
        validate_code([1, 1, 1, 1])

    with pytest.raises(InvalidCode):
        validate_code([1, 2, 2, 3])

    ## Numbers range
    with pytest.raises(InvalidCode):
        validate_code([0, 1, 2, 3])

    with pytest.raises(InvalidCode):
        validate_code([5, 6, 7, 8])

    ## List range
    with pytest.raises(InvalidCode):
        validate_code([1])

    with pytest.raises(InvalidCode):
        validate_code([1, 2])

    with pytest.raises(InvalidCode):
        validate_code([1, 2, 3, 4, 5, 6])


def test_feedback() -> None:
    assert feedback([1, 2, 3, 4], [1, 2, 3, 4]) == ["O", "O", "O", "O"]
    assert feedback([1, 2, 4, 3], [1, 2, 3, 4]) == ["O", "O", "X", "X"]
    assert feedback([4, 3, 2, 1], [1, 2, 3, 4]) == ["X", "X", "X", "X"]
    assert feedback([5, 6, 3, 4], [1, 2, 3, 4]) == ["O", "O", "_", "_"]
    assert feedback([1, 2, 5, 3], [1, 2, 3, 4]) == ["O", "O", "X", "_"]


def test_reveal_code() -> None:
    tmpfile = os.path.join(os.environ.get("TMPDIR", "/tmp"), "mastermind_code.txt")

    code_1 = [1, 2, 3, 4]
    reveal_code(code_1)

    with open(tmpfile, "r") as f:
        assert f.read() == "1234"

    code_2 = [4, 3, 2, 1]
    reveal_code(code_2)

    with open(tmpfile, "r") as f:
        assert f.read() == "4321"
