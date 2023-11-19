from typing import Optional

from rich.style import Style
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.theme import Theme
from rich.live import Live

from terminal import *


# TODO: use this for consistency. Eventually load these from db.
# custom_theme = Theme({
#     "info": "dim cyan",
#     "warning": "magenta",
#     "danger": "bold red"
# })


def md_theme(text_color: Style):
    return Theme({"markdown": text_color, "markdown.code": "bold blue"})


class Output:
    """
    Encapsulates all the data needed to update the terminal with a chat completion generator response.
    Keeps track of how many lines are printed to the screen and pretty-prints everything.
    """

    def __init__(self, color: Style, theme):
        self.full_response = ""
        self.terminal_width = TERM_WIDTH

        self._console = Console(width=self.terminal_width, theme=md_theme(color))
        self.live: Optional[Live] = None
        self.color = color  # color of normal text
        self.theme = theme

    def __enter__(self) -> "Output":
        self.live = Live(
            console=self._console,
            refresh_per_second=8,
            auto_refresh=False,
            vertical_overflow="ellipsis",
        )
        self.live.__enter__()
        return self

    def __exit__(self, *args):
        self.live.__exit__(*args)
        self._console.print()

    def print(self, text: str, markdown=True):
        self.full_response += text
        if markdown:
            self.live.update(
                Markdown(
                    self.full_response,
                    # code_theme=self.theme,
                    style=self.color,
                ),
                refresh=True,
            )
        else:
            self._console.print(
                Text(
                    text,
                    style=self.color,
                    overflow="ignore",
                ),
                soft_wrap=True,
                end="",
            )
