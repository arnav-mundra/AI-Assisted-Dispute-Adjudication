"""Environment smoke test.

Reports which LLM providers are configured. Makes no API call and never prints
a secret value.

    python -m src.config.validate_env
"""

from dotenv import load_dotenv

from src.config.paths import ENV_FILE, ROOT
from src.llm import available_models, provider_status

load_dotenv(ENV_FILE)


def main() -> None:
    print(f"Project root: {ROOT}")
    print(f".env present : {ENV_FILE.exists()}")
    print()
    print("Providers:")

    for row in provider_status():
        mark = "OK " if row["available"] else "-- "
        print(f"  {mark}{row['label']:<22} {row['env_var']:<20} {row['status']}")

    usable = available_models()
    print()
    print(f"Usable models ({len(usable)}): {', '.join(usable) or 'none'}")
    print()

    if usable:
        print("Environment smoke test: PASS")
    else:
        print(
            "Environment smoke test: NO PROVIDER CONFIGURED - "
            "set ANTHROPIC_API_KEY or GROQ_API_KEY in .env"
        )


if __name__ == "__main__":
    main()
