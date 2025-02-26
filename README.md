# gpt-cli

![preview](./docs/overview.gif)

---

## Overview

Access the most powerful LLMs from within the terminal.

##### Main Features

- Streamed responses with full Markdown rendering and [syntax highlighting](https://pygments.org/styles/)
- Intentionally minimal UI/UX with configurable styling
- Support for OpenAI and Anthropic chat models (reasoning coming soon)
  - Easily choose model with CLI option and API key
  - Highly extensible implementation
- Top-class terminal integration via escape codes

I created this out of curiosity of CLI/TUI development and because of the lack of free and convenient interfaces for LLMs.
Now a staple in my daily workflow as a rubber duck debugger and google alternative, I have found this CLI works great within one's IDE.

## Installation and Recommended Setup

Developed on MacOS and Ubuntu. All instructions will assume a unix-like OS with Python 3.11+ installed.

An OpenAI API key is required to access the GPT models and an Anthropic API key is needed for the Claude models. Both of these companies currently require paying for usage credits in advance,
so ensure you have an account with money loaded before using the CLI.

> **Sign up for OpenAI [here](https://platform.openai.com/account/api-keys) and Anthropic [here](https://www.anthropic.com/api)**.


Once you have you API keys, place them in a file named `env.json` in the project root directory like so:

`gpt-cli/env.json`
```json
{
  "openaiAPIKey": "12345678",
   "anthropicAPIKey": "87654321"
}
```

I prefer to install this app's dependencies to the system interpreter so that I can use a shell alias to run it at any time with no prior venv set up. In the terminal:

1. Ensure you are not using a venv: run `deactivate`
2. After cloning and inside the project directory, run `python -m pip install -r requirements.txt` to download all python packages.
3. Add shell alias and reload shell config to apply changes (assuming `bash` or `zsh`):
    ```shell
   config_file="${HOME}/.$(basename ${SHELL})rc" && \
   echo -e "\nalias llm='python3 ENTER_ABSOLUTE_PATH_TO_/gpt-cli/src/main.py_HERE'" >> "${config_file}" && \
   source "${config_file}"
   ```
Now no matter where your current working directory is, you can type `llm` in your terminal to start a GPT session!

## Configuration

> Note: All settings are documented in the [help page](docs/help.jpg), accessible by running with the help option: `llm --help` (assuming you have the shell alias described above)

##### System Message

This is extremely important to properly tailor to your use case. Heavily influences every response from the model. By default, it is _"You are a concise assistant to a software engineer"_,
but you can change this at any time via command line arguments or by editing the source code.

##### Colors

> `styling.py` contains many editable values to control the look of the program

Markdown code blocks can be rendered in any of the styles found [here](https://pygments.org/styles/) by setting the `--code-theme` option,
and the color of the plaintext responses can be set to most normal colors using `--text-color` (ex. `llm --text-color=orange`)

## Usage

![help page](docs/help.jpg)

###### Controls

The program is a simple REPL. Each time you click _Enter_ your prompt will be sent and the response will be streamed in real time.
`CTRL+D` and `CTRL+C` work as expected in a REPL, exiting the program and cancelling the current loop, respectively. Entering `q`, `quit`, `e`, or `exit` while in prompt mode will also exit the program.

When typing a prompt, basic keyboard shortcuts are available like history navigation with the arrow-keys and deleting entire line with `CTRL + U`. More will be added in the future.

Your entire chat history will be sent to the language model each time you press _Enter_. To clear your chat history, enter `c` or `clear` into the prompt.
I recommend doing this whenever you want to ask the model a different line of questioning, so that you get the highest quality answers and you do not run up your usage bill.

The `--prompt` argument is parsed with a fuzzy finder. For instance, `llm haiku` will use the Haiku model.

###### Pricing

Once your current conversation costs more than a cent or two, it will be shown at the end of the response so that you know how much you're spending. Total session cost will also be shown when the program exits.

> Disclaimer:
> While I do use the official OpenAI [tokenizer](https://github.com/openai/tiktoken) and an official cookbook example from that repo to calculate prices,
> it is not something I have tested thoroughly, so there is no guarantee the prices are accurate. Anthropic provides authoritative token counts however, so those should be calculated better

For clarity, both OpenAI and Anthropic bill you on tokens per request AND response, and the entire chat history of previous prompts and responses are sent in EACH request. As long as you remember to clear your history after a few prompts you will be fine.

If you want to have multiple sessions, use [screen](https://www.gnu.org/software/screen/manual/screen.html) or [tmux](https://github.com/tmux/tmux/wiki). I want this project to "do one thing well" and leave other features to existing programs. This is the difference between this project and [elia](https://github.com/darrenburns/elia), for example.

## Development

This is a personal project above all else. I use this to play around with design patterns, new python features, data structures, best practices, etc.

Feature requests are more than welcome, however I will probably take a while to get to them.

##### Planned Features:

- Support for reasoning models
- Support for ollama
- Proper unit tests for pricing
- Add hierarchical configuration: TOML file, env vars, and CLI
- Optimize for CPU-time. Rich's Live display is pretty expensive
- Ensure the code-base is highly extensible
