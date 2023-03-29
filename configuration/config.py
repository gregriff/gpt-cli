from json import load
from os import path, getcwd

with open(path.join(getcwd(), '../env.json')) as file:
    CONFIG = load(file)
