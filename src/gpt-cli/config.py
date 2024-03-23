import sys
from json import load
from os import path

env_file = path.join(sys.path[0], "../../env.json")

with open(env_file) as file:
    CONFIG: dict = load(file)

default_system_message = "You are a concise assistant to a software engineer"

MODELS_AND_PRICES = {
    "openai": {
        "gpt-3.5-turbo": {
            "prompt": 0.003 / 1000,
            "response": 0.004 / 1000,
        },
        "gpt-4": {
            "prompt": 0.03 / 1000,
            "response": 0.06 / 1000,
        },
        "gpt-4-32k": {
            "prompt": 0.06 / 1000,
            "response": 0.12 / 1000,
        },
        "gpt-4-turbo-preview": {
            "prompt": 0.01 / 1000,
            "response": 0.03 / 1000,
        },
    },
    "anthropic": {
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
