import sys
from json import load
from os import path, chdir

# script_dir = path.dirname(path.abspath(sys.argv[0]))
# chdir(script_dir)
# env_file = path.abspath('../../env.json')
env_file = path.join(sys.path[0], '../../env.json')

with open(env_file) as file:
    CONFIG: dict = load(file)

prompt_arguments = {
    'model': 'gpt-4',
    'stream': True,
    'temperature': 0.7,
    'max_tokens': 1000
}
system_message = {
    'role': 'system',
    'content': 'You are a concise assistant to software developers'
}
