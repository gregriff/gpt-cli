from typing import Callable

import openai

from config import *
from helpers import get_prompt, prompt_llm
from functions import clear_history, change_system_msg, change_temp
from terminal import *

# openai settings
openai.api_key = CONFIG['lapetusAPIkey']

# runtime variables
messages, count = [system_message, ], 0

# lookup table to run functions on certain prompts
special_case_functions: dict[str, Callable] = {

    # exit and clear history behevior
    **{kw: lambda *_: exit(0) for kw in ('exit', 'e', 'q', 'quit',)},
    **{kw: lambda _, cnt: clear_history(cnt) for kw in ('c', 'clear',)},

    # change settings
    **{kw: lambda _, cnt: change_system_msg(cnt) for kw in ('sys', 'system', 'message')},
    **{kw: lambda msgs, cnt: change_temp(msgs, cnt) for kw in ('temp', 'temperature',)}
}


if __name__ == '__main__':
    greeting(prompt_args['model'])

    while True:
        prompt, stripped_prompt = get_prompt()

        # see if prompt triggers any predefined action
        user_action = special_case_functions.get(stripped_prompt)

        # either run the action or prompt the llm; update runtime variables
        messages, count = user_action(messages, count) \
            if user_action else prompt_llm(prompt, messages, count)