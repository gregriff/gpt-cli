from functools import partial
from typing import Callable, Generator

import openai
from prompt_toolkit import PromptSession
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from rich.console import Console
from tiktoken import encoding_for_model

from terminal import *
from output import Output
from costs import gpt_pricing

# example_style = Style.from_dict({
#     'toolbar': 'bg:#002b36'
# })


def bottom_toolbar(num_tokens: int, price: float):
    total_price = num_tokens * price
    return [('class:toolbar', f"Price: ${total_price:.3f}")]

    # TODO: keep track of tokens with openai lib. Update program state with these and print to screen

    # TODO: use prompt_toolkit to add a bottom bar and a fullscreen settings menu. Could use rich to print in there


class Prompt:
    def __init__(self, text_color: str, code_theme: str, sys_msg: dict, prompt_args: dict):
        self.system_message = sys_msg
        self.prompt_args = prompt_args
        self.model = prompt_args['model']

        self.messages = [sys_msg, ]
        self.count = 0
        self.tokens = 0
        self.price_per_token = gpt_pricing(self.model, prompt=True)
        self.terminal_width = TERM_WIDTH

        self.session = PromptSession(editing_mode=EditingMode.VI)
        self.console = Console()
        self.prompt = HTML('<b><ansibrightyellow>?</ansibrightyellow></b> <b><ansibrightcyan>></ansibrightcyan></b> ')
        self.bindings = KeyBindings()

        self.color = text_color
        self.theme = code_theme

        # lookup table to run functions on certain prompts (if user presses enter)
        self.special_case_functions: dict[str, Callable] = {
            **{kw: lambda: exit_program() for kw in ('exit', 'e', 'q', 'quit',)},
            **{kw: lambda: self.clear_history() for kw in ('c', 'clear',)},
            **{kw: lambda: self.change_system_msg() for kw in ('sys', 'system', 'message',)},
            **{kw: lambda: self.change_temp() for kw in ('temp', 'temperature',)}
            # TODO: one func for opening settings menu, sqlite for maintaing settings
        }

    def run(self, *args):
        """
        Main loop to run REPL. CTRL+C to cancel current completion and CTRL+D to quit.
        TODO: given cli args, change program behavior
        """
        while True:
            try:
                user_input: str = self.session.prompt(self.prompt)
                cleaned_input = user_input.casefold().strip()
                prompt_the_llm = partial(self.prompt_llm, user_input)
                self.special_case_functions.get(cleaned_input, prompt_the_llm)()
            except KeyboardInterrupt:
                print()
                continue
            except EOFError:
                # print total cost
                exit_program()

    def prompt_llm(self, user_input: str):
        print(RESET)
        self.messages.append({'role': 'user', 'content': user_input})
        try:
            response: Generator = openai.ChatCompletion.create(messages=self.messages, **self.prompt_args)
        except openai.error.APIConnectionError as e:
            print(YELLOW, f'Could not connect to API. Error: {str(e)}\n')
            return

        with Output(self.color, self.theme) as output:
            for chunk in response:
                for choice in chunk['choices']:
                    text_part = choice['delta'].get('content', '')
                    output.print(text_part)

        self.messages.append({"role": "assistant", "content": output.full_response})
        total_price = self.num_tokens() * self.price_per_token
        self.console.print(f"Price: ${total_price:.3f}", justify='right', style='dim')
        self.count += 1

    def clear_history(self, auto=False) -> None:
        print(RESET, BOLD, BLUE)
        if not auto or self.count:
            print(f'history cleared: {self.count} messages total', '\n', RESET)
        self.messages = [self.system_message, ]
        self.count = 0

    def change_system_msg(self) -> None:
        prompt = input(f'\n{BOLD + RED}new system message:\n{CYAN}> ')
        new_message = prompt.casefold().strip()
        self.system_message['content'] = new_message
        print(BOLD + YELLOW, f'\nsystem message set to: "{new_message}"', sep='')
        self.clear_history(auto=True)

    def change_temp(self):
        prompt = input(f'\n{BOLD + RED}new temperature:\n{CYAN}> ')
        new_temp = float(prompt.casefold().strip())
        if 0.0 < new_temp < 1.0:
            self.prompt_args['temperature'] = new_temp
            reply = f'\ntemperature set to: "{new_temp}"'
        else:
            reply = f'\ninvalid temperature: {new_temp}, must be 0 < temp < 1'
        print(BOLD + YELLOW, reply, '\n', sep='')

    def num_tokens(self) -> int:
        '''
        Get the total number of tokens used in the current chat history given OpenAI's token
        counting package `tiktoken`
        '''
        encoding = encoding_for_model(self.prompt_args['model'])
        num_tokens = 0
        for message in self.messages:
            # every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += 4
            for role, text in message.items():
                assert isinstance(text, str)
                num_tokens += len(encoding.encode(text))
                if role == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens


def exit_program():
    # TODO: use token algo to print total tokens in session
    print(CLEAR_CURRENT_LINE)
    system('clear')
    exit(0)

    # TODO: need to manually wrap this open_settings function
    # @self.bindings.add('c-n')
    # def open_settings(event):
    #     " Open settings menu/controls when `c-n` is pressed. "

    # def print_hello():
    #     print('hello world')
    #
    # run_in_terminal(print_hello)  # need this if still want to use prompt while hook is printing
