"""Check whether the Groq free-tier limits leave room for an experiment run.

    python scripts/groq_quota.py                      # default model
    python scripts/groq_quota.py openai/gpt-oss-20b

Sends one tiny request (~20 tokens). If a limit is hit, Groq's error states which
one (e.g. tokens per day), how much is used, and when to retry. The key is
never printed.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
from openai import OpenAI, RateLimitError  # noqa: E402

from src.llm.groq_provider import BASE_URL  # noqa: E402

load_dotenv(ROOT / ".env")

# One full experiment style is ~4.5K tokens per case: ~45K for the pilot, ~72K for the counterfactual set.
TOKENS_PER_CASE = 4_500


def main() -> int:
    model = sys.argv[1] if len(sys.argv) > 1 else os.getenv("ADJUDICATION_MODEL", "openai/gpt-oss-120b")
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("GROQ_API_KEY is not set in .env")
        return 2

    client = OpenAI(api_key=key, base_url=BASE_URL)
    try:
        raw = client.chat.completions.with_raw_response.create(
            model=model, max_tokens=1, messages=[{"role": "user", "content": "ok"}])
    except RateLimitError as exc:
        print(f"{model}: RATE LIMITED")
        print(str(exc)[:600])
        return 1

    headers = raw.headers
    print(f"{model}: OK - not rate limited right now")
    print(f"  requests left today:  {headers.get('x-ratelimit-remaining-requests')} "
          f"of {headers.get('x-ratelimit-limit-requests')}")
    print(f"  tokens left this minute: {headers.get('x-ratelimit-remaining-tokens')} "
          f"of {headers.get('x-ratelimit-limit-tokens')}")
    print("  The daily token budget (200K on the free tier) is not in the headers; if a run hits it,\n"
          "  this script will say so. Rough need: ~45K tokens per style on the pilot, ~72K on the\n"
          "  counterfactual set.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
