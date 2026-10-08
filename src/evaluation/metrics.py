"""Scoring adjudication runs against frozen reference labels (Phase 6).

Predictions and labels are joined here, after inference, never before.

Clause scoring note — SLA-PRI-02 is a *procedural* clause ("every resolution
must cite a clause"). It is a rule about how to write a decision, not a ground
for one, and the system prompt tells the model not to cite it. One reference
label (COD-005) lists it among its governing clauses. Scoring it would
penalise a model for following its instructions, so procedural clauses are
removed from BOTH the reference set and the predicted set before comparison.
The frozen label file itself is not edited.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Optional, Sequence

DECISIONS = ("APPROVE", "REJECT", "ESCALATE")
PROCEDURAL_CLAUSES = frozenset({"SLA-PRI-02"})
REFUND_TOLERANCE_INR = 1.0
GROUNDING_MARKERS = ("does not exist", "was not among the retrieved", "not valid JSON", "no evidence IDs cited")


def _scored(clauses: Iterable[str]) -> set:
    return {c for c in clauses if c and c not in PROCEDURAL_CLAUSES}


def _prf(tp: int, fp: int, fn: int) -> Dict[str, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def _cited(pred: Dict[str, Any]) -> List[str]:
    primary = pred.get("primary_clause_id") or ""
    return [primary] + [c for c in pred.get("supporting_clause_ids") or [] if c != primary]


def score_case(pred: Dict[str, Any], label: Dict[str, Any]) -> Dict[str, Any]:
    gold_clauses = _scored(label.get("governing_clause_ids", []))
    pred_clauses = _scored(_cited(pred))
    tp = len(gold_clauses & pred_clauses)

    gold_ev = set(label.get("decisive_evidence_ids", []))
    pred_ev = set(pred.get("evidence_ids_used") or [])

    gold_sub = label.get("sub_decisions") or {}
    gold_refund = gold_sub.get("refund_amount_inr")
    pred_refund = pred.get("refund_amount_inr")
    if gold_refund is None:
        refund_ok = None
    else:
        refund_ok = pred_refund is not None and abs(float(pred_refund) - float(gold_refund)) <= REFUND_TOLERANCE_INR

    gold_res = gold_sub.get("resolution_type")
    warnings = pred.get("warnings") or []
    grounding_issue = any(any(m in w for m in GROUNDING_MARKERS) and not w.startswith("repaired")
                          for w in warnings)

    return {
        "case_id": label["case_id"],
        "predicted": pred.get("decision", "UNPARSED"),
        "reference": label["decision"],
        "correct": pred.get("decision") == label["decision"],
        "primary_clause": pred.get("primary_clause_id", ""),
        "primary_in_reference": (pred.get("primary_clause_id") or "") in gold_clauses,
        "clause_tp": tp,
        "clause_fp": len(pred_clauses - gold_clauses),
        "clause_fn": len(gold_clauses - pred_clauses),
        "reference_clauses": sorted(gold_clauses),
        "predicted_clauses": sorted(pred_clauses),
        "evidence_tp": len(gold_ev & pred_ev),
        "evidence_fp": len(pred_ev - gold_ev),
        "evidence_fn": len(gold_ev - pred_ev),
        "resolution_ok": None if gold_res is None else pred.get("resolution_type") == gold_res,
        "refund_ok": refund_ok,
        "predicted_refund": pred_refund,
        "reference_refund": gold_refund,
        "confidence": float(pred.get("confidence") or 0.0),
        "grounding_issue": grounding_issue,
        "cross_check_agrees": (pred.get("cross_check") or {}).get("agrees"),
        "latency_seconds": float(pred.get("latency_seconds") or 0.0),
        "tokens": sum((pred.get("usage") or {}).values()),
    }


def score_run(predictions: Sequence[Dict[str, Any]], labels: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    by_id = {p["case_id"]: p for p in predictions}
    per_case = [score_case(by_id[l["case_id"]], l) for l in labels if l["case_id"] in by_id]
    missing = [l["case_id"] for l in labels if l["case_id"] not in by_id]
    n = len(per_case)
    if not n:
        return {"n": 0, "missing": missing, "per_case": []}

    confusion = {gold: Counter() for gold in DECISIONS}
    for row in per_case:
        confusion.setdefault(row["reference"], Counter())[row["predicted"]] += 1

    per_class = {}
    for cls in DECISIONS:
        tp = confusion.get(cls, Counter())[cls]
        fp = sum(confusion[g][cls] for g in confusion if g != cls)
        fn = sum(v for k, v in confusion.get(cls, Counter()).items() if k != cls)
        per_class[cls] = {**_prf(tp, fp, fn), "support": sum(confusion.get(cls, Counter()).values())}
    present = [c for c in DECISIONS if per_class[c]["support"]]

    clause = _prf(sum(r["clause_tp"] for r in per_case), sum(r["clause_fp"] for r in per_case),
                  sum(r["clause_fn"] for r in per_case))
    evidence = _prf(sum(r["evidence_tp"] for r in per_case), sum(r["evidence_fp"] for r in per_case),
                    sum(r["evidence_fn"] for r in per_case))

    def rate(key: str) -> Optional[float]:
        vals = [r[key] for r in per_case if r[key] is not None]
        return sum(1 for v in vals if v) / len(vals) if vals else None

    correct = [r for r in per_case if r["correct"]]
    wrong = [r for r in per_case if not r["correct"]]
    brier = sum((r["confidence"] - (1.0 if r["correct"] else 0.0)) ** 2 for r in per_case) / n

    return {
        "n": n,
        "missing": missing,
        "decision_accuracy": len(correct) / n,
        "macro_f1": sum(per_class[c]["f1"] for c in present) / len(present) if present else 0.0,
        "per_class": per_class,
        "escalation_recall": per_class["ESCALATE"]["recall"],
        "escalation_precision": per_class["ESCALATE"]["precision"],
        "confusion": {g: dict(confusion[g]) for g in confusion},
        "clause_precision": clause["precision"],
        "clause_recall": clause["recall"],
        "clause_f1": clause["f1"],
        "primary_clause_accuracy": rate("primary_in_reference"),
        "evidence_precision": evidence["precision"],
        "evidence_recall": evidence["recall"],
        "resolution_accuracy": rate("resolution_ok"),
        "refund_accuracy": rate("refund_ok"),
        "grounding_issue_rate": rate("grounding_issue"),
        "cross_check_agreement": rate("cross_check_agrees"),
        "mean_confidence": sum(r["confidence"] for r in per_case) / n,
        "mean_confidence_correct": sum(r["confidence"] for r in correct) / len(correct) if correct else None,
        "mean_confidence_wrong": sum(r["confidence"] for r in wrong) / len(wrong) if wrong else None,
        "brier_score": brier,
        "mean_latency_seconds": sum(r["latency_seconds"] for r in per_case) / n,
        "total_tokens": sum(r["tokens"] for r in per_case),
        "per_case": per_case,
    }


def baselines(labels: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Majority-class and uniform-random reference points for the same label set."""
    counts = Counter(l["decision"] for l in labels)
    n = len(labels) or 1
    majority, majority_n = counts.most_common(1)[0] if counts else ("APPROVE", 0)
    return {
        "majority_class": {
            "label": majority,
            "decision_accuracy": majority_n / n,
            "escalation_recall": 1.0 if majority == "ESCALATE" else 0.0,
        },
        "random_uniform": {
            "decision_accuracy": 1 / 3,
            "escalation_recall": 1 / 3,
        },
    }


HEADLINE = (
    ("decision_accuracy", "Decision accuracy"),
    ("macro_f1", "Macro-F1"),
    ("escalation_recall", "Escalation recall"),
    ("clause_f1", "Clause F1"),
    ("primary_clause_accuracy", "Primary clause in reference"),
    ("resolution_accuracy", "Resolution type accuracy"),
    ("refund_accuracy", "Refund amount accuracy"),
    ("evidence_recall", "Decisive-evidence recall"),
    ("grounding_issue_rate", "Grounding violations"),
    ("brier_score", "Brier score (lower is better)"),
)


def format_summary(metrics: Dict[str, Any]) -> str:
    lines = [f"cases scored: {metrics.get('n', 0)}"]
    for key, label in HEADLINE:
        value = metrics.get(key)
        if value is None:
            continue
        lines.append(f"{label:32} {value:.3f}" if key == "brier_score" else f"{label:32} {value:.1%}")
    return "\n".join(lines)
