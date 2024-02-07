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


def gpt_pricing(model: str, prompt: bool) -> Optional[float]:
    if model.startswith("gpt-4-32k"):
        pricing = GPT_4_32K_PRICE_PER_TOKEN
    elif model.startswith("gpt-4-turbo"):
        pricing = GPT_4_TURBO_PRICE_PER_TOKEN
    elif model.startswith("gpt-4"):
        pricing = GPT_4_PRICE_PER_TOKEN
    else:
        return None
    return pricing["prompt" if prompt else "response"]
