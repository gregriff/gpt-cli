import sys
from typing import Generator
from shutil import get_terminal_size

import openai

from config import CONFIG
from terminal import *

max_text_width = max_text_width(get_terminal_size().columns)

openai.api_key = CONFIG['lapetusAPIkey']
model = 'gpt-4'

# TODO:
#   - get abs path of this file to find json when pwd is anywhere


system_message = {'role': 'system', 'content': 'You are a concise assistant to software engineers'}

if __name__ == '__main__':
    greeting(model)
    messages = [system_message, ]
    count = 0
    while True:
        try:
            prompt = input(f'{BOLD + YELLOW}? {CYAN}> ')
        except KeyboardInterrupt:
            exit(0)
        if prompt in ('exit', 'e', 'q', 'quit',):
            exit(0)
        if prompt in ('c', 'clear',):
            print(RESET, BOLD, BLUE)
            print(f'history cleared: {count} messages total', '\n', RESET)
            messages, count = [system_message, ], 0
            continue
        else:  # prompt model
            print(RESET, GREEN)
            messages.append({'role': 'user', 'content': prompt})
            response: Generator = openai.ChatCompletion.create(model=model, stream=True,
                                                               messages=messages,
                                                               temperature=0.7,
                                                               max_tokens=1000)
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
            count += 1
