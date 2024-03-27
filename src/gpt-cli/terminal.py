from sys import stdin
from shutil import get_terminal_size
from termios import TCSANOW, tcsetattr, tcgetattr, TCSAFLUSH
from tty import setcbreak

# helpful ANSI escape codes
RESET = "\033[0;0m"
CLEAR_CURRENT_LINE = "\r\033[K"
CLEAR_TO_END_OF_CURSOR = "\033[K"
MOVE_UP_ONE_LINE_AND_GOTO_LEFTMOST_POS = "\033[F"
CLEAR_LINE_ABOVE_CURRENT = "\033[F\033[K"

EXIT_COMMANDS = "exit", "e", "q", "quit"
CLEAR_COMMANDS = "c", "clear"
MULTILINE_COMMANDS = "\\", "ml"


def disable_input() -> None:
    """disable echoing of characters. this prevents unwanted glitches in displaying LLM output"""
    setcbreak(stdin, TCSANOW)


def reenable_input() -> None:
    """enable echoing of characters and delete any queued input to the terminal"""
    if not stdin.closed:
        tcsetattr(stdin, TCSAFLUSH, tcgetattr(stdin))


def get_term_width() -> int:
    """width in columns of terminal"""
    return get_terminal_size().columns
