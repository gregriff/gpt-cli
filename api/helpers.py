from typing import Generator
from shutil import get_terminal_size

import openai

from terminal import *
from config import prompt_args


def get_prompt() -> tuple[str, str]:
    try:
        prompt = input(f'{BOLD + YELLOW}? {CYAN}> ')
        stripped = prompt.casefold().strip()
        return prompt, stripped
    except KeyboardInterrupt:
        exit(0)


def prompt_llm(prompt: str, messages: list[dict], count: int):
    print(RESET, GREEN)
    messages.append({'role': 'user', 'content': prompt})
    response: Generator = openai.ChatCompletion.create(messages=messages, **prompt_args)
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
