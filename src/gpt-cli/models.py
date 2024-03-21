from abc import abstractmethod, ABC
from typing import Generator

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT, MessageStreamManager
from openai import Stream, OpenAI
from openai.types.chat import ChatCompletionChunk
from tiktoken import encoding_for_model


class LLM(ABC):
    messages: list = []
    client = None
    api_key: str | None = None

    @abstractmethod
    def stream_completion(self) -> Generator[str]:
        pass

    @abstractmethod
    def get_num_tokens(self):
        pass


class AnthropicModel(LLM):
    prompt_arguments = {
        "max_tokens": 1000,
    }

    def __init__(self, name, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.prompt_arguments["model"] = name

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

    def get_num_tokens(self) -> int:
        return self.client.count_tokens(self.make_prompt())


class OpenAIModel(LLM):
    default_system_message = {
        "role": "system",
        "content": "You are a concise assistant to a software engineer",
    }
    prompt_arguments = {
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 1000,
    }

    def __init__(self, name, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.prompt_arguments["model"] = name

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

    def get_num_tokens(self):
        """
        Get the total number of tokens used in the current chat history given OpenAI's token
        counting package `tiktoken`
        """
        encoding = encoding_for_model(self.prompt_arguments["model"])
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
        return num_tokens
