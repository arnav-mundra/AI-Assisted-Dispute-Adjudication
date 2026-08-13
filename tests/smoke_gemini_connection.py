import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("Gemini API key loaded:", bool(api_key))

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing")

client = genai.Client(api_key=api_key)

print("Sending request...")

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Reply with exactly: Gemini connection successful."
)

print("Request completed.")
print("Response:", response.text)
