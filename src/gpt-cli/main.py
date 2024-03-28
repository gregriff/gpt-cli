from typing import Optional, Annotated

from typer import Option, Typer, BadParameter, Argument
from pygments import styles

from config import default_system_message, default_max_tokens
from repl import REPL
from models import OpenAIModel, AnthropicModel
from styling import DEFAULT_CODE_THEME, DEFAULT_TEXT_COLOR

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
#  - use regex for validation of -m option value to choose between models
#  - `llm update` fetches updated models from sources
#  - `llm list` lists available models
#  - instructions for keyboard shortcuts in help menu
#  -
#   long term todos:
#   - DOCKER BUILD, ruff, uv
# fmt: off


@app.command()
def main(
    prompt: Annotated[str, Argument(help="Initial prompt. Leave blank for fresh REPL", metavar="[PROMPT]")] = None,
    model: Annotated[Optional[str], Option("--model", "-m", callback=validate_llm_model, help="OpenAI or Anthropic model to use")] = "gpt-4-turbo-preview",
    system_message: Annotated[Optional[str], Option(help="Heavily influences responses from model")] = default_system_message,
    code_theme: Annotated[Optional[str], Option(callback=validate_code_styles, help="Style of Markdown code blocks. Any Pygments `code_theme`")] = DEFAULT_CODE_THEME,
    text_color: Annotated[str, Option(help="Color of plain text from responses. Most colors supported")] = DEFAULT_TEXT_COLOR,
    max_tokens: Annotated[int, Option(help="Maximum length of each response")] = default_max_tokens
):
    # fmt: on
    model_args = dict(
        name=model,
        system_message=system_message,
        max_tokens=max_tokens
    )
    if model in OpenAIModel.model_names:
        llm = OpenAIModel(**model_args)
    else:
        llm = AnthropicModel(**model_args)

    repl = REPL(llm, text_color.casefold(), code_theme.casefold())
    repl.render_greeting()
    repl.run(prompt)


if __name__ == "__main__":
    app()
