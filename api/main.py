import sys
from typing import Generator
from shutil import get_terminal_size

import openai

from config import CONFIG
from terminal import *

max_text_width = max_text_width(get_terminal_size().columns)

openai.api_key = CONFIG['lapetusAPIkey']
model = 'gpt-3.5-turbo'

# todo log and output to a file the sum of tokens used


if __name__ == '__main__':
    greeting(model)
    while True:
        try:
            prompt = input(f'{BOLD + YELLOW}? {CYAN}> ')
        except KeyboardInterrupt:
            exit(0)
        if prompt in ('exit', 'e', 'q', 'quit'):
            exit(0)
        print(RESET, GREEN)
        response: Generator = openai.ChatCompletion.create(model=model, stream=True,
                                                           messages=[{'role': 'user', 'content': prompt}],
                                                           temperature=0.7)
        for chunk in response:
            text_part: dict = chunk['choices'][0]['delta']
            content: str = text_part.get('content', '')
            # if len(content) > max_text_width:
            #     print(f'{content : <20}')
            # else:
            print(content, end='')
        print('\n')
