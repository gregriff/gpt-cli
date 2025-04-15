from abc import ABC, abstractmethod
from typing import Any, Generator, Optional

from anthropic import Anthropic
from anthropic.types import (
    ThinkingConfigDisabledParam,
    ThinkingConfigEnabledParam,
    Usage,
)
from openai import OpenAI, Stream
from typing_extensions import override

from config import CONFIG, MODELS_AND_PRICES


class LLM(ABC):
    """Encapsulates common functionality of OpenAI and Anthropic chat completion APIs"""

    def __init__(self, name: str, api_key: str, system_message: str, max_tokens: int):
        self.model_name = name
        self.api_key = api_key
        self.system_message = system_message
        self.max_tokens = max_tokens
        self.messages = []
        self.prompt_count = 0

    @abstractmethod
    def prompt_and_stream_completion(
        self,
        prompt: str,
        reasoning: Optional[bool | dict[str, str]],
        reasoning_effort=None,
    ) -> Generator[tuple[bool, str], None, None]:
        """prompt model with the current chat history and yield partial responses as they come in"""
        pass

    @abstractmethod
    def get_cost_of_current_chat(self) -> float:
        """
        calculate cost via recommended token counting method and price per token pulled from docs
        :returns: cost in dollars ex. 0.03 for 3 cents
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """clear the state of the current chat"""
        self.prompt_count = 0


class AnthropicModel(LLM):
    model_names = list(MODELS_AND_PRICES["anthropic"].keys())

    def __init__(self, name: str, system_message: str, max_tokens: int):
        if (api_key := CONFIG.get("anthropicAPIKey")) is None:
            print('Missing value for "anthropicAPIKey" in file env.json')
            exit(1)
        super().__init__(name, api_key, system_message, max_tokens)
        self.client = Anthropic(api_key=api_key)
        self.usage = Usage(input_tokens=0, output_tokens=0)
        self.prices_per_token = MODELS_AND_PRICES["anthropic"][name]
        self.is_reasoning_model = MODELS_AND_PRICES["anthropic"][name].get(
            "thinking", False
        )
        self.thinking_tokens = 1024
        self.thinking_settings = dict(type="disabled")

    @override
    def prompt_and_stream_completion(
        self, prompt: str, reasoning=False, reasoning_effort=None
    ):
        self.messages.append({"role": "user", "content": prompt})
        if reasoning and self.is_reasoning_model:
            self.thinking_settings = ThinkingConfigEnabledParam(
                type="enabled", budget_tokens=self.thinking_tokens
            )
            max_output_tokens = 2048 if self.max_tokens <= 1024 else self.max_tokens * 2
        else:
            self.thinking_settings = ThinkingConfigDisabledParam(type="disabled")
            max_output_tokens = self.max_tokens

        with self.client.messages.stream(
            max_tokens=max_output_tokens,
            messages=self.messages,
            model=self.model_name,
            system=self.system_message,
            thinking=self.thinking_settings,
        ) as stream:
            for event in stream:
                if event.type == "content_block_delta":
                    delta = event.delta
                    if (type := delta.type) == "thinking_delta":
                        yield True, delta.thinking
                    elif type == "text_delta":
                        yield False, delta.text
                    elif type == "citations_delta":
                        yield False, delta.citation.cited_text
                    else:
                        pass
            token_counts = stream.get_final_message().usage
            self.usage.input_tokens += token_counts.input_tokens
            self.usage.output_tokens += token_counts.output_tokens
            self.messages.append(
                {"role": "assistant", "content": stream.get_final_text()}
            )
            self.prompt_count += 1

    @override
    def get_cost_of_current_chat(self):
        return (
            self.usage.input_tokens / 1_000_000 * self.prices_per_token["prompt"]
            + self.usage.output_tokens / 1_000_000 * self.prices_per_token["response"]
        )

    @override
    def reset(self):
        super().reset()
        self.messages = []
        self.usage.input_tokens, self.usage.output_tokens = 0, 0


class OpenAIModel(LLM):
    model_names = list(MODELS_AND_PRICES["openai"].keys())

    def __init__(self, name: str, system_message: str, max_tokens: int):
        if (api_key := CONFIG.get("openaiAPIKey")) is None:
            print('Missing value for "openaiAPIKey" in file env.json')
            exit(1)
        super().__init__(name, api_key, system_message, max_tokens)
        self.client = OpenAI(api_key=api_key)
        self.max_tokens = max_tokens
        self.usage = dict(input_tokens=0, output_tokens=0)
        self.prices_per_token = MODELS_AND_PRICES["openai"][name]
        self.is_reasoning_model = MODELS_AND_PRICES["openai"][name].get(
            "reasoning", False
        )
        self.supports_temperature = MODELS_AND_PRICES["openai"][name].get(
            "supports_temperature", True
        )
        self.system_message = {"role": "developer", "content": system_message}
        self.messages = [self.system_message]

    @override
    def prompt_and_stream_completion(
        self, prompt, reasoning=None, reasoning_effort: Optional[str] = "medium"
    ):
        self.messages.append({"role": "user", "content": prompt})
        completion_arguments: dict[str, Any] = dict(
            messages=self.messages,
            model=self.model_name,
            stream=True,
            stream_options=dict(include_usage=True),
            max_completion_tokens=self.max_tokens,
            store=False,
        )
        if self.supports_temperature:
            completion_arguments.update(temperature=0.7)
        if self.is_reasoning_model:
            completion_arguments.update(dict(reasoning_effort=reasoning_effort))
        response_stream: Stream = self.client.chat.completions.create(
            **completion_arguments
        )

        full_response = ""
        for chunk in response_stream:
            if not chunk.choices:
                if not chunk.usage:
                    continue
                self.usage["input_tokens"] = chunk.usage.prompt_tokens
                self.usage["output_tokens"] = chunk.usage.completion_tokens
                continue
            if (text := chunk.choices[0].delta.content) is not None:
                full_response += text
                yield False, text
        self.messages.append({"role": "assistant", "content": full_response})
        self.prompt_count += 1

    @override
    def get_cost_of_current_chat(self):
        return (
            self.usage["input_tokens"] / 1_000_000 * self.prices_per_token["prompt"]
            + self.usage["output_tokens"]
            / 1_000_000
            * self.prices_per_token["response"]
        )

    @override
    def reset(self):
        super().reset()
        self.messages = [self.system_message]
        self.usage["input_tokens"], self.usage["ouput_tokens"] = 0, 0
