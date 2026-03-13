import os
import time

import httpx

BEDROCK_REGION = "us-east-1"
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20251001-v2:0"
MAX_TOKENS = 2048
MAX_RETRIES = 3

BEDROCK_URL = (
    f"https://bedrock-runtime.{BEDROCK_REGION}.amazonaws.com"
    f"/model/{MODEL_ID}/converse"
)


def call_claude(system: str, messages: list) -> str:
    api_key = os.environ["BEDROCK_API_KEY"]

    bedrock_messages = [
        {"role": m["role"], "content": [{"text": m["content"]}]}
        for m in messages
    ]

    payload = {
        "system": [{"text": system}],
        "messages": bedrock_messages,
        "inferenceConfig": {"maxTokens": MAX_TOKENS},
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    for attempt in range(MAX_RETRIES):
        response = httpx.post(BEDROCK_URL, json=payload, headers=headers, timeout=60)

        if response.status_code == 429:
            if attempt == MAX_RETRIES - 1:
                response.raise_for_status()
            wait = 2 ** attempt
            print(f"Rate limited. Retrying in {wait}s...")
            time.sleep(wait)
            continue

        response.raise_for_status()
        data = response.json()
        return data["output"]["message"]["content"][0]["text"]
