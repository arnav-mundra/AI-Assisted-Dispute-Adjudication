"""Provider-agnostic LLM layer.

Add a vendor by subclassing `LLMProvider` and calling `register(...)`; nothing
in `src/reasoning_engine` or `app/` changes. Phase 4's multi-model comparison
plugs in at this seam.
"""

from src.llm.provider import (  # noqa: F401
    DISABLED_PROVIDERS,
    LLMProvider,
    Message,
    ProviderResponse,
    ProviderUnavailable,
    all_models,
    available_models,
    get_provider,
    provider_for_model,
    provider_status,
    providers,
    register,
)
