from abc import abstractmethod, ABC
from typing import Generator, Callable

from anthropic import Anthropic
from anthropic.types import Usage
from openai import OpenAI
from tiktoken import encoding_for_model

from config import MODELS_AND_PRICES, CONFIG


class LLM(ABC):
    """Encapsulates common functionality of OpenAI and Anthropic chat completion APIs"""

    def __init__(self, name: str, api_key: str, system_message: str, max_tokens: int):
        self.model_name = name
        self.api_key = api_key
        self.system_message = system_message
        self.prices_per_token: Callable[[str], dict[str, float]] = (
            lambda key: MODELS_AND_PRICES.get(key)[name]
        )
        self.prompt_arguments = {"max_tokens": max_tokens, "model": name}
        self.messages = []

    @abstractmethod
    def stream_completion(self) -> Generator[str, None, None]:
        """prompt model with the current chat history and yield partial responses as they come in"""
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
    model_names = list(MODELS_AND_PRICES["anthropic"].keys())

    def __init__(self, name: str, system_message: str, max_tokens: int):
        if (api_key := CONFIG.get("anthropicAPIKey")) is None:
            raise EnvironmentError(
                'Missing value for "anthropicAPIKey" in file env.json'
            )
        super().__init__(name, api_key, system_message, max_tokens)
        self.client = Anthropic(api_key=api_key)
        self.usage = Usage(input_tokens=0, output_tokens=0)
        self.prices_per_token = self.prices_per_token("anthropic")

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
    model_names = list(MODELS_AND_PRICES["openai"].keys())
    openai_prompt_args = {
        "stream": True,
        "temperature": 0.7,
    }

    def __init__(self, name: str, system_message: str, max_tokens: int):
        if (api_key := CONFIG.get("openaiAPIKey")) is None:
            raise EnvironmentError('Missing value for "openaiAPIKey" in file env.json')
        super().__init__(name, api_key, system_message, max_tokens)
        self.client = OpenAI(api_key=api_key)
        self.prompt_arguments.update(self.openai_prompt_args)
        self.prices_per_token = self.prices_per_token("openai")
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
        encoding = encoding_for_model(self.model_name)
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
