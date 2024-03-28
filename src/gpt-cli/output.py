from typing import Optional

from rich import status
from rich.console import Console
from rich.markdown import Markdown
from rich.style import Style
from rich.text import Text
from rich.live import Live

from styling import SPINNER


class Output:
    """
    Encapsulates all the data needed to update the terminal with a chat completion generator response
    with markdown formatting
    """

    def __init__(self, console: Console, color: Style, theme):
        self.full_response = ""

        self.console = console
        self.live: Optional[Live] = None
        self.color = color  # color of normal text
        self.pygments_code_theme = theme
        self.loading_response = True

        # TODO: ensure this is properly integrated with live display to avoid cursor issues
        self.spinner = status.Status("", spinner=SPINNER)

    def __enter__(self) -> "Output":
        self.spinner.__enter__()
        self.live = Live(
            console=self.console,
            auto_refresh=False,
            vertical_overflow="ellipsis",
        )
        self.live.__enter__()
        self.console.print()
        return self

    def __exit__(self, *args):
        self.live.__exit__(*args)
        self.console.print()

    def print(self, text: str, markdown=True):
        if self.loading_response:
            self.loading_response = False
            self.spinner.__exit__(None, None, None)
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
            self.live.refresh()
