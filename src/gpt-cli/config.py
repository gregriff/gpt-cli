import sys
from json import load
from os import path

env_file = path.join(sys.path[0], "../../env.json")

with open(env_file) as file:
    CONFIG: dict = load(file)

default_system_message = "You are a concise assistant to a software engineer"
default_max_tokens = 1000

MODELS_AND_PRICES = {
    "openai": {  # https://openai.com/pricing#language-models
        "gpt-3.5-turbo": {
            "prompt": 0.5 / 1_000_000,
            "response": 1.50 / 1_000_000,
        },
        "gpt-4-turbo-preview": {
            "prompt": 10.0 / 1_000_000,
            "response": 30.0 / 1_000_000,
        },
    },
    "anthropic": {  # https://www.anthropic.com/api
        "claude-3-opus-20240229": {
            "prompt": 15.0 / 1_000_000,
            "response": 75.0 / 1_000_000,
        },
        "claude-3-sonnet-20240229": {
            "prompt": 3.0 / 1_000_000,
            "response": 15.0 / 1_000_000,
        },
        "claude-3-haiku-20240307": {
            "prompt": 0.25 / 1_000_000,
            "response": 1.25 / 1_000_000,
        },
    },
}
