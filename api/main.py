import openai

from config import CONFIG

openai.api_key = CONFIG['apiKey2']
model = 'gpt-3.5-turbo'


def parse_completion(compl: dict) -> str:
    return compl['choices'][0]['message']['content']


if __name__ == '__main__':
    while True:
        prompt = input('> ')
        if prompt in ('exit', 'e', 'q', 'quit'):
            exit(0)
        completion = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': prompt}])
        response = parse_completion(completion)
        print(response)
