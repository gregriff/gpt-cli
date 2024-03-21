import sys
from json import load
from os import path

env_file = path.join(sys.path[0], "../../env.json")

with open(env_file) as file:
    CONFIG: dict = load(file)

prompt_arguments = {
    "stream": True,
    # "temperature": 0.7,
    "max_tokens": 1000,
}
default_system_message = {
    "role": "system",
    "content": "You are a concise assistant to a software engineer",
}

# TODO: once you have enough time make classes for these with pricing etc. as class attrs/method overrides
openai_models = [
    "gpt-4-turbo-preview",
]

anthropic_models = [
    "claude-3-opus-20240229",
]
