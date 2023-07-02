from typing import Generator
from shutil import get_terminal_size

import openai

from terminal import *
from config import prompt_args


def prompt_llm(prompt: str, messages: list[dict], count: int):
    print(RESET, GREEN)
    messages.append({'role': 'user', 'content': prompt})
    try:
        response: Generator = openai.ChatCompletion.create(messages=messages, **prompt_args)
    except openai.error.APIConnectionError as e:
        print(YELLOW, f'Could not connect to API. Error: {str(e)}\n')
        return messages, count
    full_response = []
    max_text_w = max_text_width(get_terminal_size().columns)
    # tw = TextWrapper(width=max_text_width)
    for chunk in response:
        for choice in chunk['choices']:
            text_part = choice['delta'].get('content', '')
            full_response.append(text_part)
            # if len(text_part) > 4:
            #     if text_part[0].isdigit() and text_part[1] == '.' and text_part[-1] in (':', '.'):
            #         text_part = BLUE + text_part + GREEN
            print(text_part, end='')
    print('\n')
    messages.append({"role": "assistant", "content": ''.join(full_response)})
    count += 1
    return messages, count
