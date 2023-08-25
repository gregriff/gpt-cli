import sys
from os import path

import openai

from config import CONFIG, system_message, prompt_arguments
from terminal import greeting
from prompt import Prompt

# openai settings
openai.api_key = CONFIG['lapetusAPIkey']


if __name__ == '__main__':
    # TODO: use a cli lib to parse args for one time run of app (dont save settings) with custom:
    #   - system message
    #   - temp
    #   - model
    #
    # TODO Flags:
    #   "-o" to print full response to stdout and quit program'

    if len(sys.argv) == 2:
        system_message['content'] = sys.argv[1]
    greeting()
    # stata-dark. dracula. native. inkpot. vim.
    prompt = Prompt('green', 'native', system_message, prompt_arguments)
    prompt.run()


# long term todos:
# - menu commands in bottom toolbar. fullpage settings menu
# - asyncio used to implement multiple prompts at once. Bottom menu bar would allow user
#   to switch between tabs, giving them a notification when a response on a background tab has completed
#       - could also dive really deep into rich and try to render markdown in real time while waiting for network io
