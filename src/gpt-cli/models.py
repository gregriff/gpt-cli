from abc import abstractmethod, ABC
from typing import Generator

from anthropic import Anthropic
from anthropic.types import Usage
from openai import OpenAI
from tiktoken import encoding_for_model

MODELS_AND_PRICES = {
    "openai": {
        "gpt-3.5-turbo": {
            "prompt": 0.003 / 1000,
            "response": 0.004 / 1000,
        },
        "gpt-4": {
            "prompt": 0.03 / 1000,
            "response": 0.06 / 1000,
        },
        "gpt-4-32k": {
            "prompt": 0.06 / 1000,
            "response": 0.12 / 1000,
        },
        "gpt-4-turbo-preview": {
            "prompt": 0.01 / 1000,
            "response": 0.03 / 1000,
        },
    },
    "anthropic": {
        "claude-3-opus-20240229": {
            "prompt": 15.0 / 1_000_000,
            "response": 75.0 / 1_000_000,
        },
        "claude-3-sonnet-20240229": {
            "prompt": 3.0 / 1_000_000,
            "response": 15.0 / 1_000_000,
        },
        "claude-3-haiku-20240307": {
            "prompt": 0.25 / 1_000_000,
            "response": 1.25 / 1_000_000,
        },
    },
}

anthropic_models = list(MODELS_AND_PRICES["anthropic"].keys())
openai_models = list(MODELS_AND_PRICES["openai"].keys())


class LLM(ABC):
    """Encapsulates common functionality of OpenAI and Anthropic chat completion APIs"""

    def __init__(self):
        self.name: str = ""
        self.messages: list = []
        self.client = None
        self.api_key: str | None = None
        self.prices_per_token: dict[str, float] = {}
        self.system_message: str | dict[str, str] = ""
        self.prompt_arguments: dict = {"max_tokens": 1000}

    @abstractmethod
    def stream_completion(self) -> Generator[str, None, None]:
        """yield partial responses of chat completions and keep track of tokens sent and received"""
        pass

    @abstractmethod
    def get_cost_of_current_chat(self) -> float:
        """calculate cost via recommended token counting method and prices pulled from docs"""
        pass

    @abstractmethod
    def reset(self) -> None:
        """clear the state of the current chat"""
        pass


class AnthropicModel(LLM):

    def __init__(self, name: str, api_key: str, system_message: str):
        super().__init__()
        self.client = Anthropic(api_key=api_key)
        self.prompt_arguments["model"] = name
        self.name = name
        self.system_message = system_message
        self.usage = Usage(input_tokens=0, output_tokens=0)
        self.prices_per_token = MODELS_AND_PRICES["anthropic"][name]

    def stream_completion(self):
        with self.client.messages.stream(
            messages=self.messages, system=self.system_message, **self.prompt_arguments
        ) as stream:
            for text in stream.text_stream:
                yield text
            token_counts = stream.get_final_message().usage
            self.usage.input_tokens += token_counts.input_tokens
            self.usage.output_tokens += token_counts.output_tokens

    def get_cost_of_current_chat(self):
        return (
            self.usage.input_tokens * self.prices_per_token["prompt"]
            + self.usage.output_tokens * self.prices_per_token["response"]
        )

    def reset(self):
        self.messages = []
        self.usage.input_tokens, self.usage.output_tokens = 0, 0


class OpenAIModel(LLM):
    openai_prompt_args = {
        "stream": True,
        "temperature": 0.7,
    }

    def __init__(self, name: str, api_key: str, system_message: str):
        super().__init__()
        self.client = OpenAI(api_key=api_key)
        self.prompt_arguments["model"] = name
        self.prompt_arguments.update(self.openai_prompt_args)
        self.name = name
        self.prices_per_token = MODELS_AND_PRICES["openai"][name]
        self.system_message = {"role": "system", "content": system_message}
        self.messages = [self.system_message]

    def stream_completion(self):
        response_stream = self.client.chat.completions.create(
            messages=self.messages, **self.prompt_arguments
        )

        for chunk in response_stream:
            if (text := chunk.choices[0].delta.content) is not None:
                yield text

    def get_cost_of_current_chat(self):
        """
        Custom token counting algorithm using official tokenizer based on code from:
        https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
        """
        encoding = encoding_for_model(self.name)
        num_prompt_tokens, num_response_tokens = 0, 0
        tokens_per_message, tokens_per_name = 3, 1
        for message in self.messages:
            num_prompt_tokens += tokens_per_message
            for key, data in message.items():
                num_prompt_tokens += (token_count := len(encoding.encode(data)))
                if key == "name":
                    num_prompt_tokens += tokens_per_name
                if key == "role":
                    if data == "assistant":
                        num_response_tokens += token_count

        # every reply is primed with <|start|>assistant<|message|>
        num_prompt_tokens += 3
        return (
            num_prompt_tokens * self.prices_per_token["prompt"]
            + num_response_tokens * self.prices_per_token["response"]
        )

    def reset(self):
        self.messages = [self.system_message]
