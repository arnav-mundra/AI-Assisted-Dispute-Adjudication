"""Provider-agnostic LLM interface.

The adjudication pipeline talks to `LLMProvider` only. Adding a provider means
adding one subclass and registering it — no changes to the pipeline or the UI.

A provider whose API key (or SDK) is absent reports itself unavailable rather
than raising, so the application can show its status instead of crashing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional

Message = Dict[str, str]  # {"role": "user" | "assistant", "content": "..."}

# ---------------------------------------------------------------------------
# THE PROVIDER TOGGLE
#
# Providers named here are registered and fully implemented but switched off:
# they never appear as selectable in the UI and refuse to run even if their
# API key is present. To re-enable Anthropic, delete "anthropic" from this set.
# That is the only change required.
# ---------------------------------------------------------------------------

DISABLED_PROVIDERS = {"anthropic"}


@dataclass
class ProviderResponse:
    text: str
    model: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def usage(self) -> Dict[str, int]:
        return {"input_tokens": self.input_tokens, "output_tokens": self.output_tokens}


class ProviderUnavailable(RuntimeError):
    """Raised when a provider is asked to run without a usable configuration."""


class LLMProvider(ABC):
    """One vendor. Subclasses implement `_complete` and declare their models."""

    name: str = ""
    label: str = ""
    env_var: str = ""
    models: List[str] = []

    def api_key(self) -> Optional[str]:
        import os

        return os.environ.get(self.env_var)

    def is_enabled(self) -> bool:
        """False while this provider is switched off in DISABLED_PROVIDERS."""
        return self.name not in DISABLED_PROVIDERS

    def is_available(self) -> bool:
        return self.is_enabled() and bool(self.api_key())

    def status(self) -> str:
        if not self.is_enabled():
            return "disabled"
        return "ready" if self.api_key() else "no API key"

    def require_available(self) -> None:
        if not self.is_enabled():
            raise ProviderUnavailable(
                f"{self.label} is disabled for this deployment "
                f"(remove '{self.name}' from DISABLED_PROVIDERS in src/llm/provider.py "
                f"to re-enable it)."
            )
        if not self.api_key():
            raise ProviderUnavailable(
                f"{self.label} is not configured: set {self.env_var} in .env and restart."
            )

    def complete(
        self,
        system: str,
        messages: List[Message],
        model: str,
        max_tokens: int = 3000,
        temperature: float = 0.0,
    ) -> ProviderResponse:
        self.require_available()
        return self._complete(system, messages, model, max_tokens, temperature)

    @abstractmethod
    def _complete(
        self,
        system: str,
        messages: List[Message],
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> ProviderResponse:
        ...


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_REGISTRY: "Dict[str, LLMProvider]" = {}
_ORDER: List[str] = []


def register(provider: LLMProvider) -> LLMProvider:
    _REGISTRY[provider.name] = provider
    if provider.name not in _ORDER:
        _ORDER.append(provider.name)
    return provider


def _load_registry() -> Dict[str, LLMProvider]:
    if not _REGISTRY:
        # Imported for their registration side effect. Order is preference order.
        from src.llm import anthropic_provider, groq_provider  # noqa: F401
    return _REGISTRY


def providers() -> List[LLMProvider]:
    _load_registry()
    return [_REGISTRY[name] for name in _ORDER]


def get_provider(name: str) -> LLMProvider:
    _load_registry()
    if name not in _REGISTRY:
        raise KeyError(f"Unknown provider '{name}'. Known: {sorted(_REGISTRY)}")
    return _REGISTRY[name]


def provider_for_model(model: str) -> LLMProvider:
    for provider in providers():
        if model in provider.models:
            return provider
    raise KeyError(f"No registered provider serves model '{model}'.")


def all_models() -> List[str]:
    """Every model of every enabled provider — configured or not.

    Disabled providers are excluded entirely: their models must not be
    selectable in the UI even when their API key is present.
    """
    return [
        model
        for provider in providers()
        if provider.is_enabled()
        for model in provider.models
    ]


def available_models() -> List[str]:
    return [
        model
        for provider in providers()
        if provider.is_available()
        for model in provider.models
    ]


def provider_status() -> List[Dict[str, object]]:
    """Rows for the UI status panel."""
    return [
        {
            "name": provider.name,
            "label": provider.label,
            "env_var": provider.env_var,
            "available": provider.is_available(),
            "enabled": provider.is_enabled(),
            "status": provider.status(),
            "models": list(provider.models),
        }
        for provider in providers()
    ]
