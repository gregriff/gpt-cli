from sys import stdout

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.theme import Theme

from terminal import *


# TODO: use this for consistency. Eventually load these from db.
# custom_theme = Theme({
#     "info": "dim cyan",
#     "warning": "magenta",
#     "danger": "bold red"
# })

def md_theme(text_color: str):
    return Theme({
        "markdown": text_color,
        "markdown.code": 'bold blue'
    })


class Output:
    """
    Encapsulates all the data needed to update the terminal with a chat completion generator response.
    Keeps track of how many lines are printed to the screen and pretty-prints everything.
    """

    def __init__(self, color, theme):
        self.full_response = []
        self.current_line_length = 0
        self.total_num_of_lines = 0
        self.terminal_width = TERM_WIDTH
        self.max_text_width = TERM_WIDTH - 2

        self.console = Console(width=self.terminal_width, theme=md_theme(color))
        self.color = color  # color of normal text
        self.theme = theme

    def print(self, text: str):
        # TODO: if errors with markdown rendering, play with overflow and softwrap
        self.console.print(Text(text, style=self.color, overflow='ignore', ), soft_wrap=True, end='')

    def update(self, text: str):
        """
        Given a partial response from openai api, print it, ensuring it is wrapped to the max text width, and keep
        track of the number of lines total so far
        """
        # ensure newlines are counted
        newlines_in_text = text.count('\n')
        if newlines_in_text:
            self.total_num_of_lines += newlines_in_text
            chars_after_last_newline = len(text.split('\n')[-1])
            self.current_line_length = chars_after_last_newline
        else:
            self.current_line_length += len(text)

        # wrap text if needed
        if self.current_line_length >= self.max_text_width:
            slice_idx = self.max_text_width - self.current_line_length
            safe_to_print = text[:slice_idx:]
            rest_of_text = text[slice_idx::]
            self.print(f'{safe_to_print}\n{rest_of_text}')
            self.total_num_of_lines += 1
            self.current_line_length = len(rest_of_text)
        else:
            self.print(text)
        self.full_response.append(text)

    def replace_with_markdown(self):
        """
        Called after an entire response has been printed to the screen, this function deletes the entire response
        using ANSI codes and then renders it in markdown
        """
        stdout.write(CLEAR_CURRENT_LINE)
        for _ in range(self.total_num_of_lines):
            stdout.write(CLEAR_LINE_ABOVE_CURRENT)
        markdown_obj = Markdown(self.final_response(), style=self.color, code_theme=self.theme)
        self.console.print(markdown_obj, '\n', overflow='fold', highlight=False)

    def final_response(self) -> str:
        return "".join(self.full_response)