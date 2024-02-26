# gpt-cli

**insert screenshot**

## Overview

I created this app out of curiosity of CLI development and because of the lack of free and convenient interfaces to GPT-4. Now apart of my daily workflow as a rubber duck debugger, this CLI works great in a terminal tab within one's IDE.
Main features include markdown rendering, live updates as chunked responses come in, and control of GPT settings via command arguments. 

## Installation and Recommended Setup

Developed on MacOS with Python 3.11. All instructions will assume a *nix machine

**GPT functionality requires an OpenAI API token. You must place it in a file called `env.json` in the project root directory. Ex.**

```json
{
  "apiKey": "12345678"
}
```

I prefer to install this app's dependencies to the system interpreter so that I can use a shell alias to run it at any time with no prior venv setup. In the terminal:

1. Ensure you are not using a venv: run `deactivate`
2. After cloning and inside the project dir, run `make install` to download all python packages. 
3. Add shell alias and reload shell config to apply changes (assuming `bash` or `zsh`):
    ```shell
   config_file="${HOME}/.$(basename ${SHELL})rc" && \
    echo "alias llm='python ENTER_ABSOLUTE_PATH_TO_src/gpt-cli/main.py_HERE'" >> "${config_file}" && \ 
   source "${config_file}" 
   ```
Now no matter where your current working directory is, you can type `llm` in your terminal to start a GPT session!

## Configuration

## Other
