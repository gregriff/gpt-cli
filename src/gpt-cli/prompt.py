from functools import partial
from typing import Callable

from openai import OpenAI, APIConnectionError, Stream
from openai.types.chat import ChatCompletionChunk

from prompt_toolkit import PromptSession
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from rich import box
from rich.columns import Columns
from rich.panel import Panel

from rich.style import Style
from rich.console import Console
from rich.text import Text
from rich.theme import Theme
from tiktoken import encoding_for_model

from terminal import *
from output import Output
from costs import gpt_pricing


# example_style = Style.from_dict({
#     'toolbar': 'bg:#002b36'
# })


def md_theme(text_color: str):
    """
    Overrides Rich's default text theme with Rich tokens.
    Instead of a string, this func could accept a Rich.styles.Style obj
    """
    return Theme({"markdown": text_color, "markdown.code": "bold blue"})


class Prompt:
    def __init__(
        self,
        text_color: str,
        code_theme: str,
        sys_msg: dict,
        api_key: str,
        refresh_rate: int,
        prompt_args: dict,
    ):
        self.system_message = sys_msg
        self.client = OpenAI(api_key=api_key)
        self.prompt_args = prompt_args
        self.model = prompt_args["model"]

        self.messages = [
            sys_msg,
        ]
        self.count = 0
        self.tokens = 0
        self.price_per_token = gpt_pricing(self.model, prompt=True)
        self.total_cost = 0
        self.terminal_width = TERM_WIDTH
        self.refresh_rate = refresh_rate

        self.session = PromptSession(editing_mode=EditingMode.VI)
        self.console = Console(width=TERM_WIDTH, theme=md_theme(text_color))
        self.prompt = HTML(
            f"<b><ansicyan>?</ansicyan></b> <b><ansibrightyellow>></ansibrightyellow></b> "
        )
        self.bindings = KeyBindings()

        self.color = Style.parse(text_color)
        self.theme = code_theme

        # lookup table to run functions on certain prompts (if user presses enter)
        self.special_case_functions: dict[str, Callable] = {
            kw: function
            for keywords, function in [
                (
                    ("exit", "e", "q", "quit"),
                    partial(exit_program, self.console, self.total_cost),
                ),
                (("c", "clear"), self.clear_history),
                (("sys", "system", "message"), self.change_system_msg),
                (("temp", "temperature"), self.change_temp),
            ]
            for kw in keywords
        }

    def run(self, initial_prompt: str | None = None, *args):
        """
        Main loop to run REPL. CTRL+C to cancel current completion and CTRL+D to quit.
        """
        system("clear")
        greeting_left = Text("gpt-cli", justify="left", style="dim bold yellow")
        greeting_right = Text(
            f"{prompt_arguments.get('model')}", justify="right", style="dim bold yellow"
        )

        # Create a panel with the help text, you can customize the box style
        columns = Columns([greeting_left, greeting_right], expand=True)
        # combined_greeting = Text.assemble(greeting_left, greeting_right, justify='default')
        # pre_title = Text(f'gpt-cli', style='bold blue')
        # title = Text('gpt-cli', style='dim')
        # greeting = Text(f'{prompt_arguments.get("model")}', style='bold blue')
        panel = Panel(columns, box=box.ROUNDED, style="dim blue", title_align="left")

        # Print the panel to the console
        self.console.print(panel, end="")
        self.console.print()

        while True:
            try:
                user_input: str = (
                    initial_prompt
                    if initial_prompt is not None
                    else self.session.prompt(self.prompt)
                ).strip()
                cleaned_input = user_input.casefold()
                prompt_the_llm = partial(self.prompt_llm, user_input)
                self.special_case_functions.get(cleaned_input, prompt_the_llm)()
            except KeyboardInterrupt:
                print()
                continue
            except EOFError:  # ctrl + D
                exit_program(self.console, self.total_cost)
                exit(0)
            finally:
                initial_prompt = None

    def prompt_llm(self, user_input: str):
        print(RESET)
        self.messages.append({"role": "user", "content": user_input})
        try:
            response_stream: Stream[
                ChatCompletionChunk
            ] = self.client.chat.completions.create(
                messages=self.messages, **self.prompt_args
            )
        except APIConnectionError as e:
            self.console.print(
                f"Could not connect to API. Error: {str(e)}\n", style="yellow"
            )
            return

        with Output(self.console, self.color, self.theme, self.refresh_rate) as output:
            for chunk in response_stream:
                for choice in chunk.choices:
                    chunk_text = choice.delta.content or ""
                    output.print(chunk_text)

        self.messages.append({"role": "assistant", "content": output.full_response})

        ending_line = (
            f"Price: ${total_price:.3f}"
            if (total_price := self.get_current_cost()) >= 0.01
            else ""
        )
        self.console.print(ending_line, justify="right", style="dim")
        self.count += 1

    def clear_history(self, auto=False) -> None:
        if not auto or self.count:
            self.console.print(
                f"\nhistory cleared: {self.count} messages total\n",
                style="dim bold blue",
            )
        self.total_cost += self.get_current_cost()
        self.messages = [
            self.system_message,
        ]
        self.count = 0

    def change_system_msg(self) -> None:
        prompt = input(f"\n{BOLD + RED} new system message:\n{CYAN} > ")
        new_message = prompt.casefold().strip()
        self.system_message["content"] = new_message
        self.console.print(
            f'\nsystem message set to: "{new_message}"', style="dim bold yellow"
        )
        self.clear_history(auto=True)

    def change_temp(self):
        prompt = input(f"\n{BOLD + RED}new temperature:\n{CYAN}> ")
        new_temp = float(prompt.casefold().strip())
        if 0.0 < new_temp < 1.0:
            self.prompt_args["temperature"] = new_temp
            reply = f'\ntemperature set to: "{new_temp}"'
        else:
            reply = f"\ninvalid temperature: {new_temp}, must be 0 < temp < 1"
        self.console.print(reply, style="dim bold yellow")

    def num_tokens(self) -> int:
        """
        Get the total number of tokens used in the current chat history given OpenAI's token
        counting package `tiktoken`
        """
        encoding = encoding_for_model(self.prompt_args["model"])
        num_tokens = 0
        for message in self.messages:
            # every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += 4
            for role, text in message.items():
                assert isinstance(text, str)
                num_tokens += len(encoding.encode(text))
                if role == "name":  # if there's a name, the role is omitted
                    num_tokens -= 1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens

    def get_current_cost(self) -> float:
        return self.num_tokens() * self.price_per_token


def exit_program(console: Console, total_cost: int):
    print(CLEAR_CURRENT_LINE)
    system("clear")
    console.print(
        f"total cost of last session: ${total_cost:.3f}",
        justify="right",
        style="dim",
    )
    exit(0)
    # TODO: use token algo to print total tokens in session
