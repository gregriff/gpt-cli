from typing import Callable, Generator

import openai
from prompt_toolkit import prompt as p
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

from functions import *
from terminal import *
from output import Output


example_style = Style.from_dict({
    'rprompt': 'bg:#008000 #ffffff',
})


def get_rprompt():
    return 'tokens: _'


def prompt_continuation(width, line_number, is_soft_wrap):
    return '.' * width
    # Or: return [('', '.' * width)]


class Prompt:
    def __init__(self, text_color: str, code_theme: str, s_msg: dict, p_args: dict):
        self.system_msg = s_msg
        self.prompt_arguments = p_args

        self.messages = [s_msg, ]
        self.count = 0
        self.tokens = 0
        self.terminal_width = TERM_WIDTH

        self.prompt = ''
        self.stripped_prompt = ''

        self.color = text_color
        self.theme = code_theme

        # lookup table to run functions on certain prompts
        self.special_case_functions: dict[str, Callable] = {
            **{kw: lambda: exit_program() for kw in ('exit', 'e', 'q', 'quit',)},
            **{kw: lambda: clear_history(self.count) for kw in ('c', 'clear',)},
            **{kw: lambda: change_system_msg(self.count) for kw in ('sys', 'system', 'message',)},
            **{kw: lambda: change_temp(self.messages, self.count) for kw in ('temp', 'temperature',)}
            # TODO: one func for opening settings menu, sqlite for maintaing settings
        }

    def get_prompt(self):
        try:
            self.prompt = p(
                HTML('<b><ansibrightyellow>?</ansibrightyellow></b> <b><ansibrightcyan>></ansibrightcyan></b> '),
                rprompt=get_rprompt, style=example_style)
            self.stripped_prompt = self.prompt.casefold().strip()
        except KeyboardInterrupt:
            exit(0)

    def interpret_user_input(self):
        """
        see if prompt triggers any predefined action and either run the action or
        prompt the llm and update runtime variables
        """
        if (user_action := self.special_case_functions.get(self.stripped_prompt)) is not None:
            user_action()
        else:
            self.prompt_llm()

    def prompt_llm(self):
        print(RESET)
        self.messages.append({'role': 'user', 'content': self.prompt})
        try:
            response: Generator = openai.ChatCompletion.create(messages=self.messages, **prompt_args)
        except openai.error.APIConnectionError as e:
            print(YELLOW, f'Could not connect to API. Error: {str(e)}\n')
            return

        output = Output(self.color, self.theme)
        for chunk in response:
            for choice in chunk['choices']:
                text_part = choice['delta'].get('content', '')
                output.update(text_part)

        output.replace_with_markdown()
        self.messages.append({"role": "assistant", "content": output.final_response()})
        self.count += 1

        # TODO: keep track of tokens with openai lib. Update program state with these and print to screen

        # TODO: use prompt_toolkit to add a bottom bar and a fullscreen settings menu. Could use rich to print in there
