import openai

from config import CONFIG
from terminal import *
from classes import Prompt

# openai settings
openai.api_key = CONFIG['lapetusAPIkey']


if __name__ == '__main__':
    greeting()
    prompt = Prompt()

    while True:
        prompt.get_prompt()
        prompt.interpret_user_input()
