import openai

from config import CONFIG, system_message, prompt_args
from terminal import greeting
from classes import Prompt

# openai settings
openai.api_key = CONFIG['lapetusAPIkey']


if __name__ == '__main__':
    greeting()  # TODO: ASCII art greeting. menu commands in bottom toolbar. fullpage settings menu
    prompt = Prompt('green', 'monokai', system_message, prompt_args)

    while True:
        prompt.get_prompt()
        prompt.interpret_user_input()


# long term todos:
# - asyncio used to implement multiple prompts at once. Bottom menu bar would allow user
#   to switch between tabs, giving them a notification when a response on a background tab has completed
#       - could also dive really deep into rich and try to render markdown in real time while waiting for network io
