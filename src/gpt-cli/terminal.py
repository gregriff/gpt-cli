from shutil import get_terminal_size

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
ORANGE = "\x1b[0;33m"
YELLOW = "\x1b[1;33m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"

CLEAR_CURRENT_LINE = "\r\033[K"
CLEAR_TO_END_OF_CURSOR = "\033[K"
MOVE_UP_ONE_LINE_AND_GOTO_LEFTMOST_POS = "\033[F"
CLEAR_LINE_ABOVE_CURRENT = "\033[F\033[K"

TERM_WIDTH = get_terminal_size().columns
