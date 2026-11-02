"""Sidebar panel: how much of the selected model's rate limits is used, and when they reset."""

from datetime import timedelta, timezone

import streamlit as st

from app.ui import theme
from src.llm import quota

IST = timezone(timedelta(hours=5, minutes=30))
TOKENS_PER_CASE = 4_500  # measured: ~4.5K tokens per adjudication with gpt-oss-120b


def _k(n: int) -> str:
    return f"{n / 1000:.0f}K" if n >= 10_000 else f"{n / 1000:.1f}K" if n >= 1000 else str(n)


@st.fragment(run_every=30)
def render(model: str, llm_ready: bool) -> None:
    snap = quota.snapshot(model)
    if snap is None:
        return

    theme.md(f'<div class="quota-head"><b>Model usage</b><span>{theme.esc(snap.plan)} · '
             f'{theme.esc(model.split("/")[-1])}</span></div>')

    if snap.blocked_until:
        at = snap.blocked_until.astimezone(IST).strftime("%H:%M")
        theme.md(f'<div class="quota-blocked">Groq is refusing calls for this model until about {at} IST. '
                 f'The rules engine still works offline.</div>')

    for meter in snap.meters:
        if meter.key == "tpd":
            sub = (f"{_k(meter.used)} of {_k(meter.limit)} · "
                   + ("exact, from Groq" if meter.exact else "estimated from this app's calls")
                   + f" · room for ~{meter.remaining // TOKENS_PER_CASE} cases")
        elif meter.key == "rpd":
            sub = f"{meter.used} of {meter.limit}" + ("" if meter.exact else " · estimated")
        else:
            sub = f"{_k(meter.used)} of {_k(meter.limit)}"
        verb = "Resets" if meter.key == "tpm" else "Frees"  # daily limits are rolling windows
        theme.quota_meter(meter.label, meter.fraction, quota.humanize_until(meter.resets_at, verb=verb), sub)

    if llm_ready:
        if st.button("Check now", key="quota_probe", help="Sends one ~20-token request to refresh the readings.",
                     width="stretch"):
            result = quota.probe(model)
            st.toast("Limits refreshed" if result == "ok" else f"Groq: {result}")
            st.rerun(scope="fragment")
