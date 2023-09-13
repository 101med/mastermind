class InvalidCode(ValueError):
    """
    Custom exception class for representing an invalid game code.

    This exception is raised when an attempt is made to use an invalid code
    in the Mastermind game.
    """
    pass

class Help(Exception):
    """
    Custom exception class for representing a user request for help.

    This exception is raised when a player requests help during the Mastermind game.
    It is used caught and handle displaying the game's help menu.
    """
    pass

class GameOver(Exception):
    """
    Custom exception class for representing the end of the game.

    This exception is raised when the Mastermind game is over, either because
    the player won or lost or wants to exit. It is used to caught and handle the end of the game.
    """
    pass
