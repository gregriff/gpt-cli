from abc import abstractmethod, ABC
from typing import Generator

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from openai import Stream, OpenAI
from openai.types.chat import ChatCompletionChunk
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
    name: str = None
    messages: list = []
    client = None
    api_key: str | None = None
    prices_per_token: dict[str, float] = None

    @abstractmethod
    def stream_completion(self) -> Generator[str, str, str]:
        pass

    @abstractmethod
    def get_cost_of_chat_history(self) -> float:
        pass

    @abstractmethod
    def reset(self):
        pass


class AnthropicModel(LLM):
    prompt_arguments = {
        "max_tokens": 1000,
    }

    def __init__(self, name: str, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.prompt_arguments["model"] = name
        self.name = name
        self.prices_per_token = MODELS_AND_PRICES["anthropic"][name]

    def stream_completion(self):
        with self.client.messages.stream(
            messages=self.messages, **self.prompt_arguments
        ) as stream:
            for text in stream.text_stream:
                yield text

    def role_to_name(self, role: str) -> str:
        if role == "system" or role == "user":
            return HUMAN_PROMPT
        elif role == "assistant":
            return AI_PROMPT
        else:
            raise ValueError(f"Unknown role: {role}")

    def make_prompt(self) -> str:
        prompt = "\n".join(
            [
                f"{self.role_to_name(message['role'])}{message['content']}"
                for message in self.messages
            ]
        )
        prompt += f"{self.role_to_name('assistant')}"
        return prompt

    def get_cost_of_chat_history(self):
        return (
            self.client.count_tokens(self.make_prompt())
            * self.prices_per_token["prompt"]
        )

    def reset(self):
        self.messages = []


class OpenAIModel(LLM):
    prompt_arguments = {
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 1000,
    }

    def __init__(self, name: str, api_key: str, system_message: str):
        self.client = OpenAI(api_key=api_key)
        self.prompt_arguments["model"] = name
        self.name = name
        self.prices_per_token = MODELS_AND_PRICES["openai"][name]
        self.system_message = {
            "role": "system",
            "content": system_message,
        }
        self.messages = [
            self.system_message,
        ]

    def stream_completion(self):
        response_stream: Stream[ChatCompletionChunk] = (
            self.client.chat.completions.create(
                messages=self.messages, **self.prompt_arguments
            )
        )
        for chunk in response_stream:
            for choice in chunk.choices:
                if (chunk_text := choice.delta.content) is not None:
                    yield chunk_text

    def get_cost_of_chat_history(self):
        """
        Get the total number of tokens used in the current chat history given OpenAI's token
        counting package `tiktoken`
        """
        encoding = encoding_for_model(self.name)
        num_tokens = 0
        for message in self.messages:
            # every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += 4
            for role, text in message.items():
                assert isinstance(text, str)
                num_tokens += len(encoding.encode(text))
                if role == "name":  # if there's a name, the role is omitted
                    num_tokens -= 1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens * self.prices_per_token["prompt"]

    def reset(self):
        self.messages = [self.system_message]
