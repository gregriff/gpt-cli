from typing import Optional, Self

from rich import status
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.padding import Padding
from rich.style import Style

from styling import OUTPUT_PADDING, SPINNER, SPINNER_STYLE


class Output:
    """
    Encapsulates all the data needed to update the terminal with a chat completion generator response
    with markdown formatting
    """

    """CREDIT: The idea and implementation to print text in markdown live, as it gets sent from server,
    was taken from the "StreamingMarkdownPrinter" class from https://github.com/kharvd/gpt-cli"""

    def __init__(self, console: Console, color: Style, theme: str):
        self.full_response = ""

        self.console = console
        self.live: Optional[Live] = None
        self.color = color  # color of normal text
        self.pygments_code_theme = theme
        self.loading_response = True

        # TODO: use status.Status internals to impl padding around spinner, so that we can use left padding. Also pad
        #   right side of prompt
        self.spinner = status.Status(
            Padding("", OUTPUT_PADDING), spinner=SPINNER, spinner_style=SPINNER_STYLE
        )

    def __enter__(self) -> Self:
        self.spinner.__enter__()
        self.console.print()
        return self

    def __exit__(self, *args):
        if self.live is None:
            return  # if user CTRL+D during loading spinner
        self.live.__exit__(*args)
        self.console.print()

    def print(self, text: str) -> None:
        """should only be used to print LLM responses"""

        if self.loading_response:  # this will only run once, on first API reply
            # must exit this before starting Live or else cursor glitches out
            self.spinner.__exit__(None, None, None)
            self.live = Live(
                console=self.console,
                auto_refresh=False,
                vertical_overflow="ellipsis",
            )
            self.loading_response = False
            self.live.__enter__()

        self.full_response += text
        self.live.update(
            Markdown(
                self.full_response,
                code_theme=self.pygments_code_theme,
                style=self.color,
            ),
            refresh=True,
        )
