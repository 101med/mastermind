# Mastermind Game

An implementation of the classic Mastermind game using Python curses.

![Screenshot](https://github.com/101med/mastermind/raw/main/preview.jpg)

- [Mastermind Game](#mastermind-game)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [How to Play](#how-to-play)
- [Game Rules](#game-rules)
- [Background](#background)
  - [What I Learned](#what-i-learned)

## Features

- Classic Mastermind gameplay.
- Interactive terminal interface.
- Support for cheating by revealing the secret code.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following prerequisites installed:

- Python 3.x
- pip (Python package manager)

### How to Play

   ```bash
   git clone https://github.com/101med/mastermind
   cd mastermind/
   pip install -r requirements.txt
   ./project.py
   ```
During the game, you can use the following keybindings:
- 0-9: Enter a combination of four unique numbers for your guess.
- Enter: Submit your guess for the current round.
- q: Quit the game at any time.

## Game Rules

Mastermind is a classic code-breaking game played between two players: the codemaker and the codebreaker. In this Python implementation, you will play as the codebreaker.

### Objective

Your objective as the codebreaker is to guess the secret code created by the computer (codemaker). The secret code consists of a sequence of four numbers.

### Guessing

1. You have a limited number of rounds (10) to guess the secret code.

2. In each round, you will make a guess by selecting a combination of four unique numbers. The numbers cannot be repeated, and the order matters.

3. After each guess, you will receive feedback in the form of pegs:
   - "O": Correct number and position.
   - "X": Correct number but in the wrong position.
   - "_": No matches.

### Winning

You win the game by correctly guessing the secret code within the allowed number of rounds. Your score will be displayed as the number of rounds remaining.

### Cheating

You have the option to cheat by revealing the secret code at any time. Use this feature sparingly!

Now that you understand the rules, launch the game and test your code-breaking skills!

## Background

This Mastermind Game project is part of the final submission for CS50's Introduction to Computer Science course at Harvard University. It serves as a culmination of the skills and knowledge acquired throughout the course.

### What I Learned

While working on this project, I had the opportunity to:

- **Apply Python Programming**: I strengthened my Python programming skills, especially in handling data structures and logic.

- **Learn Curses Library**: I explored and utilized the curses library in Python to create an interactive terminal interface for the game.

- **Practice Problem Solving**: Developing the game's logic and implementing the rules challenged me to think critically and practice problem-solving techniques.

- **Version Control with Git**: I gained experience in using Git and GitHub for version control, collaboration, and project management.

This project allowed me to combine my programming skills with creative problem-solving to bring a classic game to life in a terminal environment. I hope you enjoy playing the Mastermind Game as much as I enjoyed creating it!
