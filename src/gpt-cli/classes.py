from typing import Callable, Generator, Optional

import openai
from prompt_toolkit import prompt as p
from prompt_toolkit.formatted_text import HTML, ANSI
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

from functions import *
from terminal import *

example_style = Style.from_dict({
    'rprompt': 'bg:#008000 #ffffff',
})


def get_rprompt():
    return 'tokens: _'


def prompt_continuation(width, line_number, is_soft_wrap):
    return '.' * width
    # Or: return [('', '.' * width)]


class Output:
    """
    Encapsulates all the data needed to update the terminal with a chat completion generator response.
    Keeps track of how many lines are printed to the screen and pretty-prints everything.
    """

    def __init__(self):
        self.full_response = []
        self.current_line_length = 0
        self.total_num_of_lines = 0
        self.terminal_width = get_terminal_size().columns
        self.max_text_width = self.terminal_width - 2
        self.console = Console(width=self.terminal_width)

    def print(self, text: str):
        self.console.print(Text(text, style='green', overflow='fold', ), end='')

    def update(self, text: str):
        """
        Given a partial response from openai api, print it, ensuring it is wrapped to the max text width, and keep
        track of the number of lines total so far
        """
        # ensure newlines are counted
        newlines_in_text = text.count('\n')
        if newlines_in_text:
            self.total_num_of_lines += newlines_in_text
            chars_after_last_newline = len(text.split('\n')[-1])
            self.current_line_length = chars_after_last_newline
        else:
            self.current_line_length += len(text)

        # wrap text if needed
        if self.current_line_length >= self.max_text_width:
            slice_idx = self.max_text_width - self.current_line_length
            safe_to_print = text[:slice_idx:]
            self.print(safe_to_print)
            rest_of_text = text[slice_idx::]
            self.print('\n' + rest_of_text)
            # inc newline counter
            self.total_num_of_lines += 1
            self.current_line_length = len(rest_of_text)
        else:
            self.print(text)
        self.full_response.append(text)

    def replace_with_markdown(self, theme: Optional[str] = 'monokai', color: Optional[str] = 'green'):
        """
        Called after an entire response has been printed to the screen, this function deletes the entire response
        using ANSI codes and then renders it in markdown
        """
        for _ in range(self.total_num_of_lines):
            print(f'\033[0A', ''*self.max_text_width, end='\r', sep='')
        # print(f"\033[{self.total_num_of_lines}A", end="\r")
        self.console.print(Markdown(self.final_response(), style=color, code_theme=theme))
        print('\n')

    def final_response(self) -> str:
        return "".join(self.full_response)


class Prompt:
    def __init__(self, text_color: str, code_theme: str, s_msg: dict, p_args: dict):
        self.system_msg = s_msg
        self.prompt_arguments = p_args

        self.messages = [s_msg, ]
        self.count = 0
        self.tokens = 0
        self.terminal_width = get_terminal_size().columns

        self.prompt = ''
        self.stripped_prompt = ''

        self.color = text_color
        self.theme = code_theme

        # lookup table to run functions on certain prompts
        self.special_case_functions: dict[str, Callable] = {

            # exit and clear history behavior
            **{kw: lambda: exit_program() for kw in ('exit', 'e', 'q', 'quit',)},
            **{kw: lambda: clear_history(self.count) for kw in ('c', 'clear',)},

            # change settings
            **{kw: lambda: change_system_msg(self.count) for kw in ('sys', 'system', 'message',)},
            **{kw: lambda: change_temp(self.messages, self.count) for kw in ('temp', 'temperature',)}
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

        output = Output()
        for chunk in response:
            for choice in chunk['choices']:
                text_part = choice['delta'].get('content', '')
                output.update(text_part)

        final_response = output.final_response()
        output.replace_with_markdown(color=self.color, theme=self.theme)

        self.messages.append({"role": "assistant", "content": final_response})
        self.count += 1
