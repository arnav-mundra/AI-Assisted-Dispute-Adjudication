import pytest


@pytest.fixture(autouse=True)
def _isolated_usage_log(tmp_path, monkeypatch):
    """Mock provider calls must not land in the real runs/llm_usage.jsonl."""
    monkeypatch.setenv("LLM_USAGE_LOG", str(tmp_path / "llm_usage.jsonl"))
