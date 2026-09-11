"""The DISABLED_PROVIDERS toggle must hold regardless of what is in the environment."""

import pytest

from src.llm import (
    DISABLED_PROVIDERS,
    ProviderUnavailable,
    all_models,
    available_models,
    get_provider,
    provider_status,
)


def test_anthropic_is_currently_switched_off():
    assert "anthropic" in DISABLED_PROVIDERS


def test_disabled_provider_models_are_not_selectable_even_with_a_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-not-a-real-key")

    anthropic = get_provider("anthropic")
    assert not anthropic.is_enabled()
    assert not anthropic.is_available()
    assert anthropic.status() == "disabled"

    for model in anthropic.models:
        assert model not in all_models()
        assert model not in available_models()


def test_disabled_provider_refuses_to_run(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-not-a-real-key")

    with pytest.raises(ProviderUnavailable) as excinfo:
        get_provider("anthropic").complete(
            system="x",
            messages=[{"role": "user", "content": "x"}],
            model="claude-opus-5",
        )

    assert "disabled" in str(excinfo.value).lower()


def test_groq_is_registered_and_enabled():
    groq = get_provider("groq")
    assert groq.is_enabled()
    assert groq.models


def test_only_groq_and_anthropic_are_registered():
    names = {row["name"] for row in provider_status()}
    assert names == {"anthropic", "groq"}
