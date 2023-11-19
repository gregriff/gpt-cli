from enum import Enum
from typing import Optional, Annotated

import typer
from pygments import styles

from config import CONFIG, default_system_message, prompt_arguments
from terminal import greeting
from prompt import Prompt

# TODO: update screen rendering so that updates to not mess with auto-scrolling relating to terminal height:
#   - look at reference projects for solutions
#   - look into storing info about recently rendered text. If it does not involve markdown, strictly append to screen.
#     if it does involve markdown, rewrite only that section? Someone must have already implemented this.
#
# update openai package:
#   - async is now supported. Judge if this would be worth it. Prompt toolkit and maybe rich support this
# integrate typer as the frontend:
#   - replace all prompt-toolkit and hardcoded keyboard actions into typer, or maybe just wrap startup functionality with
#     typer and keep in-app keyboard interactions the same
app = typer.Typer(name="gpt-cli")


def validate_code_styles(value: str):
    if value not in (valid_styles := list(styles.get_all_styles())):
        raise typer.BadParameter(f"{value} \n\nChoose from {valid_styles}")


code_styles = tuple(styles.get_all_styles())
CodeStyles = Enum("code styles", code_styles)


@app.command()
def main(
    prompt: Annotated[str, typer.Argument()] = None,
    system_message: Optional[str] = default_system_message["content"],
    code_style: Annotated[
        Optional[str], typer.Option(callback=validate_code_styles)
    ] = "native",
    # code_style: CodeStyles = CodeStyles.native,
    text_color: Annotated[str, typer.Option()] = "green",
):
    # TODO: use a cli lib to parse args for one time run of app (dont save settings) with custom:
    #   - temp
    #   - model
    #   - theme
    #
    # ensure cli lib generates man pages
    #
    # TODO Flags:
    #   "-o" to print full response to stdout and quit program'
    api_key = CONFIG.get("lapetusAPIkey")

    default_system_message["content"] = system_message

    greeting()
    # stata-dark. dracula. native. inkpot. vim.
    _prompt = Prompt(
        text_color, code_style, default_system_message, api_key, prompt_arguments
    )
    _prompt.run(prompt)


if __name__ == "__main__":
    # typer.run(main)
    app()

# long term todos:
# - menu commands in bottom toolbar. fullpage settings menu
# - asyncio used to implement multiple prompts at once. Bottom menu bar would allow user
#   to switch between tabs, giving them a notification when a response on a background tab has completed
#       - could also dive really deep into rich and try to render markdown in real time while waiting for network io
