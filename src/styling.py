from rich.text import Text
from rich.theme import Theme

PROMPT_LEAD = Text(" ? ", style="cyan") + Text(
    "> ", justify="left", overflow="fold", style="yellow"
)

### Decorations
GREETING_TEXT = "gpt-cli"
GREETING_PANEL_TEXT_STYLE = "dim bold yellow"  # Any Rich Style: https://rich.readthedocs.io/en/stable/style.html
GREETING_PANEL_OUTLINE_STYLE = "dim blue"
CLEAR_HISTORY_STYLE = "dim bold blue"
ERROR_STYLE = "yellow"
COST_STYLE = "dim"
SPINNER = "point"  # Run `python -m rich.spinner` to see all options
SPINNER_STYLE = ""

### Output
MARKDOWN_CODE = "bold blue"
DEFAULT_TEXT_COLOR = "green"
OUTPUT_PADDING = 0, 1, 0, 0  # css format, units in terminal columns
# known issue, padding of spinner is incomplete

# any pygments code theme: https://pygments.org/styles/
# cool themes: stata-dark. dracula. native. inkpot. vim.
DEFAULT_CODE_THEME = "native"


def md_theme(text_color: str):
    """
    Overrides Rich's default text theme with Rich tokens.
    Instead of a string, this func could accept a Rich.styles.Style obj
    """
    return Theme({"markdown": text_color, "markdown.code": MARKDOWN_CODE})
