from shutil import get_terminal_size
from sys import stdout
from typing import Callable, Generator, Optional

import openai
from prompt_toolkit import prompt as p
from prompt_toolkit.formatted_text import HTML, ANSI
from prompt_toolkit.styles import Style
from rich.console import Console, Theme
from rich.markdown import Markdown
from rich.text import Text

from functions import *
from terminal import *


# TODO: use this for consistency. Eventually load these from db.
# custom_theme = Theme({
#     "info": "dim cyan",
#     "warning": "magenta",
#     "danger": "bold red"
# })

def md_theme(text_color: str):
    return Theme({
        "markdown": text_color,
        "markdown.code": 'bold blue'
    })


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

    def __init__(self, color, theme):
        self.full_response = []
        self.current_line_length = 0
        self.total_num_of_lines = 0
        self.terminal_width = TERM_WIDTH
        self.max_text_width = self.terminal_width - 2

        self.console = Console(width=self.terminal_width, theme=md_theme(color))
        self.color = color  # color of normal text
        self.theme = theme

    def print(self, text: str):
        # TODO: if errors with markdown rendering, play with overflow and softwrap
        self.console.print(Text(text, style=self.color, overflow='ignore', ), soft_wrap=True, end='')

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

        # TODO: simple ```...``` parser. When closing ``` is detected, if a newline is not the next character,
        #  insert one, and inc newline counter.
        # this should resolve bugs with duplicate lines after markdown rendering

        # wrap text if needed
        if self.current_line_length >= self.max_text_width:
            slice_idx = self.max_text_width - self.current_line_length
            safe_to_print = text[:slice_idx:]
            rest_of_text = text[slice_idx::]
            self.print(f'{safe_to_print}\n{rest_of_text}')
            self.total_num_of_lines += 1
            self.current_line_length = len(rest_of_text)
        else:
            self.print(text)
        self.full_response.append(text)

    def replace_with_markdown(self):
        """
        Called after an entire response has been printed to the screen, this function deletes the entire response
        using ANSI codes and then renders it in markdown
        """
        stdout.write(CLEAR_CURRENT_LINE)
        for _ in range(self.total_num_of_lines):
            stdout.write(CLEAR_LINE_ABOVE_CURRENT)
        markdown_obj = Markdown(self.final_response(), style=self.color, code_theme=self.theme)
        self.console.print(markdown_obj, '\n', overflow='fold', highlight=False)

    def final_response(self) -> str:
        return "".join(self.full_response)


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
