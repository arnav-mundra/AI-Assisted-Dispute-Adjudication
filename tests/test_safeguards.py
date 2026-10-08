from src.reasoning_engine import safeguards
from src.reasoning_engine.result import Adjudication


def _result(decision="REJECT", confidence=0.9, rules="REJECT"):
    return Adjudication(
        case_id="X", decision=decision, primary_clause_id="SLA-COD-03", supporting_clause_ids=[],
        evidence_ids_used=["E1"], rationale="r", resolution_type="NO_CUSTOMER_ACTION",
        refund_amount_inr=150.0, confidence=confidence, model="m", sla_version="0.1",
        latency_seconds=0.0, retrieved_clause_ids=[],
        cross_check={"rules_decision": rules, "agrees": rules == decision},
    )


def test_off_by_default():
    result = _result(rules="ESCALATE")
    assert safeguards.apply(result) is None
    assert result.decision == "REJECT"


def test_guard_escalates_on_disagreement_and_keeps_the_original():
    result = _result(rules="ESCALATE")
    record = safeguards.apply(result, guard=True)
    assert result.decision == "ESCALATE" and result.resolution_type == "MANUAL_REVIEW"
    assert result.refund_amount_inr is None
    assert record["original_decision"] == "REJECT"
    assert result.safeguard == record and "rules engine reached ESCALATE" in record["reasons"][0]
    assert any("manual review" in w for w in result.warnings)


def test_guard_leaves_agreement_alone():
    result = _result(rules="REJECT")
    assert safeguards.apply(result, guard=True) is None


def test_confidence_floor():
    low = _result(confidence=0.55)
    assert safeguards.apply(low, min_confidence=0.7)["original_decision"] == "REJECT"
    high = _result(confidence=0.9)
    assert safeguards.apply(high, min_confidence=0.7) is None


def test_never_downgrades_an_escalation():
    result = _result(decision="ESCALATE", confidence=0.1, rules="APPROVE")
    assert safeguards.apply(result, guard=True, min_confidence=0.9) is None


def test_saved_predictions_round_trip():
    saved = _result(rules="APPROVE").to_dict()
    escalated = safeguards.apply_to_dict(saved, guard=True)
    assert escalated["decision"] == "ESCALATE" and saved["decision"] == "REJECT"
    assert Adjudication.from_dict(escalated).safeguard["original_decision"] == "REJECT"
