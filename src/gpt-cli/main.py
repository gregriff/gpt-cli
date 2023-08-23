import openai

from config import CONFIG, system_message, prompt_args
from terminal import *
from classes import Prompt

# openai settings
openai.api_key = CONFIG['lapetusAPIkey']


if __name__ == '__main__':
    greeting()
    prompt = Prompt('green', 'monokai', system_message, prompt_args)

    while True:
        prompt.get_prompt()
        prompt.interpret_user_input()
