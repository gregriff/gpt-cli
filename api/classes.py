from typing import Callable

from config import system_message, prompt_args
from functions import *
from terminal import *
from helpers import prompt_llm


class Prompt:
    def __init__(self):
        self.system_msg = system_message
        self.prompt_arguments = prompt_args

        self.messages = [self.system_msg, ]
        self.count = 0
        self.tokens = 0

        self.prompt = ''
        self.stripped_prompt = ''

        # lookup table to run functions on certain prompts
        self.special_case_functions: dict[str, Callable] = {

            # exit and clear history behevior
            **{kw: lambda *_: exit_program() for kw in ('exit', 'e', 'q', 'quit',)},
            **{kw: lambda _, cnt: clear_history(cnt) for kw in ('c', 'clear',)},

            # change settings
            **{kw: lambda _, cnt: change_system_msg(cnt) for kw in ('sys', 'system', 'message')},
            **{kw: lambda msgs, cnt: change_temp(msgs, cnt) for kw in ('temp', 'temperature',)}
        }

    def get_prompt(self):
        try:
            prompt = input(f'{BOLD + YELLOW}? {CYAN}> ')
            self.stripped_prompt = prompt.casefold().strip()
            self.prompt = prompt
        except KeyboardInterrupt:
            exit(0)

    def interpret_user_input(self):
        # see if prompt triggers any predefined action
        user_action = self.special_case_functions.get(self.stripped_prompt)

        # either run the action or prompt the llm; update runtime variables
        self.messages, self.count = user_action(self.messages, self.count) \
            if user_action else prompt_llm(self.prompt, self.messages, self.count)