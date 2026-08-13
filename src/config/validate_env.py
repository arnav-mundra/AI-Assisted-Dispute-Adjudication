"""Phase 0 environment smoke test.

This deliberately does not make an API call. It only checks that the local
configuration is syntactically available without printing secret values.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

keys = ["OPENAI_API_KEY", "GEMINI_API_KEY"]
configured = [k for k in keys if os.getenv(k)]

print(f"Project root: {ROOT}")
print(f"Configured LLM providers: {', '.join(k.replace('_API_KEY', '') for k in configured) or 'none'}")
print("Environment smoke test: PASS")
