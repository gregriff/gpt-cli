import sys
from typing import Generator

import openai

from config import CONFIG
from colors import *

openai.api_key = CONFIG['apiKey2']
model = 'gpt-3.5-turbo'

# todo log and output to a file the sum of tokens used


if __name__ == '__main__':
    while True:
        sys.stdout.write(BOLD + CYAN)
        prompt = input('> ')
        if prompt in ('exit', 'e', 'q', 'quit'):
            exit(0)
        sys.stdout.write(RESET)
        sys.stdout.write(GREEN)
        response: Generator = openai.ChatCompletion.create(model=model, stream=True,
                                                           messages=[{'role': 'user', 'content': prompt}],
                                                           temperature=0.7)
        for chunk in response:
            text_part: dict = chunk['choices'][0]['delta']
            content: str = text_part.get('content', '')
            print(content, end='')
        print('\n')
        sys.stdout.write(RESET)
