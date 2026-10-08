"""Phase 6 — running the pipeline over a dataset and scoring it.

Ground truth is joined to predictions here and only here, after inference, per
the leakage controls in `docs/phase0/evaluation_protocol.md`. `experiment`
runs and saves configurations, `metrics` scores them, `counterfactuals`
builds the stress set.
"""
