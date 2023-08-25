from terminal import *
from config import *


def clear_history(count: int, auto=False) -> tuple[list[dict], int]:
    print(RESET, BOLD, BLUE)
    if not auto or count:
        print(f'history cleared: {count} messages total', '\n', RESET)
    return [system_message, ], 0


def exit_program():
    # TODO: use token algo to print total tokens in session
    print(CLEAR_CURRENT_LINE)
    system('clear')
    exit(0)


def change_system_msg(count: int) -> tuple[list[dict], int]:
    prompt = input(f'\n{BOLD + RED}new system message:\n{CYAN}> ')
    new_message = prompt.casefold().strip()
    system_message['content'] = new_message
    print(BOLD + YELLOW, f'\nsystem message set to: "{new_message}"', sep='')
    return clear_history(count, auto=True)


def change_temp(messages: list[dict], count: int):
    prompt = input(f'\n{BOLD + RED}new temperature:\n{CYAN}> ')
    new_temp = float(prompt.casefold().strip())
    if 0.0 < new_temp < 1.0:
        prompt_arguments['temperature'] = new_temp
        reply = f'\ntemperature set to: "{new_temp}"'
    else:
        reply = f'\ninvalid temperature: {new_temp}, must be 0 < temp < 1'
    print(BOLD + YELLOW, reply, '\n', sep='')
    return messages, count
