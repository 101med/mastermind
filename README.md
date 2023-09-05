# Curses Mastermind

#### Video Demo:  <URL HERE>

#### Description:

# Mastermind Game in Python with Curses

## Introduction

This project is an implementation of the classic code-breaking board game, Mastermind, using Python with the built-in library, curses. In this README, we will discuss how the code works and why certain design choices were made.

## Project Contents

- [Project Contents](#project-contents)
- [Project Structure](#project-structure)
- [Game Initialization](#game-initialization)
- [Feedback Logic](#feedback-logic)
- [Board Class](#board-class)
  - [Data Property](#data-property)
  - [Draw Method](#draw-method)
  - [Validate Code Method](#validate-code-method)
- [How to Play](#how-to-play)
  - [Install Requirements](#install-requirements)
  - [Play The Game](#play-the-game)
  - [Feedback Pegs](#feedback-pegs)
  - [Valid Guesses](#valid-guesses)
  - [Invalid Guesses](#invalid-guesses)
  - [Cheats (Optional)](#cheats-optional)
- [Key Takeaways](#key-takeaways)

This project consists of two main files:

1. **`project.py`**: This is the main Python script that runs the Mastermind game using the curses library. It handles game logic, user interaction, and gameplay. Key functions and methods within this file include:

   - `main()`: The main entry point of the program.
   - `play_game(...)`: Coordinates gameplay.
   - `make_guess(...)`: Handles player input for making guesses.
   - `game_over(...)`: Manages the game-over state.
   - `cheat(...)`: Enables the "cheat" mode.
   - `Board` class methods and properties:
     - `__init__(...)`: Initializes the game board.
     - `reset(...)`: Resets the game board to its initial state.
     - `code` (property): Gets and sets the secret code.
     - `current_guess` (property and setter): Manages player guesses.
     - `__feedback(...)`: Calculates feedback pegs.
     - `draw(...)`: Draws the game board using the `tabulate` library.
     - `__data` (property): Organizes game data for rendering.
     - `__validate_code(...)`: Validates code or guess format.

2. **`test_project.py`**: This file contains unit tests for various components of the project. It ensures that different aspects of the game, such as code validation and feedback calculation, function correctly and reliably.

3. **`requirements.txt`**: Lists the project's dependencies and their versions. You can install these requirements using `pip` as described in the "Install Requirements" section.

4. **`README.md`**: The documentation you are currently reading, providing an overview of the project, its structure, and how to play the game.

## Project Structure

The code begins by initializing a curses screen and creating three new windows:

1. **board_window**: This window is mainly for displaying a table that represents the game board.
2. **hint_window**: This window is used for displaying hints and a game over messages.
3. **input_window**: It is designed for gathering user input, placing itself precisely in the current column to indicate the current round of the game.

## Game Initialization

The game initializes with the creation of these windows, and then control is passed to the `play_game()` function. This function initializes a new `Board` instance outside of a while loop because in Mastermind, you don't buy a new board for each game; you reset the existing board. The `Board` class is responsible for generating a random 4-digit code using numbers from 1 to 6, maintaining a list for storing guesses and feedback pegs, tracking the current round, and determining if the player has won.

## Feedback Logic

One significant design choice is how feedback is handled. In this project, the logic of a code-maker wasn't considered as straightforward as it may seem. The board acts like an electric board with specific behaviors:

- If you enter a valid code, it gives you feedback as pegs, where "O" represents a correct number in the correct spot, "X" represents a correct number but in the wrong spot, and "_" represents an incorrect number.

   These feedback pegs are essential for deducing the secret code. They are sorted for clarity, not in the order of your guesses.

## Board Class

The `Board` class is the heart of the game, managing code generation, guess validation, feedback calculation, and game state tracking. Key methods and properties in the `Board` class include:

- `current_guess`: Returns the player's current guess for the current round.
- `current_guess` setter: Processes the player's guess, validates it, updates pegs, and checks if the player has won or if the game has ended.

### Data Property

The `data` property organizes and standardizes the board's data, ensuring a consistent length throughout the game. This structured data is then passed to the `draw` method for display. It relies on the `

tabulate` library to create a visually appealing table that represents the game board.

### Draw Method

The `draw` method employs the `tabulate` library to craft a well-structured and visually appealing game board. It showcases crucial game information, such as round numbers, player guesses (code pegs), and feedback pegs. This method ensures that data is displayed in an organized manner, making it easier for players to track their progress and make informed decisions during gameplay.

### Validate Code Method

- `__validate_code`: The `__validate_code` method ensures the validity of the player's guess or any code set manually. It checks the correct number of digits, valid numbers (between 1 and 6), and no number repetition.

   This method maintains the game's integrity, whether validating player guesses or setting codes for testing and development.

## How to Play

### Install Requirements

Before running the Mastermind game, make sure you have the following requirements installed:

- Python 3: You can download Python from the [official website](https://www.python.org/downloads/).

Next, install the required Python libraries by running:

```bash
pip install -r requirements.txt
```

This will install the necessary libraries (`tabulate`), to run the game.

### Play The Game
To play the game:

1. Launch the game using the provided Python script.
2. Enter a 4-digit code using numbers from 1 to 6.

### Feedback Pegs

3. Receive Feedback as Pegs:

   - **"O"**: Correct number in the correct spot.
   - **"X"**: Correct number but in the wrong spot.
   - **"_"**: Incorrect number.

   Deciphering these pegs helps you deduce the secret code. They are sorted for clarity, not in the order of your guesses.

### Valid Guesses

4. Continue making guesses and receiving feedback until you break the code or run out of chances.

### Invalid Guesses

   - If you enter an invalid guess (e.g., not exactly 4 numbers), you'll receive an error message.
   - If you use numbers outside the valid range (1 to 6), you'll be prompted to correct your input.
   - Repeating numbers in your guess is not allowed.

5. Upon game completion, you can choose to replay.

### Cheats (Optional)

You can enable cheats using the following command:

```bash
./project.py -c
```

Enabling this option reveals the secret code, stored in `$TMPDIR/mastermind_code.txt` (where `$TMPDIR` could be `/tmp` or your system's designated directory). This allows you to experiment freely with full knowledge of the secret code.

These cheat options can enhance your understanding of the game's mechanics and help you develop advanced strategies. Enjoy mastering the game with these additional features!

## Key Takeaways

This project offered several valuable lessons:

- **Game Mechanics**: Mastered the mechanics of the classic Mastermind game, gaining insights into code-breaking strategies.

- **Python and Curses**: Explored Python's curses library for creating interactive terminal-based applications.

- **Error Handling**: Enhanced input validation and error handling for a smoother user experience.

- **Object-Oriented Programming**: Implemented object-oriented principles to encapsulate game logic.

- **Problem Solving**: Improved problem-solving skills when dealing with complex game logic and debugging.

Overall, this project provided a valuable learning experience, reinforcing coding skills, problem-solving, and user-focused design.

This was CS50P, enjoy playing Mastermind!
