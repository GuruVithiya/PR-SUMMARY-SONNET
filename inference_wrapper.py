import os
import sys
import time

import httpx

BEDROCK_REGION = "us-east-1"
MAX_TOKENS = 2048
MAX_RETRIES = 3

# Models in priority order — first available will be used
CANDIDATE_MODELS = [
    "us.anthropic.claude-sonnet-4-5-20251001-v1:0",
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
]


def _invoke(model_id: str, payload: dict, headers: dict) -> httpx.Response:
    url = (
        f"https://bedrock-runtime.{BEDROCK_REGION}.amazonaws.com"
        f"/model/{model_id}/invoke"
    )
    return httpx.post(url, json=payload, headers=headers, timeout=60)


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

    for model_id in CANDIDATE_MODELS:
        print(f"Trying model: {model_id}", file=sys.stderr)
        for attempt in range(MAX_RETRIES):
            response = _invoke(model_id, payload, headers)

            if response.status_code == 429:
                if attempt == MAX_RETRIES - 1:
                    break
                wait = 2 ** attempt
                print(f"Rate limited. Retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue

            if response.status_code in (404, 400):
                print(f"Model {model_id} unavailable: {response.text}", file=sys.stderr)
                break  # try next model

            if not response.is_success:
                print(f"Bedrock error {response.status_code}: {response.text}", file=sys.stderr)
                response.raise_for_status()

            data = response.json()
            return data["content"][0]["text"]

    raise RuntimeError("No available Bedrock model found. Check model access in AWS console.")
