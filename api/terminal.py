from importlib.metadata import version

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
ORANGE = "\x1b[0;33m"
YELLOW = "\x1b[1;33m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"


def greeting(model):
    print(CYAN, '\n', '=*=' * 10, ORANGE)
    print(f'{"openai" : <10}{"v" + version("openai") : <15}')
    print(f'{"model" : <10}{model : <15}', RESET + CYAN)
    print('=*=' * 10, end='\n\n')


def max_text_width(term_size_columns: int):
    return int(term_size_columns / 2) if term_size_columns > 80 else int(term_size_columns)
