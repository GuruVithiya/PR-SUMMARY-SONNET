import os
import sys
import time

import httpx

BEDROCK_REGION = "us-east-1"
MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
MAX_TOKENS = 2048
MAX_RETRIES = 3

BEDROCK_URL = (
    f"https://bedrock-runtime.{BEDROCK_REGION}.amazonaws.com"
    f"/model/{MODEL_ID}/invoke"
)


def call_claude(system: str, messages: list) -> str:
    api_key = os.environ["BEDROCK_API_KEY"]

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": MAX_TOKENS,
        "system": system,
        "messages": messages,
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
            print(f"Rate limited. Retrying in {wait}s...", file=sys.stderr)
            time.sleep(wait)
            continue

        if not response.is_success:
            print(f"Bedrock error {response.status_code}: {response.text}", file=sys.stderr)
            response.raise_for_status()

        data = response.json()
        return data["content"][0]["text"]
