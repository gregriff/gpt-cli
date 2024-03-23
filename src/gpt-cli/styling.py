from rich.theme import Theme

### Decorations
GREETING_TEXT = "gpt-cli"
GREETING_PANEL_TEXT_STYLE = "dim bold yellow"  # Any Rich Style: https://rich.readthedocs.io/en/stable/style.html
GREETING_PANEL_OUTLINE_STYLE = "dim blue"
CLEAR_HISTORY_STYLE = "dim bold blue"
ERROR_STYLE = "yellow"
COST_STYLE = "dim"

### Output
MARKDOWN_CODE = "bold blue"
DEFAULT_TEXT_COLOR = "green"
DEFAULT_CODE_THEME = "native"  # any pygments code theme


def md_theme(text_color: str):
    """
    Overrides Rich's default text theme with Rich tokens.
    Instead of a string, this func could accept a Rich.styles.Style obj
    """
    return Theme({"markdown": text_color, "markdown.code": MARKDOWN_CODE})


# Example
# custom_theme = Theme({
#     "info": "dim cyan",
#     "warning": "magenta",
#     "danger": "bold red"
# })
