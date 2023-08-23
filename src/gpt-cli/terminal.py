from importlib.metadata import version
from os import system
from shutil import get_terminal_size

from config import prompt_args

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
ORANGE = "\x1b[0;33m"
YELLOW = "\x1b[1;33m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"


def greeting():
    system('clear')
    print(CYAN)
    print('=*=' * 10, ORANGE)
    print(f'{"openai" : <10}{"v" + version("openai") : <15}')
    print(f'{"model" : <10}{prompt_args.get("model") : <15}', RESET + CYAN)
    print('=*=' * 10, end='\n\n')
