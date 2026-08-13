import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

print("API key loaded:", bool(api_key))

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing")

client = OpenAI(api_key=api_key)

print("Sending request...")

response = client.responses.create(
    model="gpt-4o-mini",
    input="Reply with exactly: OpenAI connection successful."
)

print("Request completed.")
print("Response type:", type(response))
print("Response ID:", response.id)
print("Output text:", repr(response.output_text))
print("Full output:", response.output)