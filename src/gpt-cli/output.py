from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.style import Style
from rich.text import Text
# from rich.theme import Theme
from rich.live import Live

from terminal import *


# TODO: use this for consistency. Eventually load these from db.
# custom_theme = Theme({
#     "info": "dim cyan",
#     "warning": "magenta",
#     "danger": "bold red"
# })


# def md_theme(text_color: str):
#     """
#     Overrides Rich's default text theme with Rich tokens.
#     Instead of a string, this func could accept a Rich.styles.Style obj
#     """
#     return Theme({"markdown": text_color, "markdown.code": "bold blue"})


class Output:
    """
    Encapsulates all the data needed to update the terminal with a chat completion generator response.
    Keeps track of how many lines are printed to the screen and pretty-prints everything.
    """

    def __init__(self, console: Console, color: Style, theme, refresh_rate: int):
        self.full_response = ""
        self.terminal_width = TERM_WIDTH

        self.console = console
        self.live: Optional[Live] = None
        self.color = color  # color of normal text
        self.pygments_code_theme = theme
        self.refresh_rate = refresh_rate

    def __enter__(self) -> "Output":
        self.live = Live(
            console=self.console,
            refresh_per_second=self.refresh_rate,
            auto_refresh=False,
            vertical_overflow="ellipsis",
        )
        self.live.__enter__()
        return self

    def __exit__(self, *args):
        self.live.__exit__(*args)
        self.console.print()

    def print(self, text: str, markdown=True):
        self.full_response += text
        if markdown:
            self.live.update(
                Markdown(
                    self.full_response,
                    code_theme=self.pygments_code_theme,
                    style=self.color,
                ),
                refresh=True,
            )
        else:
            self.console.print(
                Text(
                    text,
                    style=self.color,
                    overflow="ignore",
                ),
                soft_wrap=True,
                end="",
            )
