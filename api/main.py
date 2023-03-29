import sys
from typing import Generator
from shutil import get_terminal_size

import openai

from config import CONFIG
from terminal import *

max_text_width = max_text_width(get_terminal_size().columns)

openai.api_key = CONFIG['lapetusAPIkey']
model = 'gpt-3.5-turbo'

# TODO:
#   - implement chat functionality:
# openai.ChatCompletion.create(
#   model="gpt-3.5-turbo",
#   messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Who won the world series in 2020?"},
#         {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
#         {"role": "user", "content": "Where was it played?"}
#     ]
# )

messages = [{'role': 'system',
            'content': 'You are a concise assistant that helps software engineers'}]


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
        messages.append({'role': 'user', 'content': prompt})
        response: Generator = openai.ChatCompletion.create(model=model, stream=True,
                                                           messages=messages,
                                                           temperature=0.7)
        full_response = []
        for chunk in response:
            for choice in chunk['choices']:
                text_part = choice['delta'].get('content', '')
                full_response.append(text_part)
                print(text_part, end='')
            # text_part: dict = chunk['choices'][0]['delta']
            # content: str = text_part.get('content', '')
            # print(content, end='')
        print('\n')
        messages.append({"role": "assistant", "content": ''.join(full_response)})
