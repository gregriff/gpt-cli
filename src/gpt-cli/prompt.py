from typing import Callable, Generator

import openai
from prompt_toolkit import PromptSession
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from functions import *
from terminal import *
from output import Output


example_style = Style.from_dict({
    'bottom-toolbar': ' #ffffff',
})


def bottom_toolbar():
    return [('class:bottom-toolbar', 'Tokens: ')]


class Prompt:
    def __init__(self, text_color: str, code_theme: str, s_msg: dict, p_args: dict):
        self.system_message = s_msg
        self.prompt_arguments = p_args

        self.messages = [s_msg, ]
        self.count = 0
        self.tokens = 0
        self.terminal_width = TERM_WIDTH

        self.session = PromptSession(editing_mode=EditingMode.VI)
        self.prompt = HTML('<b><ansibrightyellow>?</ansibrightyellow></b> <b><ansibrightcyan>></ansibrightcyan></b> ')
        self.bindings = KeyBindings()

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

    def run(self):
        """
        Main loop to run REPL. CTRL+C to cancel current completion and CTRL+D to quit.
        """
        while True:
            try:
                user_input = self.session.prompt(self.prompt, style=example_style)
                stripped_input = user_input.casefold().strip()

                if (user_action := self.special_case_functions.get(stripped_input)) is not None:
                    user_action()
                else:
                    self.prompt_llm(user_input)
            except KeyboardInterrupt:
                print()
                continue
            except EOFError:
                exit_program()

    def prompt_llm(self, user_input: str):
        print(RESET)
        self.messages.append({'role': 'user', 'content': user_input})
        try:
            response: Generator = openai.ChatCompletion.create(messages=self.messages, **self.prompt_arguments)
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

        @self.bindings.add('c-t')
        def open_settings(event):
            " Say 'hello' when `c-t` is pressed. "

            # def print_hello():
            #     print('hello world')
            #
            # run_in_terminal(print_hello)
