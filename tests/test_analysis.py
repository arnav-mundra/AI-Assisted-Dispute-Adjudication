from src.evaluation.analysis import (
    collect_errors,
    confidence_floor_sweep,
    consistency,
    error_kind,
    guard_effect,
    guarded,
    wilson_interval,
)


def test_guard_escalates_only_on_disagreement():
    agree = {"decision": "REJECT", "cross_check": {"rules_decision": "REJECT", "agrees": True}}
    differ = {"decision": "REJECT", "cross_check": {"rules_decision": "APPROVE", "agrees": False}}
    assert guarded(agree)["decision"] == "REJECT"
    assert guarded(differ)["decision"] == "ESCALATE"
    assert guarded({"decision": "REJECT"})["decision"] == "REJECT"


def test_confidence_floor_sweep():
    run = {
        "config": {"dataset": "pilot", "engine": "llm", "model": "m/x", "prompt_style": "facts"},
        "predictions": [
            {"case_id": "DG-004", "decision": "REJECT", "confidence": 0.55},   # wrong, low confidence
            {"case_id": "DG-001", "decision": "APPROVE", "confidence": 0.85},  # right, high confidence
        ],
    }
    by_floor = {row["floor"]: row for row in confidence_floor_sweep([run], floors=(0.6, 0.9))}
    assert by_floor[0.6]["errors_fixed"] == 1 and by_floor[0.6]["correct_sent_to_review"] == 0
    assert by_floor[0.9]["errors_fixed"] == 1 and by_floor[0.9]["correct_sent_to_review"] == 1


def test_guarded_runs_are_not_simulated_again():
    run = {"config": {"dataset": "pilot", "engine": "llm", "model": "m/x", "prompt_style": "facts",
                      "guard": True}, "predictions": []}
    assert guard_effect([run]) == [] and confidence_floor_sweep([run]) == []


def test_guard_effect_counts_fixes_and_review_cost():
    run = {
        "config": {"dataset": "pilot", "engine": "llm", "model": "m/x", "prompt_style": "facts"},
        "predictions": [
            # DG-004 is ESCALATE in the reference: the guard fixes it.
            {"case_id": "DG-004", "decision": "REJECT",
             "cross_check": {"rules_decision": "ESCALATE", "agrees": False}},
            # DG-001 is APPROVE in the reference: the guard sends a correct decision to review.
            {"case_id": "DG-001", "decision": "APPROVE",
             "cross_check": {"rules_decision": "REJECT", "agrees": False}},
        ],
    }
    [row] = guard_effect([run])
    assert row["escalated_by_guard"] == 2
    assert row["errors_fixed"] == 1
    assert row["correct_sent_to_review"] == 1
    assert row["accuracy_before"] == row["accuracy_after"] == 0.5


def _run(run_id, decisions, style="facts", accuracy=0.5):
    return {
        "run_id": run_id,
        "config": {"dataset": "pilot", "engine": "llm", "model": "m/x", "prompt_style": style},
        "metrics": {"n": len(decisions), "decision_accuracy": accuracy, "escalation_recall": 0.0},
        "predictions": [
            {"case_id": case_id, "decision": decision, "cross_check": {"rules_decision": "ESCALATE"}}
            for case_id, decision in decisions.items()
        ],
    }


def test_wilson_interval_is_bounded_and_contains_the_point_estimate():
    low, high = wilson_interval(8, 10)
    assert 0.0 <= low < 0.8 < high <= 1.0
    assert wilson_interval(0, 0) == (0.0, 0.0)
    assert wilson_interval(10, 10)[1] == 1.0


def test_error_kinds():
    assert error_kind("APPROVE", "APPROVE") is None
    assert error_kind("REJECT", "ESCALATE") == "missed_escalation"
    assert error_kind("ESCALATE", "REJECT") == "over_escalation"
    assert error_kind("APPROVE", "REJECT") == "polarity"
    assert error_kind("UNPARSED", "REJECT") == "unparsed"


def test_collect_errors_joins_reference_labels():
    # DG-004 is labelled ESCALATE in the frozen pilot ground truth.
    errors = collect_errors([_run("r1", {"DG-004": "REJECT", "DG-001": "APPROVE"})])
    assert [e["case_id"] for e in errors] == ["DG-004"]
    assert errors[0]["kind"] == "missed_escalation"
    assert errors[0]["rules_correct"] is True


def test_consistency_flags_cases_that_change_between_repeats():
    runs = [_run("r1", {"DG-001": "APPROVE", "DG-004": "REJECT"}),
            _run("r2", {"DG-001": "APPROVE", "DG-004": "ESCALATE"})]
    [summary] = consistency(runs)
    assert summary["runs"] == 2
    assert summary["unstable_cases"] == {"DG-004": {"REJECT": 1, "ESCALATE": 1}}
    assert summary["pairwise_agreement"] == 0.5
