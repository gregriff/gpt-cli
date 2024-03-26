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
        self.refresh_rate = refresh_rate
        self.multiline = False

        self.session = PromptSession(editing_mode=EditingMode.VI)
        self.console = Console(width=get_term_width(), theme=md_theme(text_color))
        self.bindings = KeyBindings()

        self.prompt = PROMPT_LEAD
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

    def run(self, initial_prompt: str | None = None):
        """
        Main loop to run REPL. CTRL+C to cancel current completion and CTRL+D to quit.
        """
        # fmt: off
        system("clear")
        greeting_left = Text(GREETING_TEXT, justify="left", style=GREETING_PANEL_TEXT_STYLE)
        greeting_right = Text(f"{self.model.model_name}", justify="right", style=GREETING_PANEL_TEXT_STYLE)

        # Create a panel with the help text, you can customize the box style
        columns = Columns([greeting_left, greeting_right], expand=True)
        panel = Panel(columns, box=box.ROUNDED, style=GREETING_PANEL_OUTLINE_STYLE, title_align="left")
        self.console.print(panel)

        while True:
            try:
                # TODO: add "raw" mode for one-shot unformatted outputs, for scripting
                if (user_input := initial_prompt) is None:
                    style = MULTILINE_PROMPT_STYLE if self.multiline else PROMPT_STYLE
                    user_input = self.session.prompt(self.prompt, style=style, multiline=self.multiline).strip()
                disable_input()
                cleaned_input = user_input.casefold()
                if not cleaned_input:
                    continue  # prevent API error
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

    def prompt_llm(self, user_input: str):
        # fmt: off
        print(RESET)
        self.console.width = get_term_width()  # adjust printing if user has resized their terminal
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
            f"Price: ${total_cost:.3f}"
            if (total_cost := self.model.get_cost_of_current_chat() >= 0.01)
            else ""
        )
        self.console.print(ending_line, justify="right", style=COST_STYLE)
        self.count += 1
        self.multiline = False

    def clear_history(self) -> None:
        message = f"\nhistory cleared: {self.count} messages total\n"
        self.console.print(message, style=CLEAR_HISTORY_STYLE)
        self.total_cost += self.model.get_cost_of_current_chat()
        self.model.reset()
        self.count = 0

    def exit_program(self) -> None:
        print(CLEAR_CURRENT_LINE)
        system("clear")
        self.total_cost += self.model.get_cost_of_current_chat()
        message = f"total cost of last session: ${self.total_cost:.3f}"
        self.console.print(
            message,
            justify="right",
            style=COST_STYLE,
        )
        exit(0)

    def enable_multiline(self) -> None:
        print(
            MOVE_UP_ONE_LINE_AND_GOTO_LEFTMOST_POS,
            CLEAR_CURRENT_LINE,
            end="",
        )
        self.multiline = True
