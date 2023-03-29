from typing import Generator
import asyncio

import openai

from config import CONFIG

openai.api_key = CONFIG['apiKey2']
model = 'gpt-3.5-turbo'

# todo log and output to a file the sum of tokens used


if __name__ == '__main__':
    while True:
        prompt = input('> ')
        if prompt in ('exit', 'e', 'q', 'quit'):
            exit(0)
        response: Generator = openai.ChatCompletion.create(model=model, stream=True,
                                                           messages=[{'role': 'user', 'content': prompt}],
                                                           temperature=0.7)
        for chunk in response:
            text_part: dict = chunk['choices'][0]['delta']
            content: str = text_part.get('content', '')
            print(content, end='')
        print('\n')
