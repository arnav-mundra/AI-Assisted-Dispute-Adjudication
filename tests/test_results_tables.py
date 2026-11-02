"""The results tables must flag weak runs and leave no held-out run in the output."""

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "results_tables", Path(__file__).resolve().parents[1] / "scripts" / "results_tables.py")
results_tables = importlib.util.module_from_spec(spec)
spec.loader.exec_module(results_tables)


def _run(run_id, dataset, accuracy, **config):
    return {
        "run_id": run_id,
        "config": {"engine": "llm", "model": "openai/gpt-oss-20b", "prompt_style": "cot", "dataset": dataset,
                   "dense": True, **config},
        "metrics": {"n": 10, "decision_accuracy": accuracy, "escalation_recall": 0.5, "clause_f1": 0.5,
                    "refund_accuracy": 1.0, "per_case": [{"grounding_issue": False}]},
        "baselines": {"majority_class": {"label": "APPROVE", "decision_accuracy": 0.5, "escalation_recall": 0.0}},
        "predictions": [],
    }


def test_summary_flags_baseline_and_excludes_heldout():
    summary = results_tables.render_summary([_run("weak-run", "pilot", 0.4), _run("sealed-run", "heldout", 0.9)])
    assert "weak-run" in summary and "At or below the majority-class baseline" in summary
    assert "sealed-run" not in summary
    assert "counterfactual · gpt-oss-120b · facts" in summary  # listed under "Not run yet"


def test_guarded_runs_stay_out_of_the_tables():
    guarded = _run("guarded-run", "pilot", 1.0, guard=True)
    assert "guarded-run" not in results_tables.render_summary([guarded])
