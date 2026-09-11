"""Anthropic / Claude provider."""

from typing import List

from src.llm.provider import LLMProvider, Message, ProviderResponse, register


class AnthropicProvider(LLMProvider):
    name = "anthropic"
    label = "Anthropic (Claude)"
    env_var = "ANTHROPIC_API_KEY"
    models = ["claude-opus-5", "claude-sonnet-5", "claude-haiku-4-5"]

    def is_available(self) -> bool:
        # is_enabled() first: the DISABLED_PROVIDERS toggle outranks configuration.
        if not self.is_enabled() or not self.api_key():
            return False
        try:
            import anthropic  # noqa: F401
        except ImportError:
            return False
        return True

    def status(self) -> str:
        if not self.is_enabled():
            return "disabled"
        if not self.api_key():
            return "no API key"
        try:
            import anthropic  # noqa: F401
        except ImportError:
            return "SDK not installed"
        return "ready"

    def _complete(
        self,
        system: str,
        messages: List[Message],
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> ProviderResponse:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key())
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )

        text = "".join(
            block.text for block in response.content if getattr(block, "type", "") == "text"
        )

        return ProviderResponse(
            text=text,
            model=model,
            provider=self.name,
            input_tokens=getattr(response.usage, "input_tokens", 0) or 0,
            output_tokens=getattr(response.usage, "output_tokens", 0) or 0,
        )


register(AnthropicProvider())
