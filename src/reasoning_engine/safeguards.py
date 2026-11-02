"""Post-decision safeguards: route doubtful LLM rulings to manual review.

Two optional rules, applied after the model has decided and the rules engine has
cross-checked it:

- guard:           the LLM and the deterministic rules engine disagree -> ESCALATE.
- min_confidence:  the LLM's own confidence is below the floor        -> ESCALATE.

They never turn an ESCALATE into anything else, and they keep the model's
original ruling under `safeguard` so the change is auditable. The same function
runs live (adjudicator.adjudicate) and offline over saved runs
(evaluation.analysis), so simulated and live behaviour cannot drift apart.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def safeguard_reasons(prediction: Dict[str, Any], guard: bool = False,
                      min_confidence: float = 0.0) -> List[str]:
    if prediction.get("decision") == "ESCALATE":
        return []
    reasons = []
    cross = prediction.get("cross_check") or {}
    if guard and cross.get("rules_decision") and cross.get("agrees") is False:
        reasons.append(f"rules engine reached {cross['rules_decision']}")
    confidence = prediction.get("confidence")
    if min_confidence and isinstance(confidence, (int, float)) and confidence < min_confidence:
        reasons.append(f"confidence {confidence:.2f} below the {min_confidence:.2f} floor")
    return reasons


def apply_to_dict(prediction: Dict[str, Any], guard: bool = False,
                  min_confidence: float = 0.0) -> Dict[str, Any]:
    """A copy of a saved prediction with the safeguards applied."""
    reasons = safeguard_reasons(prediction, guard, min_confidence)
    if not reasons:
        return prediction
    return {**prediction, "decision": "ESCALATE", "resolution_type": "MANUAL_REVIEW",
            "refund_amount_inr": None,
            "safeguard": {"original_decision": prediction.get("decision"),
                          "original_resolution_type": prediction.get("resolution_type"),
                          "reasons": reasons}}


def apply(result: Any, guard: bool = False, min_confidence: float = 0.0) -> Optional[Dict[str, Any]]:
    """Apply in place to an `Adjudication`. Returns the safeguard record, or None."""
    reasons = safeguard_reasons(result.to_dict(), guard, min_confidence)
    if not reasons:
        return None
    result.safeguard = {"original_decision": result.decision,
                        "original_resolution_type": result.resolution_type,
                        "reasons": reasons}
    result.decision = "ESCALATE"
    result.resolution_type = "MANUAL_REVIEW"
    result.refund_amount_inr = None
    result.warnings.append("Sent to manual review: " + "; ".join(reasons)
                           + f" (model ruled {result.safeguard['original_decision']}).")
    return result.safeguard
