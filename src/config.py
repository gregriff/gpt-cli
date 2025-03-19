import sys
from json import load
from os import path

env_file = path.join(sys.path[0], "../env.json")

with open(env_file) as file:
    CONFIG: dict = load(file)

default_model = "claude-3-7-sonnet-latest"
default_system_message = "You are a concise assistant to a software engineer"
default_max_tokens = 1024

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
        "gpt-4.5-preview": {"prompt": 75.0 / 1_000_000, "response": 150.0 / 1_000_000},
        "o1": {
            "prompt": 15.0 / 1_000_000,
            "response": 60.0 / 1_000_000,
            "reasoning": True,
            "supports_temperature": False,
        },
        "o3-mini": {
            "prompt": 1.1 / 1_000_000,
            "response": 4.4 / 1_000_000,
            "reasoning": True,
            "supports_temperature": False,
        },
    },
    "anthropic": {  # https://www.anthropic.com/api
        "claude-3-5-haiku-20241022": {
            "prompt": 0.25 / 1_000_000,
            "response": 1.25 / 1_000_000,
        },
        "claude-3-7-sonnet-latest": {
            "prompt": 3.0 / 1_000_000,
            "response": 15.0 / 1_000_000,
            "thinking": True,
        },
        "claude-3-opus-20240229": {
            "prompt": 15.0 / 1_000_000,
            "response": 75.0 / 1_000_000,
        },
    },
}
