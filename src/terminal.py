from shutil import get_terminal_size
from sys import stdin
from termios import TCSAFLUSH, TCSANOW, tcgetattr, tcsetattr
from tty import setcbreak
from typing import Any

# helpful ANSI escape codes
RESET = "\033[0;0m"
CLEAR_CURRENT_LINE = "\r\033[K"
CLEAR_TO_END_OF_CURSOR = "\033[K"
MOVE_UP_ONE_LINE_AND_GOTO_LEFTMOST_POS = "\033[F"
CLEAR_LINE_ABOVE_CURRENT = "\033[F\033[K"

EXIT_COMMANDS = "exit", "e", "q", "quit"
CLEAR_COMMANDS = "c", "clear"
MULTILINE_COMMANDS = "\\", "ml"


def disable_input() -> list[Any]:
    """
    disable echoing of characters. this prevents unwanted glitches in displaying LLM output. Since we use
    something which modifies stdin (probably the Console object), we need to save settings to reenable input
    because its file descriptor changes
    """
    old_settings = tcgetattr(fd := stdin.fileno())
    setcbreak(fd, TCSANOW)
    return old_settings


# Restore terminal settings
def reenable_input(old_settings):
    """enable echoing of characters and delete any queued input to the terminal"""
    if not stdin.closed:
        tcsetattr(stdin, TCSAFLUSH, old_settings)


def get_term_width() -> int:
    """width of terminal in columns"""
    return get_terminal_size().columns
