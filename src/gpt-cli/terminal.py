from shutil import get_terminal_size

# helpful ANSI escape codes
RESET = "\033[0;0m"
CLEAR_CURRENT_LINE = "\r\033[K"
CLEAR_TO_END_OF_CURSOR = "\033[K"
MOVE_UP_ONE_LINE_AND_GOTO_LEFTMOST_POS = "\033[F"
CLEAR_LINE_ABOVE_CURRENT = "\033[F\033[K"

TERM_WIDTH = get_terminal_size().columns

EXIT_COMMANDS = "exit", "e", "q", "quit"
CLEAR_COMMANDS = "c", "clear"
