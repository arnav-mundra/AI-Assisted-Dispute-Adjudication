"""Counterfactual stress set: pilot cases with one SLA-relevant fact changed.

    python -m src.evaluation.counterfactuals        # (re)writes data/synthetic/counterfactual/

Each perturbation edits a pilot case so that a single clause condition flips
(the report arrives after the window, the reconciliation log moves, unboxing
evidence disappears, the narrative is paraphrased...). Its expected outcome is
written by hand *per perturbation*, from the SLA text, in the `expect` field
below — it is never produced by running the rules engine or a model.

Purpose: a regression and robustness suite that is not the data the pipeline
was tuned on. Caveat for the write-up: the expected labels were written by the
same team that built the pipeline, so treat this as a stress test, not as an
independent ground truth; ideally a second annotator reviews each `expect`.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List

from src.config.paths import COUNTERFACTUAL_CASES_FILE, COUNTERFACTUAL_LABELS_FILE, PILOT_CASES_FILE

LABEL_TIMESTAMP = "2026-10-09T03:00:00+05:30"


def _load_pilot() -> Dict[str, Dict[str, Any]]:
    cases = json.loads(PILOT_CASES_FILE.read_text(encoding="utf-8"))
    return {c["case_id"]: c for c in cases}


def _pod_time(case: Dict[str, Any]) -> datetime:
    pod = next(i for i in case["delivery_evidence"] if i["type"] == "POD")
    return datetime.fromisoformat(pod["timestamp_ist"])


def _stamp(moment: datetime) -> str:
    return moment.replace(microsecond=0).isoformat()


def report_after(hours: float) -> Callable[[Dict[str, Any]], None]:
    """Move all customer evidence so the first message is `hours` after PoD (spacing kept)."""
    def edit(case: Dict[str, Any]) -> None:
        pod = _pod_time(case)
        times = [datetime.fromisoformat(i["timestamp_ist"]) for i in case["customer_evidence"]]
        shift = (pod + timedelta(hours=hours)) - min(times)
        for item in case["customer_evidence"]:
            item["timestamp_ist"] = _stamp(datetime.fromisoformat(item["timestamp_ist"]) + shift)
        for item in case["agent_evidence"]:
            moved = datetime.fromisoformat(item["timestamp_ist"]) + shift
            item["timestamp_ist"] = _stamp(max(moved, pod))
    return edit


def set_text(section: str, index: int, text: str) -> Callable[[Dict[str, Any]], None]:
    def edit(case: Dict[str, Any]) -> None:
        case[section][index]["text"] = text
    return edit


def drop(section: str, evidence_id: str) -> Callable[[Dict[str, Any]], None]:
    def edit(case: Dict[str, Any]) -> None:
        case[section] = [i for i in case[section] if i["evidence_id"] != evidence_id]
    return edit


def set_recon(amount: float) -> Callable[[Dict[str, Any]], None]:
    def edit(case: Dict[str, Any]) -> None:
        recon = next(i for i in case["delivery_evidence"] if i["type"] == "RECONCILIATION_LOG")
        recon.update(status="RECORDED", amount_collected_inr=float(amount),
                     note="Daily cash remittance entry matched to AWB for this order.")
    return edit


def set_order(**fields: Any) -> Callable[[Dict[str, Any]], None]:
    def edit(case: Dict[str, Any]) -> None:
        case["order"].update(fields)
    return edit


def add_delivery_log(evidence_id: str, note: str) -> Callable[[Dict[str, Any]], None]:
    def edit(case: Dict[str, Any]) -> None:
        pod = _pod_time(case)
        case["delivery_evidence"].append({
            "evidence_id": evidence_id, "type": "DELIVERY_LOG",
            "timestamp_ist": _stamp(pod), "note": note,
        })
    return edit


def edit_agent(text: str) -> Callable[[Dict[str, Any]], None]:
    return set_text("agent_evidence", 0, text)


# Each spec: source case, edits, and the hand-written expected outcome.
SPECS: List[Dict[str, Any]] = [
    {
        "id": "CF-101", "from": "DG-003", "edits": [report_after(60)],
        "perturbation": "Intact-PoD claim moved to 60 h after delivery.",
        "expect": {"decision": "REJECT", "clauses": ["SLA-DG-01"], "resolution": "NO_STANDARD_RESOLUTION",
                   "evidence": ["POD-003", "CUSTOMER-005"],
                   "why": "PoD intact, so no SLA-DG-02 extension; 60 h > 48 h → presumptively ineligible (SLA-DG-01)."},
    },
    {
        "id": "CF-102", "from": "DG-001", "edits": [report_after(96)],
        "perturbation": "Damaged-PoD claim moved to 4 days after delivery.",
        "expect": {"decision": "APPROVE", "clauses": ["SLA-DG-02", "SLA-DG-06"], "resolution": "REPLACEMENT_DEFAULT",
                   "evidence": ["POD-001", "CUSTOMER-001", "CUSTOMER-002"],
                   "why": "PoD shows external damage → 7-day window (SLA-DG-02); damage consistent → approve (SLA-DG-06)."},
    },
    {
        "id": "CF-103", "from": "DG-001", "edits": [report_after(200)],
        "perturbation": "Damaged-PoD claim moved to ~8.3 days after delivery.",
        "expect": {"decision": "REJECT", "clauses": ["SLA-DG-01", "SLA-DG-02"], "resolution": "NO_STANDARD_RESOLUTION",
                   "evidence": ["POD-001", "CUSTOMER-001"],
                   "why": "Even the 7-day SLA-DG-02 extension has lapsed → ineligible under SLA-DG-01."},
    },
    {
        "id": "CF-104", "from": "DG-001", "edits": [set_order(order_value_inr=6200.0)],
        "perturbation": "Damaged-PoD case re-priced above the ₹5,000 threshold (no unboxing evidence).",
        "expect": {"decision": "ESCALATE", "clauses": ["SLA-DG-03"], "resolution": "MANUAL_REVIEW",
                   "evidence": ["POD-001", "CUSTOMER-001"],
                   "why": "SLA-DG-03 requires unboxing evidence for ≥ ₹5,000 regardless of window, and is not waived "
                          "by visible PoD damage; requirement unmet but claim plausible → manual review (as DG-004)."},
    },
    {
        "id": "CF-105", "from": "DG-001",
        "edits": [add_delivery_log("DELIVERY-901", "Account history: 3 prior damaged-goods claims from this "
                                                   "customer in the rolling 90-day window.")],
        "perturbation": "Strong damage claim from a customer with 3 prior claims in 90 days.",
        "expect": {"decision": "ESCALATE", "clauses": ["SLA-DG-09"], "resolution": "MANUAL_REVIEW",
                   "evidence": ["DELIVERY-901"],
                   "why": "SLA-DG-09: 3+ claims in 90 days → manual fraud review regardless of merit."},
    },
    {
        "id": "CF-106", "from": "DG-003",
        "edits": [set_text("customer_evidence", 0,
                           "Order ORD-2026-40390 came yesterday and the item I received is damaged. "
                           "Please sort this out.")],
        "perturbation": "Vague narrative ('item is damaged'), no photo, no unboxing.",
        "expect": {"decision": "REJECT", "clauses": ["SLA-DG-04"], "resolution": "NO_STANDARD_RESOLUTION",
                   "evidence": ["CUSTOMER-005"],
                   "why": "SLA-DG-04 requires unboxing media, a damage photo, or a description naming type and "
                          "location of damage; none is present."},
    },
    {
        "id": "CF-107", "from": "DG-002", "edits": [report_after(26)],
        "perturbation": "Late chipped-carafe claim moved inside the 48 h window (PoD intact, no unboxing).",
        "expect": {"decision": "ESCALATE", "clauses": ["SLA-DG-05", "SLA-DG-08"], "resolution": "MANUAL_REVIEW",
                   "evidence": ["POD-002", "CUSTOMER-003", "CUSTOMER-004"],
                   "why": "Within window; PoD intact and no unboxing → SLA-DG-05 removes auto-approval; specific "
                          "plausible claim → SLA-DG-08 manual review (same pattern as DG-003)."},
    },
    {
        "id": "CF-108", "from": "DG-001",
        "edits": [set_text("customer_evidence", 0,
                           "Hello, order ORD-2026-40118 aaj subah aaya. Box ek side se bilkul pichka hua tha "
                           "and the lamp ka ceramic base has a crack across the bottom rim. Please replace.")],
        "perturbation": "Narrative rewritten in Hinglish with different wording.",
        "expect": {"decision": "APPROVE", "clauses": ["SLA-DG-06"], "resolution": "REPLACEMENT_DEFAULT",
                   "evidence": ["POD-001", "CUSTOMER-001", "CUSTOMER-002"],
                   "why": "Same facts as DG-001; only the language of the narrative changes."},
    },
    {
        "id": "CF-109", "from": "COD-001", "edits": [report_after(30)],
        "perturbation": "Overcharge claim moved to 30 h after delivery.",
        "expect": {"decision": "REJECT", "clauses": ["SLA-COD-01"], "resolution": "NO_STANDARD_RESOLUTION",
                   "evidence": ["POD-006", "CUSTOMER-009"],
                   "why": "COD claims must be raised within 24 h of PoD (SLA-COD-01)."},
    },
    {
        "id": "CF-110", "from": "COD-001",
        "edits": [set_recon(1505.0),
                  set_text("customer_evidence", 0,
                           "For order ORD-2026-41004 the invoice says 1500 but the agent took 1505 because he "
                           "had no change. Please refund the extra.")],
        "perturbation": "Overcharge reduced to ₹5, confirmed by the reconciliation log.",
        "expect": {"decision": "REJECT", "clauses": ["SLA-COD-07"], "resolution": "NO_STANDARD_RESOLUTION",
                   "evidence": ["RECON-001", "CUSTOMER-009"],
                   "why": "Discrepancies ≤ ₹10 are rounding/change and not eligible (SLA-COD-07); a log exists, "
                          "so the SLA-COD-06 precedence does not apply."},
    },
    {
        "id": "CF-111", "from": "COD-004",
        "edits": [set_text("customer_evidence", 0,
                           "Order ORD-2026-41377: invoice total is 2350 but the agent collected 2358 and said he "
                           "had no change. Please return the excess.")],
        "perturbation": "No reconciliation log and only an ₹8 disputed excess.",
        "expect": {"decision": "APPROVE", "clauses": ["SLA-COD-06", "SLA-COD-07"], "resolution": "REFUND",
                   "refund": 8.0, "evidence": ["RECON-004", "CUSTOMER-012"],
                   "why": "With no log, SLA-COD-06 takes precedence over SLA-COD-07 even for ≤ ₹10 → refund ₹8."},
    },
    {
        "id": "CF-112", "from": "COD-005", "edits": [drop("customer_evidence", "CUSTOMER-014")],
        "perturbation": "Contested ₹3,500 claim with the customer's photo removed.",
        "expect": {"decision": "REJECT", "clauses": ["SLA-COD-03"], "resolution": "NO_STANDARD_RESOLUTION",
                   "evidence": ["RECON-005", "CUSTOMER-013"],
                   "why": "Log matches invoice and the customer offers no corroborating evidence → presumptive "
                          "rejection (SLA-COD-03)."},
    },
    {
        "id": "CF-113", "from": "COD-002",
        "edits": [set_recon(2450.0),
                  set_text("customer_evidence", 0,
                           "Order ORD-2026-41128 was delivered yesterday evening. The invoice is 2200 but I paid "
                           "2500 in cash. Please refund the difference."),
                  edit_agent("Delivery agent statement recorded by the partner helpdesk: 'I collected 2450 and "
                             "remitted 2450 at the hub.'")],
        "perturbation": "Reconciliation now above invoice (₹2,450 vs ₹2,200); customer claims ₹2,500.",
        "expect": {"decision": "APPROVE", "clauses": ["SLA-COD-04", "SLA-PRI-01"], "resolution": "REFUND",
                   "refund": 250.0, "evidence": ["RECON-002", "CUSTOMER-010"],
                   "why": "Refund = reconciliation − invoice = ₹250 (SLA-COD-04), not the ₹300 the customer "
                          "asserts; structured record governs (SLA-PRI-01)."},
    },
    {
        "id": "CF-114", "from": "COD-003",
        "edits": [set_recon(1800.0),
                  edit_agent("Delivery agent statement recorded by the partner helpdesk: 'I returned 200 in "
                             "change and remitted 1800 for this order.'")],
        "perturbation": "Reconciliation now matches the invoice; customer still claims ₹2,000, no corroboration.",
        "expect": {"decision": "REJECT", "clauses": ["SLA-COD-03"], "resolution": "NO_STANDARD_RESOLUTION",
                   "evidence": ["RECON-003", "CUSTOMER-011"],
                   "why": "Log matches invoice, no corroborating evidence → presumptively rejected (SLA-COD-03)."},
    },
    {
        "id": "CF-115", "from": "COD-001",
        "edits": [set_text("customer_evidence", 0,
                           "Invoice for ORD-2026-41004 was Rs. 1,500 but the delivery boy charged me ₹1,700 in "
                           "cash, said it was a handling fee. Kindly refund.")],
        "perturbation": "Amounts written with 'Rs.', '₹' and thousands separators.",
        "expect": {"decision": "APPROVE", "clauses": ["SLA-COD-04"], "resolution": "REFUND", "refund": 200.0,
                   "evidence": ["RECON-001", "CUSTOMER-009"],
                   "why": "Same facts as COD-001; only the number formatting changes."},
    },
    {
        "id": "CF-116", "from": "DG-004",
        "edits": [set_order(order_value_inr=3900.0)],
        "perturbation": "High-value headphone claim re-priced below ₹5,000 (PoD intact, no unboxing).",
        "expect": {"decision": "ESCALATE", "clauses": ["SLA-DG-05", "SLA-DG-08"], "resolution": "MANUAL_REVIEW",
                   "evidence": ["POD-004", "CUSTOMER-006", "AGENT-004"],
                   "why": "Below threshold, SLA-DG-03 no longer requires unboxing, but PoD intact + no unboxing → "
                          "SLA-DG-05 discretion; specific narrative → SLA-DG-08 manual review."},
    },
]


def build() -> Dict[str, List[Dict[str, Any]]]:
    pilot = _load_pilot()
    cases: List[Dict[str, Any]] = []
    labels: List[Dict[str, Any]] = []

    for spec in SPECS:
        case = copy.deepcopy(pilot[spec["from"]])
        for edit in spec["edits"]:
            edit(case)
        case["case_id"] = spec["id"]
        cases.append(case)

        expect = spec["expect"]
        sub: Dict[str, Any] = {"resolution_type": expect["resolution"]}
        if "refund" in expect:
            sub["refund_amount_inr"] = expect["refund"]
        labels.append({
            "case_id": spec["id"],
            "decision": expect["decision"],
            "governing_clause_ids": expect["clauses"],
            "decisive_evidence_ids": expect["evidence"],
            "contradictory_evidence_ids": [],
            "missing_evidence_ids": [],
            "rationale": expect["why"],
            "sub_decisions": sub,
            "labeler_id": "COUNTERFACTUAL-SPEC",
            "label_timestamp": LABEL_TIMESTAMP,
            "policy_version": "0.1",
            "derived_from": spec["from"],
            "perturbation": spec["perturbation"],
        })
    return {"cases": cases, "labels": labels}


def write() -> None:
    data = build()
    COUNTERFACTUAL_CASES_FILE.parent.mkdir(parents=True, exist_ok=True)
    COUNTERFACTUAL_CASES_FILE.write_text(json.dumps(data["cases"], indent=2, ensure_ascii=False), encoding="utf-8")
    COUNTERFACTUAL_LABELS_FILE.write_text(json.dumps(data["labels"], indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(data['cases'])} counterfactual cases → {COUNTERFACTUAL_CASES_FILE.parent}")


if __name__ == "__main__":
    write()
