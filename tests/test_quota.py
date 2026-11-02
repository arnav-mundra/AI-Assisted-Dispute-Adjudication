import json
from datetime import datetime, timedelta, timezone

from src.llm import quota

MODEL = "openai/gpt-oss-120b"
T0 = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)
GROQ_TPD_ERROR = (
    "Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-120b` "
    "in organization `org_x` service tier `on_demand` on tokens per day (TPD): Limit 200000, "
    "Used 199734, Requested 4512. Please try again in 30m33.12s. Need more tokens? Upgrade to "
    "Dev Tier today', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"
)


def _write(log, *entries):
    with log.open("a", encoding="utf-8") as file:
        for entry in entries:
            file.write(json.dumps(entry) + "\n")


def _call(at, tokens, headers=None):
    entry = {"at": at.isoformat(), "kind": "call", "provider": "groq", "model": MODEL, "tokens": tokens}
    if headers:
        entry["headers"] = headers
    return entry


def test_parse_duration():
    assert quota.parse_duration("7.66s") == timedelta(seconds=7.66)
    assert quota.parse_duration("2m59.56s") == timedelta(minutes=2, seconds=59.56)
    assert quota.parse_duration("1h2m3s") == timedelta(hours=1, minutes=2, seconds=3)
    assert quota.parse_duration("120ms") == timedelta(milliseconds=120)
    assert quota.parse_duration("") is None


def test_parse_groq_tpd_error():
    parsed = quota.parse_rate_limit_error(GROQ_TPD_ERROR)
    assert parsed["kind"] == "tpd"
    assert parsed["limit"] == 200000 and parsed["used"] == 199734 and parsed["requested"] == 4512
    assert abs(parsed["retry_seconds"] - (30 * 60 + 33.12)) < 1e-6
    assert quota.parse_rate_limit_error("Error code: 503 overloaded") is None


def test_daily_tokens_are_a_rolling_estimate(tmp_path):
    log = tmp_path / "u.jsonl"
    _write(log, _call(T0 - timedelta(hours=25), 9000),          # outside the window
           _call(T0 - timedelta(hours=3), 4000), _call(T0 - timedelta(hours=1), 5000))
    snap = quota.snapshot(MODEL, at=T0, log=log, runs_dir=tmp_path)
    tpd = snap.meter("tpd")
    assert tpd.used == 9000 and tpd.limit == 200000 and not tpd.exact
    assert tpd.resets_at == T0 - timedelta(hours=3) + timedelta(hours=24)


def test_rate_limit_error_makes_daily_tokens_exact(tmp_path):
    log = tmp_path / "u.jsonl"
    # record_error stamps the real clock, so this test is anchored to it rather than T0.
    _write(log, _call(quota.now() - timedelta(hours=2), 4000))
    quota.record_error("groq", MODEL, GROQ_TPD_ERROR, log=log)
    snap = quota.snapshot(MODEL, at=quota.now() + timedelta(seconds=5), log=log, runs_dir=tmp_path)
    tpd = snap.meter("tpd")
    assert tpd.exact and tpd.used == 199734
    assert snap.blocked_until is not None


def test_headers_make_requests_and_minute_tokens_exact(tmp_path):
    log = tmp_path / "u.jsonl"
    headers = {"x-ratelimit-limit-requests": "1000", "x-ratelimit-remaining-requests": "961",
               "x-ratelimit-reset-requests": "2m0s", "x-ratelimit-limit-tokens": "8000",
               "x-ratelimit-remaining-tokens": "3000", "x-ratelimit-reset-tokens": "30s"}
    _write(log, _call(T0 - timedelta(seconds=10), 20, headers))
    snap = quota.snapshot(MODEL, at=T0, log=log, runs_dir=tmp_path)
    rpd, tpm = snap.meter("rpd"), snap.meter("tpm")
    assert rpd.exact and rpd.used == 39 and rpd.limit == 1000
    assert tpm.exact and tpm.used == 5000 and tpm.resets_at == T0 + timedelta(seconds=20)
    # Once the minute has passed, the header reading is stale and the meter falls back.
    later = quota.snapshot(MODEL, at=T0 + timedelta(minutes=2), log=log, runs_dir=tmp_path)
    assert later.meter("tpm").used == 0


def test_backfill_from_saved_runs(tmp_path):
    runs = tmp_path / "runs"
    runs.mkdir()
    (runs / "x_pilot_llm_gpt-oss-120b_facts.json").write_text(json.dumps({
        "created_at": (T0 - timedelta(hours=2)).isoformat(),
        "config": {"model": MODEL},
        "predictions": [{"usage": {"input_tokens": 3000, "output_tokens": 500}}] * 2,
    }), encoding="utf-8")
    snap = quota.snapshot(MODEL, at=T0, log=tmp_path / "empty.jsonl", runs_dir=runs)
    assert snap.meter("tpd").used == 7000
    assert snap.meter("rpd").used == 2  # one request per saved prediction


def test_unknown_model_has_no_snapshot(tmp_path):
    assert quota.snapshot("claude-opus-5", log=tmp_path / "u.jsonl", runs_dir=tmp_path) is None


def test_humanize_until():
    assert quota.humanize_until(None) == "Full"
    assert quota.humanize_until(T0 + timedelta(hours=3, minutes=33, seconds=5), at=T0) == "Resets in 3 hr 33 min"
    assert quota.humanize_until(T0 + timedelta(seconds=42), at=T0) == "Resets in 42 s"
    assert quota.humanize_until(T0 - timedelta(seconds=1), at=T0) == "Resetting now"
    assert quota.humanize_until(T0 + timedelta(minutes=5), at=T0, verb="Frees") == "Frees in 5 min"
    assert quota.humanize_until(T0, at=T0, verb="Frees") == "Freeing now"
