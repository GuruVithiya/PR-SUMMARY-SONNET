import time
import anthropic

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048
MAX_RETRIES = 3


def call_claude(system: str, messages: list) -> str:
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system,
                messages=messages,
            )
            return response.content[0].text
        except anthropic.RateLimitError:
            if attempt == MAX_RETRIES - 1:
                raise
            wait = 2 ** attempt
            print(f"Rate limited. Retrying in {wait}s...")
            time.sleep(wait)
