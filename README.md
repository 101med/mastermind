# Curses Mastermind

#### Video Demo:  [Demo Video](https://youtube.com/)

#### Description:
Mastermind Game in Python's Curses

## Table of Contents
- [Description](#description)
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

## Description

### Mastermind Game in Python with Curses

This project is an implementation of the classic code-breaking board game, Mastermind, using Python with the built-in library, curses. In this README, we will discuss how the code works and why certain design choices were made.

## Project Contents

### Project Structure

The code begins by initializing a curses screen and creating three new windows:

- **board_window**: This window is mainly for displaying a table that represents the game board.
- **hint_window**: This window is used for displaying hints and a game over messages.
- **input_window**: It is designed for gathering user input, placing itself precisely in the current column to indicate the current round of the game.

### Game Initialization

The game initializes with the creation of these windows, and then control is passed to the `play_game()` function. This function initializes a new `Board` instance outside of a while loop because in Mastermind, you don't buy a new board for each game; you reset the existing board. The `Board` class is responsible for generating a random 4-digit code using numbers from 1 to 6, maintaining a list for storing guesses and feedback pegs, tracking the current round, and determining if the player has won.

### Feedback Logic

One significant design choice is how feedback is handled. In this project, the logic of a code-maker wasn't considered as straightforward as it may seem. The board acts like an electric board with specific behaviors:

- If you enter a valid code, it gives you feedback as pegs, where "O" represents a correct number in the correct spot, "X" represents a correct number but in the wrong spot, and "_" represents an incorrect number.

   These feedback pegs are essential for deducing the secret code. They are sorted for clarity, not in the order of your guesses.

### Board Class

The `Board` class is the heart of the game, managing code generation, guess validation, feedback calculation, and game state tracking. Key methods and properties in the `Board` class include:

- `current_guess`: Returns the player's current guess for the current round.
- `current_guess` setter: Processes the player's guess, validates it, updates pegs, and checks if the player has won or if the game has ended.

#### Data Property

The `data` property organizes and standardizes the board's data, ensuring a consistent length throughout the game. This structured data is then passed to the `draw` method for display. It relies on the `tabulate` library to create a visually appealing table that represents the game board.

#### Draw Method

The `draw` method employs the `tabulate` library to craft a well-structured and visually appealing game board. It showcases crucial game information, such as round numbers, player guesses (code pegs), and feedback pegs. This method ensures that data is displayed in an organized manner, making it easier for players to track their progress and make informed decisions during gameplay.

#### Validate Code Method

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

To play the game, follow these steps:

1. Launch the game using the provided Python script.
2. Enter a 4-digit code using numbers from 1 to 6. (You can use any 10-base numbers, but numbers greater than 6 are considered invalid.)

Note: You can press **q** at any time to stop the game and reveal the code. Press any other key to restart a new game with a new code, or press **q** again to quit.

#### Feedback Pegs

3. Receive Feedback as Pegs:

   - **"O"**: Correct number in the correct spot.
   - **"X"**: Correct number but in the wrong spot.
   - **"_"**: Incorrect number.

   Deciphering these pegs helps you deduce the secret code. They are sorted for clarity, not in the order of your guesses.

#### Valid Guesses

4. Continue making guesses and receiving feedback until you break the code or run out of chances.

#### Invalid Guesses

   - If you enter an invalid guess (e.g., not exactly 4 numbers), you'll receive an error message.
   - If you use numbers outside the valid range (1 to 6), you'll be prompted to correct your input.
   - Repeating numbers in your guess is not allowed.

5. Upon game completion, you can choose to replay.

### Cheats (Optional)

You can enable cheats using the following command:

```bash
./project.py -c
```

Enabling this option reveals the secret code, stored in `$TMPDIR/mastermind_code.txt` (where `$TMPDIR` could be `/tmp` or your system's designated directory).

## Key Takeaways

This project offered several valuable lessons:

- **Game Mechanics**: Mastered the mechanics of the classic Mastermind game, gaining insights into code-breaking strategies.

- **Python and Curses**: Explored Python's curses library for creating interactive terminal-based applications.

- **Error Handling**: Enhanced input validation and error handling for a smoother user experience.

- **Object-Oriented Programming**: Implemented object-oriented principles to encapsulate game logic.

- **Problem Solving**: Improved problem-solving skills when dealing with complex game logic and debugging.

Overall, this project provided a valuable learning experience, reinforcing coding skills, problem-solving, and user-focused design.

This was CS50P, enjoy playing Mastermind!
