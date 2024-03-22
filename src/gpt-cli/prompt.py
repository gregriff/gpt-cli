import sys
from functools import partial
from os import system
from termios import tcflush, TCIFLUSH
from typing import Callable

from openai import OpenAIError

from prompt_toolkit import PromptSession
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from rich import box
from rich.columns import Columns
from rich.panel import Panel

from rich.style import Style
from rich.console import Console
from rich.text import Text
from anthropic import AnthropicError
from terminal import *
from output import Output
from models import LLM
from styling import *


class Prompt:
    def __init__(
        self,
        model: LLM,
        text_color: str,
        code_theme: str,
        refresh_rate: int,
    ):
        self.model = model
        self.count = 0
        self.tokens = 0
        self.total_cost = 0
        self.terminal_width = TERM_WIDTH
        self.refresh_rate = refresh_rate

        self.session = PromptSession(editing_mode=EditingMode.VI)
        self.console = Console(width=TERM_WIDTH, theme=md_theme(text_color))
        self.prompt = HTML(
            f"<b><ansicyan>?</ansicyan></b> <b><ansibrightyellow>></ansibrightyellow></b> "
        )
        self.bindings = KeyBindings()

        self.color = Style.parse(text_color)
        self.theme = code_theme

        # lookup table to run functions on certain prompts (if user presses enter)
        self.special_case_functions: dict[str, Callable] = {
            kw: function
            for keywords, function in [
                (EXIT_COMMANDS, self.exit_program),
                (CLEAR_COMMANDS, self.clear_history),
            ]
            for kw in keywords
        }

    def run(self, initial_prompt: str | None = None):
        """
        Main loop to run REPL. CTRL+C to cancel current completion and CTRL+D to quit.
        """
        # fmt: off
        system("clear")
        greeting_left = Text("gpt-cli", justify="left", style=GREETING_PANEL_TEXT_STYLE)
        greeting_right = Text(f"{self.model.name}", justify="right", style=GREETING_PANEL_TEXT_STYLE)

        # Create a panel with the help text, you can customize the box style
        columns = Columns([greeting_left, greeting_right], expand=True)
        panel = Panel(columns, box=box.ROUNDED, style=GREETING_PANEL_OUTLINE_STYLE, title_align="left")
        self.console.print(panel)

        while True:
            try:
                if (user_input := initial_prompt) is None:
                    user_input = self.session.prompt(self.prompt).strip()
                cleaned_input = user_input.casefold()
                prompt_the_llm = partial(self.prompt_llm, user_input)
                self.special_case_functions.get(cleaned_input, prompt_the_llm)()
            except KeyboardInterrupt:
                print()
                continue
            # TODO: this does not do anything while response is streaming...
            except EOFError:  # ctrl + D
                self.exit_program()
            finally:
                initial_prompt = None
                if not sys.stdin.closed:
                    tcflush(sys.stdin, TCIFLUSH)  # discard any user input while response was printing
        # fmt: on

    def prompt_llm(self, user_input: str):
        # fmt: off
        print(RESET)
        self.model.messages.append({"role": "user", "content": user_input})
        try:
            with Output(self.console, self.color, self.theme, self.refresh_rate) as output:
                for text in self.model.stream_completion():
                    output.print(text)
        except (OpenAIError, AnthropicError) as e:
            self.console.print(f"API Error: {str(e)}\n", style=ERROR_STYLE)
            return
        # fmt: on

        self.model.messages.append(
            {"role": "assistant", "content": output.full_response}
        )

        ending_line = (
            f"Price: ${total_price:.3f}"
            if (total_price := self.model.get_cost_of_chat_history()) >= 0.01
            else ""
        )
        self.console.print(ending_line, justify="right", style=COST_STYLE)
        self.count += 1

    def clear_history(self) -> None:
        message = f"\nhistory cleared: {self.count} messages total\n"
        self.console.print(message, style=CLEAR_HISTORY_STYLE)
        self.total_cost += self.model.get_cost_of_chat_history()
        self.model.reset()
        self.count = 0

    def exit_program(self):
        print(CLEAR_CURRENT_LINE)
        system("clear")
        message = f"total cost of last session: ${self.total_cost:.3f}"
        self.console.print(
            message,
            justify="right",
            style=COST_STYLE,
        )
        exit(0)
