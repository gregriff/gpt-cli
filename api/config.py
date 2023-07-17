from json import load
from os import path

env_file = path.join(path.dirname(path.abspath(__file__)), 'env.json')

with open(env_file) as file:
    CONFIG = load(file)

prompt_args = {
    'model': 'gpt-4',
    'stream': True,
    'temperature': 0.7,
    'max_tokens': 1000
}
system_message = {
    'role': 'system',
    'content': 'You are a concise assistant to software developers'
}
