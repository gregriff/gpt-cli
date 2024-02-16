from typing import Optional, Annotated

from typer import Option, Typer, BadParameter, Argument
from pygments import styles

from config import CONFIG, default_system_message, prompt_arguments
from prompt import Prompt

app = Typer(name="gpt-cli", add_completion=False)


def validate_code_styles(value: str):
    if value not in (valid_styles := list(styles.get_all_styles())):
        raise BadParameter(f"{value} \n\nChoose from {valid_styles}")
    return value


# code_styles = tuple(styles.get_all_styles())
# CodeStyles = Enum("code styles", code_styles)


# TODO:
#  - clean up these Annotated sections
#  -
#   save feature, use sqlite database:
#  - META + S to save current chat, option to name it in bottom toolbar
#  - `llm saved` to list saved chats with # prompts and summaries
#  - `llm load [tag]` to load the saved chat history of chat [tag]
#  - `llm delete [tag]`
#  -
#   long term todos:
#   - menu commands in bottom toolbar


@app.command()
def main(
    prompt: Annotated[
        str,
        Argument(
            help="For pipe support (incomplete). Leave blank for fresh REPL",
            metavar="[PROMPT]",
        ),
    ] = None,
    system_message: Annotated[
        Optional[str], Option(help="Influences all subsequent output from GPT")
    ] = default_system_message["content"],
    code_theme: Annotated[
        Optional[str],
        Option(
            callback=validate_code_styles,
            help="Style of Markdown code blocks. Any Pygments `code_theme`",
        ),
    ] = "native",
    # code_style: CodeStyles = CodeStyles.native,
    text_color: Annotated[
        str, Option(help="Color of plain text from responses. Most colors supported")
    ] = "green",
    refresh_rate: Annotated[
        int,
        Option(
            "--refresh-rate", "-R", help="Printing frequency from response buffer in Hz"
        ),
    ] = 8,
):
    api_key = CONFIG.get("lapetusAPIkey")

    default_system_message["content"] = system_message

    # stata-dark. dracula. native. inkpot. vim.
    _prompt = Prompt(
        text_color.casefold(),
        code_theme.casefold(),
        default_system_message,
        api_key,
        int(refresh_rate),
        prompt_arguments,
    )
    _prompt.run(prompt)


if __name__ == "__main__":
    app()
