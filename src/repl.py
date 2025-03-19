from functools import partial
from os import system
from sys import stdin
from typing import Callable

from anthropic import AnthropicError
from openai import OpenAIError
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from models import LLM
from output import Output
from styling import (
    CLEAR_HISTORY_STYLE,
    COST_STYLE,
    ERROR_STYLE,
    GREETING_PANEL_OUTLINE_STYLE,
    GREETING_PANEL_TEXT_STYLE,
    GREETING_TEXT,
    PROMPT_LEAD,
    md_theme,
)
from terminal import (
    CLEAR_COMMANDS,
    CLEAR_CURRENT_LINE,
    EXIT_COMMANDS,
    disable_input,
    get_term_width,
    reenable_input,
)


class REPL:
    def __init__(
        self, model: LLM, text_color: str, code_theme: str, reasoning_mode: bool
    ):
        self.model = model
        if not stdin.isatty():
            self.one_shot_and_quit()

        self.tokens = 0
        self.total_cost = 0

        self.console = Console(width=get_term_width(), theme=md_theme(text_color))
        self.console.set_window_title(self.model.model_name)
        self.stdin_settings = None

        self.color = Style.parse(text_color)
        self.reasoning_color = Style.parse("red")
        self.theme = code_theme
        self.reasoning_mode = reasoning_mode

        # lookup table to run functions on certain prompts (if user presses enter)
        self.special_case_functions: dict[str, Callable] = {
            kw: function
            for keywords, function in [
                (EXIT_COMMANDS, self.exit_program),
                (CLEAR_COMMANDS, self.clear_history),
            ]
            for kw in keywords
        }

    def run(self, initial_prompt: str | None = None) -> None:
        """
        Main loop to run REPL. CTRL+C to cancel current completion and CTRL+D to quit.
        """
        # fmt: off
        while True:
            try:
                if (user_input := initial_prompt) is None:
                    self.console.print(PROMPT_LEAD, end='')
                    user_input = input().strip()
                    if not user_input:
                        continue  # prevent API error
                self.stdin_settings = disable_input()
                cleaned_input = user_input.lower()
                prompt_the_llm = partial(self.prompt_llm, user_input)
                self.special_case_functions.get(cleaned_input, prompt_the_llm)()
            except KeyboardInterrupt:
                print()
                continue
            except EOFError:  # ctrl + D
                self.exit_program()
            finally:
                initial_prompt = None
                reenable_input(self.stdin_settings)
        # fmt: on

    def prompt_llm(self, user_input: str, reasoning_mode: bool = False) -> None:
        # adjust printing if user has resized their terminal
        self.console.width = get_term_width()

        try:
            with Output(
                self.console, self.color, self.reasoning_color, self.theme
            ) as output:
                with open("log.txt", "w") as file:
                    for is_reasoning, text in self.model.prompt_and_stream_completion(
                        user_input, self.reasoning_mode
                    ):
                        file.write(text)
                        output.print(text, is_reasoning)
        except (OpenAIError, AnthropicError) as e:
            self.console.print(f"API Error: {str(e)}\n", style=ERROR_STYLE)
            return

        self.print_cost()

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
            return "less than \u2152 \u00a2"
        else:
            return f"{cost * 100:.1f}\u00a2"

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
        # fmt: off
        message = f"session cost: {self.get_cost_str(self.total_cost)}" if self.total_cost else ""
        self.console.print(message, justify="right", style=COST_STYLE)
        exit(0)
        # fmt: on

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

    def one_shot_and_quit(self) -> None:
        """Take a prompt from stdin (most likely a unix pipe), print model output to stdout and exit program"""
        output = ""
        prompt = stdin.read().strip()
        try:
            for text in self.model.prompt_and_stream_completion(prompt):
                output += text
            print(output, flush=True)
        except Exception as _:
            exit(2)
        exit(0)
