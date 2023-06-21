from json import load
from os import path

env_file = path.join(path.dirname(path.abspath(__file__)), 'env.json')

with open(env_file) as file:
    CONFIG = load(file)
