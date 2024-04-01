from prompt_toolkit.styles import Style as ptkStyle
from rich.theme import Theme

# add an entry with a class name of empty string to color user input
PROMPT_STYLE = ptkStyle(
    [("primary", "ansibrightcyan"), ("secondary", "ansibrightyellow")]
)
MULTILINE_PROMPT_STYLE = ptkStyle(
    [("primary", "ansicyan"), ("secondary", "ansipurple")]
)

# use the classes above to build a prompt lead
PROMPT_LEAD = [
    ("class:primary", "? "),
    ("class:secondary", "> "),
]

### Decorations
GREETING_TEXT = "gpt-cli"
GREETING_PANEL_TEXT_STYLE = "dim bold yellow"  # Any Rich Style: https://rich.readthedocs.io/en/stable/style.html
GREETING_PANEL_OUTLINE_STYLE = "dim blue"
CLEAR_HISTORY_STYLE = "dim bold blue"
ERROR_STYLE = "yellow"
COST_STYLE = "dim"
SPINNER = "point"  # Run `python -m rich.spinner` to see all options
SPINNER_STYLE = "dim green"

### Output
MARKDOWN_CODE = "bold blue"
DEFAULT_TEXT_COLOR = "green"

# any pygments code theme: https://pygments.org/styles/
# cool themes: stata-dark. dracula. native. inkpot. vim.
DEFAULT_CODE_THEME = "native"


def md_theme(text_color: str):
    """
    Overrides Rich's default text theme with Rich tokens.
    Instead of a string, this func could accept a Rich.styles.Style obj
    """
    return Theme({"markdown": text_color, "markdown.code": MARKDOWN_CODE})
