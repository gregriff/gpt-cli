from typing import Optional

GPT_3_5_TURBO_16K_PRICE_PER_TOKEN = {
    "prompt": 0.003 / 1000,
    "response": 0.004 / 1000,
}

GPT_4_PRICE_PER_TOKEN = {
    "prompt": 0.03 / 1000,
    "response": 0.06 / 1000,
}

GPT_4_32K_PRICE_PER_TOKEN = {
    "prompt": 0.06 / 1000,
    "response": 0.12 / 1000,
}

GPT_4_TURBO_PRICE_PER_TOKEN = {
    "prompt": 0.01 / 1000,
    "response": 0.03 / 1000,
}

CLAUDE_3_OPUS_PRICING = {
    "prompt": 15.0 / 1_000_000,
    "response": 75.0 / 1_000_000,
}

CLAUDE_3_SONNET_PRICING = {
    "prompt": 3.0 / 1_000_000,
    "response": 15.0 / 1_000_000,
}

CLAUDE_3_HAIKU_PRICING = {
    "prompt": 0.25 / 1_000_000,
    "response": 1.25 / 1_000_000,
}


def gpt_pricing(model: str, prompt: bool) -> Optional[float]:
    if model.startswith("gpt-4-32k"):
        pricing = GPT_4_32K_PRICE_PER_TOKEN
    elif model.startswith("gpt-4-turbo") or model.startswith("gpt-4-"):
        pricing = GPT_4_TURBO_PRICE_PER_TOKEN
    elif model.startswith("gpt-4"):
        pricing = GPT_4_PRICE_PER_TOKEN
    else:
        return 0
    return pricing["prompt" if prompt else "response"]
