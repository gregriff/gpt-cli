import sys
from typing import Generator
from importlib.metadata import version

import openai

from config import CONFIG
from colors import *

openai.api_key = CONFIG['apiKey2']
model = 'gpt-3.5-turbo'


def greeting():
    print()
    sys.stdout.write(CYAN)
    print('=*='*10)
    sys.stdout.write(ORANGE)
    print(f'{"openai" : <10}{"v"+version("openai") : <15}')
    print(f'{"model" : <10}{model : <15}')
    sys.stdout.write(RESET)
    sys.stdout.write(CYAN)
    print('=*='*10)
    print('\n')

# todo log and output to a file the sum of tokens used


if __name__ == '__main__':
    greeting()
    while True:
        sys.stdout.write(BOLD + YELLOW)
        prompt = input(f'? {CYAN}> ')
        if prompt in ('exit', 'e', 'q', 'quit'):
            exit(0)
        sys.stdout.write(RESET)
        sys.stdout.write(GREEN)
        print()
        response: Generator = openai.ChatCompletion.create(model=model, stream=True,
                                                           messages=[{'role': 'user', 'content': prompt}],
                                                           temperature=0.7)
        for chunk in response:
            text_part: dict = chunk['choices'][0]['delta']
            content: str = text_part.get('content', '')
            print(content, end='')
        print('\n')
