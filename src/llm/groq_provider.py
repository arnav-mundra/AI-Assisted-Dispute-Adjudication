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
        return self._request(model, [{"role": "system", "content": system}, *messages],
                             max_tokens, temperature, json_mode=True)

    def probe(self, model: str) -> None:
        """Plain-text 1-token request: JSON mode can reject output truncated that short."""
        from src.llm import quota

        self.require_available()
        try:
            response = self._request(model, [{"role": "user", "content": "ok"}], 1, 0.0, json_mode=False)
        except Exception as exc:
            quota.record_error(self.name, model, str(exc))
            raise
        quota.record_call(self.name, model, response.input_tokens + response.output_tokens,
                          response.rate_limit_headers)

    def _request(self, model: str, messages: List[Message], max_tokens: int, temperature: float,
                 json_mode: bool) -> ProviderResponse:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key(), base_url=BASE_URL)
        extra = {"response_format": {"type": "json_object"}} if json_mode else {}
        raw = client.chat.completions.with_raw_response.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
            **extra,
        )
        response = raw.parse()

        return ProviderResponse(
            text=response.choices[0].message.content or "",
            model=model,
            provider=self.name,
            input_tokens=getattr(response.usage, "prompt_tokens", 0) or 0,
            output_tokens=getattr(response.usage, "completion_tokens", 0) or 0,
            rate_limit_headers={k: v for k, v in raw.headers.items() if k.lower().startswith("x-ratelimit")},
        )


register(GroqProvider())
