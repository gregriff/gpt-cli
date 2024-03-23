from typing import Optional, Annotated

from typer import Option, Typer, BadParameter, Argument
from pygments import styles

from config import (
    default_system_message,
    CONFIG,
)
from prompt import Prompt
from models import OpenAIModel, AnthropicModel
from styling import DEFAULT_CODE_THEME, DEFAULT_TEXT_COLOR

openai_apikey = CONFIG.get("openaiAPIKey")
anthropic_apikey = CONFIG.get("anthropicAPIKey")

app = Typer(name="gpt-cli", add_completion=False)


def validate_code_styles(value: str):
    if value not in (valid_styles := list(styles.get_all_styles())):
        raise BadParameter(f"{value} \n\nChoose from {valid_styles}")
    return value


def validate_llm_model(value: str):
    if value not in (
        valid_models := OpenAIModel.model_names + AnthropicModel.model_names
    ):
        raise BadParameter(f"{value} \n\nChoose from {valid_models}")
    return value


# TODO:
#  - BETTER ERROR HANDLING from API docs
#  -
#  CLI features
#  - one word for argv[2] needs to be treated as an argument and not a prompt
#  - more commands:
#  - argv[2] command alias for models ex. `llm opus`:
#       impl this by hardcoding aliases, then searching model keys for the alias substring
#  - `llm update` fetches updated models from sources
#  - `llm list` lists available models
#  - `llm -m[--model] [model_name]` use specified model for this session
#  - instructions for keyboard shortcuts in help menu
#  - pipe support. research how to capture stdin as soon as app starts, --pipe option to output raw response and quit
#  -
#   long term todos:
#   - DOCKER BUILD, ruff, uv, pipx?
#   - menu commands in bottom toolbar
# fmt: off


@app.command()
def main(
    prompt: Annotated[str, Argument(help="Initial prompt. Leave blank for fresh REPL", metavar="[PROMPT]")] = None,
    model: Annotated[Optional[str], Option("--model", "-m", callback=validate_llm_model, help="OpenAI or Anthropic model to use")] = "gpt-4-turbo-preview",
    system_message: Annotated[Optional[str], Option(help="Heavily influences responses from model")] = default_system_message,
    code_theme: Annotated[Optional[str], Option(callback=validate_code_styles, help="Style of Markdown code blocks. Any Pygments `code_theme`")] = DEFAULT_CODE_THEME,
    text_color: Annotated[str, Option(help="Color of plain text from responses. Most colors supported")] = DEFAULT_TEXT_COLOR,
    refresh_rate: Annotated[int, Option("--refresh-rate", "-R", help="How frequently streamed responses are printed to the screen (Hz)")] = 8,
):
    # TODO: make this a factory given the model name
    if model in OpenAIModel.model_names:
        llm = OpenAIModel(name=model, api_key=openai_apikey, system_message=system_message)
    else:
        llm = AnthropicModel(name=model, api_key=anthropic_apikey, system_message=system_message)

    # cool themes: stata-dark. dracula. native. inkpot. vim.
    _prompt = Prompt(
        llm,
        text_color.casefold(),
        code_theme.casefold(),
        int(refresh_rate),
    )
    _prompt.run(prompt)

# fmt: on


if __name__ == "__main__":
    app()
