from typing import Optional, Annotated

from typer import Option, Typer, BadParameter, Argument
from pygments import styles

from config import (
    default_system_message,
    CONFIG,
)
from prompt import Prompt
from models import OpenAIModel, AnthropicModel, anthropic_models, openai_models

openai_apikey = CONFIG.get("openaiAPIKey")
anthropic_apikey = CONFIG.get("anthropicAPIKey")

app = Typer(name="gpt-cli", add_completion=False)


def validate_code_styles(value: str):
    if value not in (valid_styles := list(styles.get_all_styles())):
        raise BadParameter(f"{value} \n\nChoose from {valid_styles}")
    return value


def validate_llm_model(value: str):
    valid_models = openai_models + anthropic_models
    if value not in valid_models:
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
    prompt: Annotated[str, Argument(help="Quoted text to prompt LLM. Leave blank for fresh REPL", metavar="[PROMPT]")] = None,
    model: Annotated[Optional[str], Option("--model", "-m", callback=validate_llm_model, help="OpenAI or Anthropic model to use")] = "gpt-4-turbo-preview",
    system_message: Annotated[Optional[str], Option(help="Influences all subsequent output (GPT only")] = default_system_message["content"],
    code_theme: Annotated[Optional[str], Option(callback=validate_code_styles, help="Style of Markdown code blocks. Any Pygments `code_theme`")] = "native",
    text_color: Annotated[str, Option(help="Color of plain text from responses. Most colors supported")] = "green",
    refresh_rate: Annotated[int, Option("--refresh-rate", "-R", help="Printing frequency from response buffer in Hz")] = 8,
):
    if model in openai_models:
        llm = OpenAIModel(name=model, api_key=openai_apikey, system_message=system_message)
    else:
        llm = AnthropicModel(name=model, api_key=anthropic_apikey)

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
