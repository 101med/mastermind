# MASTERMIND
#### Video Demo: [Here](https://yewtu.be)
#### Description:
This is a text-based implementation of the classic board game Mastermind.
The game is created using Python and the `curses` library.
It's my final project for Harvard's CS50's Introduction to Programming with Python.

## Project Structure

```plaintext
mastermind/
├── requirements.txt
├── constants.py
├── exceptions.py
├── ui.py
├── project.py
├── test_project.py
└── README.md
```

- `requirements.txt`: List of dependencies needed to run the game.
- `constants.py`: Game-specific constants.
- `exceptions.py`: Custom exceptions used in the game.
- `ui.py`: User interface components for the game.
- `project.py`: Core logic and game implementation.
- `test_project.py`: Unit tests for game functions.
- `README.md`: You are reading this file!

`project.py` and `ui.py` work together to accomplish the project's goal. Here's a brief overview of what each of these files does:

#### `project.py`

- The main entry point of the game.
- Defines the `main` function, which controls the game loop.
- Initializes the game, generates a random secret code, and sets up the user interface using the `GameUI` class from `ui.py`.
- Validates the code entered by the player, provides feedback, and manages win or loss conditions.
- Calls functions to reveal the code if cheats are enabled.

#### `ui.py`

- Contains the `GameUI` class, responsible for creating and managing the user interface using `curses`.
- Sets up windows for different parts of the game, such as the main board, input, hint, help screens and yx coordinates that helps center theses elements.
- Provides methods to display the game's static menu, game board, feedback, hints, and game-over screens.
- Handles user input for guessing and navigating the help screen.
- Defines a `board` method to format and display the game board.

### How to Play
- **Install Dependencies**: Start by installing the required library `tablaute` using pip:

   ```bash
   $ pip install -r requirements.txt
   ```

- **Launch the Game**: You can start the game in two ways, depending on your preference:
   - Using Python:

     ```bash
     $ python project.py
     ```

   - Or, make the script executable and run it directly:

     ```bash
     $ ./project.py
     ```

- **Command-Line Flags**: The game offers two command-line flags for customization:
   - `-h` or `--help`.
   - `-c` or `--cheats`.

     ```bash
     $ python project.py -h
     ```

     ```plaintext
     usage: project.py [-h] [-c]

     Classic board-game MasterMind in the terminal.

     options:
       -h, --help    show this help message and exit
       -c, --cheats  store the game's code in $TMPDIR/mastermind_code.txt
     ```

- **Objective**: The objective is to crack a code by guessing a combination of numbers.

- **Rules**:
   - You have a maximum of 10 attempts to guess the secret code.
   - Each guess should consist of four numbers, with each number between 1 and 6.
   - You cannot repeat the same number in a single guess.

- **Feedback**:
   - After making a guess, you'll receive feedback in the form of pegs.
   - Feedback pegs are represented as:
     - "O": Correct number in the correct position.
     - "X": Correct number in the wrong position.
     - "_": Number is not part of the code.
   - The order of feedback pegs doesn't necessarily match the order of your guess.

- **Winning**: If your guess matches the secret code ("OOOO" as feedback), you win the game.

- **Losing**: You lose the game if:
   - You've used all 10 attempts without cracking the code.
   - You choose to quit the game.

- **Controls**:
   - Enter four numbers (1-6) for your guess and press Enter to confirm.
   - Use the backspace or delete key to correct your guess.
   - Press "H" to toggle the help screen.
   - Press "Q" to quit the game.

- **Game Over Menu**: At the end of the game (win or lose), you'll have the option to restart or exit the game.

- **Cheats (Optional)**: If you enable cheats, the game's secret code will be stored in `$TMPDIR/mastermind_code.txt`, start the game with the `-c` or `--cheats` flags.

Enjoy! and... This was CS50P.
