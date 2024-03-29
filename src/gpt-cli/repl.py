from functools import partial
from os import system
from typing import Callable

from openai import OpenAIError
from anthropic import AnthropicError

from prompt_toolkit import PromptSession
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding import KeyBindings
from rich import box
from rich.columns import Columns
from rich.panel import Panel
from rich.style import Style
from rich.console import Console
from rich.text import Text

from terminal import *
from output import Output
from models import LLM
from styling import *


class REPL:
    def __init__(
        self,
        model: LLM,
        text_color: str,
        code_theme: str,
    ):
        self.model = model
        if not stdin.isatty():
            self.one_shot_and_quit()

        self.tokens = 0
        self.total_cost = 0
        self.multiline = False

        self.bindings = KeyBindings()
        # self.bindings.add('c-n')(self.enable_multiline)
        self.session = PromptSession(
            editing_mode=EditingMode.VI, key_bindings=self.bindings
        )
        self.console = Console(width=get_term_width(), theme=md_theme(text_color))
        self.console.set_window_title(self.model.model_name)

        self.color = Style.parse(text_color)
        self.theme = code_theme

        # lookup table to run functions on certain prompts (if user presses enter)
        self.special_case_functions: dict[str, Callable] = {
            kw: function
            for keywords, function in [
                (EXIT_COMMANDS, self.exit_program),
                (CLEAR_COMMANDS, self.clear_history),
                (MULTILINE_COMMANDS, self.enable_multiline),
            ]
            for kw in keywords
        }

    def run(self, initial_prompt: str = None) -> None:
        """
        Main loop to run REPL. CTRL+C to cancel current completion and CTRL+D to quit.
        """
        # fmt: off
        while True:
            try:
                if (user_input := initial_prompt) is None:
                    style = MULTILINE_PROMPT_STYLE if self.multiline else PROMPT_STYLE
                    user_input = self.session.prompt(PROMPT_LEAD, style=style, multiline=self.multiline).strip()
                    if not user_input:
                        continue  # prevent API error
                disable_input()
                cleaned_input = user_input.casefold()
                prompt_the_llm = partial(self.prompt_llm, user_input)
                self.special_case_functions.get(cleaned_input, prompt_the_llm)()
            except KeyboardInterrupt:
                print()
                continue
            except EOFError:  # ctrl + D
                self.exit_program()
            finally:
                initial_prompt = None
                reenable_input()
        # fmt: on

    def prompt_llm(self, user_input: str) -> None:

        # adjust printing if user has resized their terminal
        self.console.width = get_term_width()
        try:
            with Output(self.console, self.color, self.theme) as output:
                for text in self.model.prompt_and_stream_completion(user_input):
                    output.print(text)
        except (OpenAIError, AnthropicError) as e:
            self.console.print(f"API Error: {str(e)}\n", style=ERROR_STYLE)
            return

        self.print_cost()
        self.multiline = False

    def clear_history(self) -> None:
        """add to the running total the price of the current chat thread and reset model state"""
        self.console.width = get_term_width()
        system("clear")
        message = f"history cleared: {self.model.prompt_count} {'prompt' if self.model.prompt_count == 1 else 'prompts'} total"
        self.console.print(message, justify="right", style=CLEAR_HISTORY_STYLE)
        self.total_cost += self.model.get_cost_of_current_chat()
        self.model.reset()

    @staticmethod
    def get_cost_str(cost: float) -> str:
        """given a cost in dollars, return a formatted string to be printed to screen"""
        if cost >= 1.0:
            return f"${cost:.2f}"
        elif cost < 0.0005:
            return f"less than \u2152 \u00A2"
        else:
            return f"{cost * 100:.1f} \u00A2"

    def print_cost(self) -> None:
        if (cost := self.model.get_cost_of_current_chat()) < 0.01:
            return
        message = f"cost: {self.get_cost_str(cost)}"
        self.console.print(message, justify="right", style=COST_STYLE)
        """CREDIT: The idea to print costs on the right was taken from https://github.com/kharvd/gpt-cli"""

    def exit_program(self) -> None:
        print(CLEAR_CURRENT_LINE)
        self.console.width = get_term_width()
        system("clear")
        self.total_cost += self.model.get_cost_of_current_chat()
        message = f"total session cost: {self.get_cost_str(self.total_cost)}"
        self.console.print(
            message,
            justify="right",
            style=COST_STYLE,
        )
        exit(0)

    def render_greeting(self) -> None:
        system("clear")
        greeting_left = Text(
            GREETING_TEXT, justify="left", style=GREETING_PANEL_TEXT_STYLE
        )
        greeting_right = Text(
            f"{self.model.model_name}", justify="right", style=GREETING_PANEL_TEXT_STYLE
        )

        # Create a panel with the help text, you can customize the box style
        columns = Columns([greeting_left, greeting_right], expand=True)
        panel = Panel(
            columns,
            box=box.ROUNDED,
            style=GREETING_PANEL_OUTLINE_STYLE,
            title_align="left",
        )
        self.console.print(panel)

    def enable_multiline(self) -> None:
        print(
            MOVE_UP_ONE_LINE_AND_GOTO_LEFTMOST_POS,
            CLEAR_CURRENT_LINE,
            end="",
        )
        self.multiline = True

    def one_shot_and_quit(self) -> None:
        """Take a prompt from stdin (most likely a unix pipe), print model output to stdout and exit program"""
        output = ""
        prompt = stdin.read().strip()
        try:
            for text in self.model.prompt_and_stream_completion(prompt):
                output += text
            print(output, flush=True)
        except:
            exit(2)
        exit(0)
