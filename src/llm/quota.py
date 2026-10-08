"""Provider rate limits: what is left, and when it resets.

Three sources, best first:

1. A rate-limit (429) error. Groq's message states the exact limit, usage and
   retry time ("... tokens per day (TPD): Limit 200000, Used 199734, Requested
   4512. Please try again in 1m38.5s ...").
2. Response headers (x-ratelimit-*): exact requests-per-day and tokens-per-minute
   as of the last call.
3. A local log of this app's own calls (runs/llm_usage.jsonl), summed over a
   rolling 24h. Groq does not report daily tokens in headers, so this is the only
   way to show them between 429s. It is an estimate: it cannot see the same key
   being used elsewhere.

`LLMProvider.complete` records every call here; the UI only reads `snapshot`.
"""

from __future__ import annotations

import json
import os
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config.paths import EXPERIMENT_RUNS_DIR, RUNS_DIR

# LLM_USAGE_LOG overrides the location (the test suite points it at a temp file).
USAGE_LOG = Path(os.environ.get("LLM_USAGE_LOG", RUNS_DIR / "llm_usage.jsonl"))
DAY = timedelta(hours=24)
MINUTE = timedelta(minutes=1)

# Groq free tier, per model (console.groq.com/docs/rate-limits, checked 2026-10-09).
# Headers override these whenever a call reports its own limits.
FREE_TIER: Dict[str, Dict[str, int]] = {
    "openai/gpt-oss-120b": {"rpd": 1_000, "tpm": 8_000, "tpd": 200_000},
    "openai/gpt-oss-20b": {"rpd": 1_000, "tpm": 8_000, "tpd": 200_000},
    "qwen/qwen3.8-27b": {"rpd": 1_000, "tpm": 8_000, "tpd": 200_000},
}
PLAN_LABEL = {"groq": "Groq free tier"}

_LOCK = threading.Lock()

_LIMIT_RE = re.compile(
    r"\((?P<kind>TPD|TPM|RPD|RPM)\):\s*Limit\s+(?P<limit>\d+),\s*Used\s+(?P<used>\d+)"
    r"(?:,\s*Requested\s+(?P<requested>\d+))?.*?try again in\s+(?P<wait>[\d.hms]+)",
    re.IGNORECASE | re.DOTALL,
)
_DURATION_RE = re.compile(r"(\d+(?:\.\d+)?)(ms|h|m|s)")


def now() -> datetime:
    return datetime.now(timezone.utc)


def parse_duration(text: Optional[str]) -> Optional[timedelta]:
    """Groq reset strings: '7.66s', '2m59.56s', '1h2m3s', '120ms'."""
    if not text:
        return None
    parts = _DURATION_RE.findall(str(text).strip())
    if not parts:
        return None
    seconds = 0.0
    for value, unit in parts:
        seconds += float(value) * {"h": 3600, "m": 60, "s": 1, "ms": 0.001}[unit]
    return timedelta(seconds=seconds)


def parse_rate_limit_error(message: str) -> Optional[Dict[str, Any]]:
    match = _LIMIT_RE.search(message or "")
    if not match:
        return None
    wait = parse_duration(match.group("wait"))
    return {
        "kind": match.group("kind").lower(),
        "limit": int(match.group("limit")),
        "used": int(match.group("used")),
        "requested": int(match.group("requested") or 0),
        "retry_seconds": wait.total_seconds() if wait else None,
    }


# ---------------------------------------------------------------------------
# Recording
# ---------------------------------------------------------------------------

def _log_path(log: Optional[Path]) -> Path:
    return log or Path(os.environ.get("LLM_USAGE_LOG", USAGE_LOG))


def _append(entry: Dict[str, Any], log: Optional[Path] = None) -> None:
    log = _log_path(log)
    try:
        with _LOCK:
            log.parent.mkdir(parents=True, exist_ok=True)
            with log.open("a", encoding="utf-8") as file:
                file.write(json.dumps(entry) + "\n")
    except OSError:
        pass  # usage display must never break an adjudication


def record_call(provider: str, model: str, tokens: int,
                headers: Optional[Dict[str, str]] = None, log: Optional[Path] = None) -> None:
    entry: Dict[str, Any] = {"at": now().isoformat(), "kind": "call", "provider": provider,
                             "model": model, "tokens": int(tokens)}
    if headers:
        entry["headers"] = {k.lower(): v for k, v in headers.items() if k.lower().startswith("x-ratelimit")}
    _append(entry, log)


def record_error(provider: str, model: str, message: str, log: Optional[Path] = None) -> None:
    parsed = parse_rate_limit_error(message)
    if parsed:
        _append({"at": now().isoformat(), "kind": "rate_limited", "provider": provider, "model": model,
                 "limit_kind": parsed["kind"], **{k: v for k, v in parsed.items() if k != "kind"}}, log)


def _read(log: Optional[Path]) -> List[Dict[str, Any]]:
    log = _log_path(log)
    if not log.exists():
        return []
    entries = []
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
            entry["_at"] = datetime.fromisoformat(entry["at"])
            entries.append(entry)
        except (ValueError, KeyError):
            continue
    return entries


def _backfill(model: str, before: Optional[datetime], runs_dir: Path) -> List[Dict[str, Any]]:
    """Token totals from saved experiment runs that predate the usage log."""
    rows = []
    if not runs_dir.exists():
        return rows
    for path in runs_dir.glob("*_llm_*.json"):
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
            at = datetime.fromisoformat(run["created_at"])
        except (OSError, ValueError, KeyError):
            continue
        if run.get("config", {}).get("model") != model or (before and at >= before):
            continue
        for prediction in run.get("predictions", []):  # one request per case (repairs not recorded)
            tokens = sum((prediction.get("usage") or {}).values())
            rows.append({"_at": at, "kind": "call", "model": model, "tokens": tokens, "backfilled": True})
    return rows


# ---------------------------------------------------------------------------
# Snapshot for the UI
# ---------------------------------------------------------------------------

@dataclass
class Meter:
    key: str
    label: str
    used: int
    limit: int
    resets_at: Optional[datetime]
    exact: bool
    note: str = ""

    @property
    def fraction(self) -> float:
        return min(1.0, self.used / self.limit) if self.limit else 0.0

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.used)


@dataclass
class QuotaSnapshot:
    model: str
    plan: str
    meters: List[Meter] = field(default_factory=list)
    last_call: Optional[datetime] = None
    blocked_until: Optional[datetime] = None

    def meter(self, key: str) -> Optional[Meter]:
        return next((m for m in self.meters if m.key == key), None)


def snapshot(model: str, provider: str = "groq", at: Optional[datetime] = None,
             log: Optional[Path] = None, runs_dir: Path = EXPERIMENT_RUNS_DIR) -> Optional[QuotaSnapshot]:
    """Current usage of `model`, or None if it has no known limits."""
    limits = FREE_TIER.get(model)
    if not limits:
        return None
    at = at or now()
    logged = [e for e in _read(log) if e.get("model") == model]
    first_logged = min((e["_at"] for e in logged), default=None)
    entries = sorted(logged + _backfill(model, first_logged, runs_dir), key=lambda e: e["_at"])
    calls = [e for e in entries if e["kind"] == "call"]
    errors = [e for e in entries if e["kind"] == "rate_limited"]
    last_headers = next((e for e in reversed(calls) if e.get("headers")), None)

    snap = QuotaSnapshot(model=model, plan=PLAN_LABEL.get(provider, provider),
                         last_call=calls[-1]["_at"] if calls else None)
    blocks = [e["_at"] + timedelta(seconds=e["retry_seconds"]) for e in errors
              if e.get("retry_seconds") is not None and e["_at"] + timedelta(seconds=e["retry_seconds"]) > at]
    snap.blocked_until = max(blocks, default=None)

    # --- tokens per day: rolling 24h window ---------------------------------
    window = [e for e in calls if e["_at"] > at - DAY]
    used_day = sum(int(e.get("tokens", 0)) for e in window)
    resets_day = window[0]["_at"] + DAY if window else None
    exact_day = False
    tpd_error = next((e for e in reversed(errors) if e.get("limit_kind") == "tpd"), None)
    if tpd_error and tpd_error["_at"] + timedelta(seconds=tpd_error.get("retry_seconds") or 0) > at:
        # Groq told us exactly; add anything logged after the error.
        later = sum(int(e.get("tokens", 0)) for e in window if e["_at"] > tpd_error["_at"])
        used_day = tpd_error["used"] + later
        resets_day = tpd_error["_at"] + timedelta(seconds=tpd_error["retry_seconds"] or 0)
        limits = {**limits, "tpd": tpd_error["limit"]}
        exact_day = True
    snap.meters.append(Meter("tpd", "Tokens · rolling 24h", used_day, limits["tpd"], resets_day, exact_day,
                             "" if exact_day else "estimated from this app's calls"))

    # --- requests per day + tokens per minute: from the latest headers -------
    rpd_limit, tpm_limit = limits["rpd"], limits["tpm"]
    # Requests free up one at a time on a rolling day, so the reset shown is when the
    # oldest logged request leaves the window; headers only make the count exact.
    used_rpd, resets_rpd, exact_rpd = len(window), (window[0]["_at"] + DAY if window else None), False
    used_tpm, resets_tpm, exact_tpm = 0, None, False
    if last_headers:
        h, seen = last_headers["headers"], last_headers["_at"]
        try:
            rpd_limit = int(h.get("x-ratelimit-limit-requests", rpd_limit))
            reset = parse_duration(h.get("x-ratelimit-reset-requests"))
            if reset is not None and seen + reset > at:
                used_rpd = rpd_limit - int(h.get("x-ratelimit-remaining-requests", rpd_limit))
                used_rpd += sum(1 for e in calls if e["_at"] > seen)
                exact_rpd = True
        except ValueError:
            pass
        try:
            tpm_limit = int(h.get("x-ratelimit-limit-tokens", tpm_limit))
            reset = parse_duration(h.get("x-ratelimit-reset-tokens"))
            if reset is not None and seen + reset > at:
                used_tpm = tpm_limit - int(h.get("x-ratelimit-remaining-tokens", tpm_limit))
                resets_tpm, exact_tpm = seen + reset, True
        except ValueError:
            pass
    if not exact_tpm:
        recent = [e for e in calls if e["_at"] > at - MINUTE]
        used_tpm = sum(int(e.get("tokens", 0)) for e in recent)
        resets_tpm = recent[0]["_at"] + MINUTE if recent else None
    snap.meters.append(Meter("rpd", "Requests · today", used_rpd, rpd_limit, resets_rpd, exact_rpd))
    snap.meters.append(Meter("tpm", "Tokens · per minute", used_tpm, tpm_limit, resets_tpm, exact_tpm))
    return snap


def probe(model: str) -> str:
    """One ~20-token request, recorded like any call. Returns a status line."""
    from src.llm.provider import provider_for_model

    provider = provider_for_model(model)
    try:
        provider.probe(model)
        return "ok"
    except Exception as exc:  # noqa: BLE001 - reported to the user, never raised in the UI
        parsed = parse_rate_limit_error(str(exc))
        if parsed:
            return f"rate limited ({parsed['kind'].upper()})"
        return f"check failed: {str(exc)[:120]}"


def humanize_until(moment: Optional[datetime], at: Optional[datetime] = None, verb: str = "Resets") -> str:
    """'Resets in 3 hr 33 min', in the style of the Claude usage panel.

    Rolling windows pass verb="Frees": capacity returns gradually from that moment, not all at once.
    """
    if not moment:
        return "Full"
    seconds = int((moment - (at or now())).total_seconds())
    if seconds <= 0:
        return {"Resets": "Resetting now", "Frees": "Freeing now"}.get(verb, "Now")
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{verb} in {hours} hr {minutes} min"
    if minutes:
        return f"{verb} in {minutes} min"
    return f"{verb} in {secs} s"
