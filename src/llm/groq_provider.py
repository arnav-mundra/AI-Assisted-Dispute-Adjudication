"""Groq provider.

Groq serves the OpenAI chat-completions dialect at its own base URL, so it uses
the OpenAI SDK as a transport. That is an implementation detail of this module —
the pipeline sees only `LLMProvider`.
"""

from typing import List

from src.llm.provider import LLMProvider, Message, ProviderResponse, register

BASE_URL = "https://api.groq.com/openai/v1"


class GroqProvider(LLMProvider):
    name = "groq"
    label = "Groq"
    env_var = "GROQ_API_KEY"
    models = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]

    def _complete(
        self,
        system: str,
        messages: List[Message],
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> ProviderResponse:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key(), base_url=BASE_URL)
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system}, *messages],
        )

        return ProviderResponse(
            text=response.choices[0].message.content or "",
            model=model,
            provider=self.name,
            input_tokens=getattr(response.usage, "prompt_tokens", 0) or 0,
            output_tokens=getattr(response.usage, "completion_tokens", 0) or 0,
        )


register(GroqProvider())
