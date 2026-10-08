"""Phase 4 — SLA-grounded adjudication.

`adjudicator` builds the prompt (three styles), calls a provider from
`src.llm`, and validates the ruling against the SLA and the case.
`rules_engine` encodes the SLA as an explicit decision procedure used as an
offline fallback, a baseline and a cross-check. Both return `Adjudication`
(`result.py`).
"""
