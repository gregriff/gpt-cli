import sys
from os import path

import openai

from config import CONFIG, system_message, prompt_arguments
from terminal import greeting
from prompt import Prompt

# TODO: update screen rendering so that updates to not mess with auto-scrolling relating to terminal height:
#   - look at reference projects for solutions
#   - look into storing info about recently rendered text. If it does not involve markdown, strictly append to screen. 
#     if it does involve markdown, rewrite only that section? Someone must have already implemented this.
# 
# update openai package:
#   - async is now supported. Judge if this would be worth it. Prompt toolkit and maybe rich support this
# integrate typer as the frontend:
#   - replace all prompt-toolkit and hardcoded keyboard actions into typer, or maybe just wrap startup functionality with
#     typer and keep in-app keyboard interactions the same

if __name__ == '__main__':
    # TODO: use a cli lib to parse args for one time run of app (dont save settings) with custom:
    #   - system message
    #   - temp
    #   - model
    #   - theme
    #   - output main color
    #
    # ensure cli lib generates man pages
    #
    # TODO Flags:
    #   "-o" to print full response to stdout and quit program'
    api_key = CONFIG.get('lapetusAPIkey')

    if len(sys.argv) == 2:
        system_message['content'] = sys.argv[1]
    greeting()
    # stata-dark. dracula. native. inkpot. vim.
    prompt = Prompt('green', 'native', system_message, api_key, prompt_arguments)
    prompt.run()


# long term todos:
# - menu commands in bottom toolbar. fullpage settings menu
# - asyncio used to implement multiple prompts at once. Bottom menu bar would allow user
#   to switch between tabs, giving them a notification when a response on a background tab has completed
#       - could also dive really deep into rich and try to render markdown in real time while waiting for network io
