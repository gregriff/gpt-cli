from math import ceil
from typing import Generator
from shutil import get_terminal_size

import openai
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

from terminal import *
from config import prompt_args


def prompt_llm(prompt: str, messages: list[dict], count: int):
    print(RESET)
    console = Console(width=get_terminal_size().columns)
    inital_position = console
    messages.append({'role': 'user', 'content': prompt})
    try:
        response: Generator = openai.ChatCompletion.create(messages=messages, **prompt_args)
    except openai.error.APIConnectionError as e:
        print(YELLOW, f'Could not connect to API. Error: {str(e)}\n')
        return messages, count
    full_response = []

    for chunk in response:
        for choice in chunk['choices']:
            text_part = choice['delta'].get('content', '')
            full_response.append(text_part)

            # TODO:
            #   - calculate total lines by math.ceil(len(full_response_joined) / width) + newline_count
            #   - overwrite all text on far edge with 'crop' style?
            console.print(Text(text_part, style='green', overflow='fold', ), end='')
    final_response = "".join(full_response)
    # newline_count = final_response.count("\n")
    # total_lines = ceil(len(final_response) / console.width) + (newline_count - 1)
    # if newline_count == 0 and total_lines == 0:
    #     print(end='\r')
    # else:
    #     print(f"\033[{total_lines}A", end="\r")
    # console.print(Markdown(final_response, style='blue', code_theme='ansibrightblue'))
    #
    # for i in range(total_lines // 2):
    #     print('\033[K')
    # print(f"\033[{total_lines // 2}A", end='\r\n\n')
    # print(f'{newline_count=} {console.width} {total_lines=} {ceil(len(final_response) / console.width)=}')
    print('\n')
    messages.append({"role": "assistant", "content": final_response})
    count += 1
    return messages, count
