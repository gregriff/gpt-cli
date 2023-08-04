import openai

from config import CONFIG, system_message, prompt_args
from terminal import *
from classes import Prompt

# openai settings
openai.api_key = CONFIG['lapetusAPIkey']


if __name__ == '__main__':
    greeting()
    prompt = Prompt(system_message, prompt_args)

    while True:
        prompt.get_prompt()
        prompt.interpret_user_input()

# TODO: 
# count num of characters per chunk loaded from API. if total char count > max_width, insert into current chunk a '\n' before the last full word
# in the chunk. This should wrap the entire output. Reset the total char count after this happens, then increment the newline counter. 
# Additionally, check each chunk for newline characters. Increment newline counter here too. This should leave you with an accurate linecount after 
# completion finishes. Delete that number of lines and render markdown in its place. 
# This may leave straggler chars printed on screen. Need to flush these. Maybe we can flush stdout on each line as we delete the lines??. 
# or maybe delete lines in a for loop and replace all lines with all space chars before we move up to the next line. 
