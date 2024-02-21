import sys
from json import load
from os import path

env_file = path.join(sys.path[0], "../../env.json")

with open(env_file) as file:
    CONFIG: dict = load(file)

prompt_arguments = {
    "model": "gpt-4-turbo-preview",
    "stream": True,
    "temperature": 0.7,
    "max_tokens": 1000,
}
default_system_message = {
    "role": "system",
    "content": "You are a concise assistant to a software engineer",
}
