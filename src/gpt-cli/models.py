# TODO

# class LLM:
#     def __init__(self, api_key: str):
#         self.api_key = api_key
#
#
# class OpenAIModel(LLM):
#     default_system_message = {
#         "role": "system",
#         "content": "You are a concise assistant to a software engineer",
#     }
#     prompt_arguments = {
#         "stream": True,
#         "temperature": 0.7,
#         "max_tokens": 1000,
#     }
#
#     def __init__(self, name, api_key: str):
#         super().__init__(api_key)
#         self.prompt_arguments["model"] = name
