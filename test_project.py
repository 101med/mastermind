import pytest
from project import MasterMindGame
from project import GameOver, InvalidCode


def test_reset():
    game = MasterMindGame()
    game.reset()

    assert game.current_round == 0
    assert game.player_won == False
    assert len(game.code_pegs) == 0
    assert len(game.feedback_pegs) == 0


def test_code():
    game = MasterMindGame()

    # Validate that the generated code has the correct length and contains valid digits
    code = game.code
    assert len(code) == 4
    for digit in code:
        assert digit in range(1, 7)


def test_current_guess():
    game = MasterMindGame()

    # Test that current_guess returns the correct list
    game.code_pegs = ["1234", "5621"]
    game.current_round = 1

    assert game.current_guess == [5, 6, 2, 1]


def test_make_guess():
    game = MasterMindGame()
    game.code = [1, 2, 3, 4]

    # Test making a correct guess
    with pytest.raises(GameOver):
        game.make_guess([1, 2, 3, 4])

    assert game.player_won == True

    # Test making an incorrect guess
    game.reset()
    game.make_guess([5, 6, 2, 1])
    assert game.player_won == False
    assert game.current_round == 1


def test__validate_code():
    game = MasterMindGame()

    # Test valid code
    valid_code = [1, 2, 3, 4]
    assert game._validate_code(valid_code) == None

    # Test code with invalid length
    with pytest.raises(ValueError):
        invalid_code = [1, 2, 3]
        game._validate_code(invalid_code)

    # Test code with invalid digits
    with pytest.raises(ValueError):
        invalid_code = [0, 7, 8, 9]
        game._validate_code(invalid_code)

    # Test code with repeated digits
    with pytest.raises(ValueError):
        invalid_code = [1, 2, 2, 3]
        game._validate_code(invalid_code)


def test__feedback():
    game = MasterMindGame()
    game.code = [1, 2, 3, 4]

    # Test correct feedback
    feedback = game._feedback([1, 2, 3, 4])
    assert feedback == ["O", "O", "O", "O"]

    # Test feedback with correct digits in wrong positions
    feedback = game._feedback([4, 3, 2, 1])
    assert feedback == ["X", "X", "X", "X"]

    # Test feedback with some correct digits in correct positions
    feedback = game._feedback([1, 2, 5, 6])
    assert feedback == ["O", "O", "_", "_"]


def test_get_game_data():
    game = MasterMindGame()
    game.code_pegs = ["1234", "5678"]
    game.feedback_pegs = ["OOXX", "XXOO"]

    # Test that get_game_data returns the correct dictionary
    data = game.get_game_data()
    assert data == {
        "": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"],
        "Code": [
            "1234",
            "5678",
            "....",
            "....",
            "....",
            "....",
            "....",
            "....",
            "....",
            "....",
        ],
        "Pegs": [
            "OOXX",
            "XXOO",
            "....",
            "....",
            "....",
            "....",
            "....",
            "....",
            "....",
            "....",
        ],
    }


def test_reveal_code():
    game = MasterMindGame(cheats=True)
    game.code = [1, 2, 3, 4]

    # Test that reveal_code creates a file with the correct code
    game.reveal_code()
    with open("/tmp/mastermind_code.txt", "r") as f:
        content = f.read()
    assert content == "1234" + "\n"
