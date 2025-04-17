import sys
from json import load
from os import path

env_file = path.join(sys.path[0], "../env.json")

with open(env_file) as file:
    CONFIG: dict = load(file)

default_model = "claude-3-7-sonnet-latest"
default_system_message = "You are a concise assistant to a software engineer"
default_max_tokens = 1024

# TODO: this should be an object
MODELS_AND_PRICES: dict[str, dict[str, float | bool] | dict[str, float]] = {
    "openai": {  # https://openai.com/pricing#language-models
        "gpt-4o-mini": {
            "prompt": 0.15 / 1_000_000,
            "response": 0.075 / 1_000_000,
        },
        "gpt-4o": {
            "prompt": 2.5 / 1_000_000,
            "response": 10.0 / 1_000_000,
        },
        "gpt-4.1": {"prompt": 2.0 / 1_000_000, "response": 8.0 / 1_000_000},
        "gpt-4.1-mini": {"prompt": 0.4 / 1_000_000, "response": 1.6 / 1_000_000},
        "gpt-4.1-nano": {"prompt": 0.1 / 1_000_000, "response": 0.4 / 1_000_000},
        "o3": {
            "prompt": 10.0 / 1_000_000,
            "response": 40.0 / 1_000_000,
            "reasoning": True,
            "supports_temperature": False,
        },
        "o4-mini": {
            "prompt": 1.1 / 1_000_000,
            "response": 4.4 / 1_000_000,
            "reasoning": True,
            "supports_temperature": False,
        },
    },
    "anthropic": {  # https://www.anthropic.com/api
        "claude-3-5-haiku-latest": {
            "prompt": 0.8 / 1_000_000,
            "response": 4.00 / 1_000_000,
        },
        "claude-3-7-sonnet-latest": {
            "prompt": 3.0 / 1_000_000,
            "response": 15.0 / 1_000_000,
            "thinking": True,
        },
        "claude-3-opus-latest": {
            "prompt": 15.0 / 1_000_000,
            "response": 75.0 / 1_000_000,
        },
    },
}
