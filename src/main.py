from typing import Annotated, Optional

from pygments import styles
from rapidfuzz import fuzz, process
from typer import Argument, BadParameter, Option, Typer

from config import default_max_tokens, default_model, default_system_message
from models import AnthropicModel, OpenAIModel
from repl import REPL
from styling import DEFAULT_CODE_THEME, DEFAULT_TEXT_COLOR

app = Typer(name="gpt-cli", add_completion=False)


def validate_code_styles(value: str):
    if value not in (valid_styles := list(styles.get_all_styles())):
        raise BadParameter(f"{value} \n\nChoose from {valid_styles}")
    return value


def validate_llm_model(value: str):
    """use fuzzy matching to choose model from user input"""
    valid_models = OpenAIModel.model_names + AnthropicModel.model_names
    closest_model, score, _ = process.extractOne(
        value, valid_models, scorer=fuzz.WRatio
    )

    # tweak this as needed
    if score < 75:
        raise BadParameter(f"{value} \n\nChoose from {valid_models}")
    return closest_model


# fmt: off


@app.command()
def main(
    model: Annotated[str, Argument(callback=validate_llm_model, help="OpenAI or Anthropic model to use")] = default_model,
    prompt: Annotated[Optional[str], Option("--prompt", "-p", help="Initial prompt. Omit for blank REPL")] = None,
    reasoning_mode: Annotated[str, Option("--reasoning", "-r", help="Enable reasoning on supported models")] = "false",
    system_message: Annotated[str, Option("--system-message", "-s", help="Heavily influences responses from model")] = default_system_message,
    code_theme: Annotated[str, Option("--code-theme", "-t", callback=validate_code_styles, help="Style of Markdown code blocks. Any Pygments `code_theme`")] = DEFAULT_CODE_THEME,
    text_color: Annotated[str, Option("--text-color", "-c", help="Color of plain text from responses. Most colors supported")] = DEFAULT_TEXT_COLOR,
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

    reasoning = reasoning_mode.lower() in ('t', 'y', 'yes', 'true')
    repl = REPL(llm, text_color.lower(), code_theme.lower(), reasoning)
    repl.render_greeting()
    repl.run(prompt)


if __name__ == "__main__":
    app()
