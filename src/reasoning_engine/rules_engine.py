"""Deterministic SLA decision procedure.

An explicit encoding of docs/sla_policy.md as a decision tree over the facts
produced by `src.evidence_extraction.extractor`. It serves three purposes:

1. **Research baseline.** A transparent, non-learned adjudicator that the LLM
   engines are compared against (alongside majority-class and random baselines).
2. **Cross-check.** Every LLM decision is compared with the rules decision; a
   disagreement is surfaced in the UI as a reason for human attention.
3. **Offline demo.** It runs with no API key, so the application never fails
   in front of an audience.

It reads only the SLA and the extracted facts. It contains no case IDs and
never loads ground truth. Each step it takes is recorded in `trace` so the
UI can show *why* it reached the outcome.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from src.clause_matching.sla_clauses import sla_version
from src.evidence_extraction.extractor import (
    COD_ROUNDING_TOLERANCE_INR,
    CaseFacts,
    extract_facts,
)
from src.reasoning_engine.result import Adjudication

RULES_MODEL = "rules-engine"


class _Builder:
    def __init__(self, facts: CaseFacts):
        self.facts = facts
        self.trace: List[Dict[str, str]] = []

    def step(self, clause: str, question: str, answer: str, outcome: str = "continue") -> None:
        self.trace.append({"clause": clause, "question": question, "answer": answer, "outcome": outcome})

    def done(
        self,
        decision: str,
        primary: str,
        supporting: List[str],
        evidence_keys: List[str],
        rationale: str,
        resolution: str,
        confidence: float,
        refund: Optional[float] = None,
    ) -> Dict[str, Any]:
        evidence = self.facts.sources(*evidence_keys)
        return {
            "decision": decision,
            "primary_clause_id": primary,
            "supporting_clause_ids": [c for c in dict.fromkeys(supporting) if c != primary],
            "evidence_ids_used": evidence,
            "rationale": rationale,
            "resolution_type": resolution,
            "refund_amount_inr": refund,
            "confidence": confidence,
        }


def _fmt_h(hours: Optional[float]) -> str:
    return "unknown" if hours is None else f"{hours:.1f} h"


# ---------------------------------------------------------------------------
# Damaged goods — SLA section 3
# ---------------------------------------------------------------------------

def _damaged_goods(b: _Builder) -> Dict[str, Any]:
    f = b.facts
    hours = f.get("hours_to_report")
    pod = f.get("pod_condition")
    window = f.get("reporting_window_h")

    prior = f.get("prior_claims_90d", 0) or 0
    b.step("SLA-DG-09", "3+ damaged-goods claims from this customer in 90 days?", f"{prior} prior claims",
           "stop" if prior >= 3 else "continue")
    if prior >= 3:
        return b.done(
            "ESCALATE", "SLA-DG-09", ["SLA-DG-01"], ["prior_claims_90d", "hours_to_report"],
            f"The customer has {prior} prior damaged-goods claims in the rolling 90-day window. "
            "SLA-DG-09 routes repeat claimants to manual fraud review regardless of the merit of this claim.",
            "MANUAL_REVIEW", 0.9,
        )

    # Effective PoD reading under SLA-PRI-01
    effective = pod
    if pod == "UNUSABLE" and f.get("independent_damage_corroboration"):
        effective = "DAMAGED_CORROBORATED"
    b.step("SLA-PRI-01", "Can the PoD photo be relied on?",
           {"UNUSABLE": "no — flagged unusable", "DAMAGED": "yes — shows damage",
            "INTACT": "yes — shows intact package"}.get(pod, "unclear")
           + ("; transit damage independently corroborated (hub exception / agent)"
              if effective == "DAMAGED_CORROBORATED" else ""))

    b.step("SLA-DG-01/02", "Reported within the reporting window?",
           f"{_fmt_h(hours)} after PoD vs {window:.0f} h window",
           "continue" if f.get("within_window") else "stop")
    if f.get("within_window") is False:
        supporting = ["SLA-DG-02"] if pod == "DAMAGED" else []
        return b.done(
            "REJECT", "SLA-DG-01", supporting + ["SLA-GEN-03"], ["hours_to_report", "pod_condition"],
            f"The claim was first reported {_fmt_h(hours)} after the PoD timestamp. "
            + ("Even the 7-day exception under SLA-DG-02 has lapsed. " if pod == "DAMAGED" else
               "The PoD photo does not show external package damage, so the 7-day exception "
               "under SLA-DG-02 does not apply and the 48-hour default governs. ")
            + "Under SLA-DG-01 the claim is presumptively ineligible.",
            "NO_STANDARD_RESOLUTION", 0.9,
        )

    has_evidence = bool(
        f.get("unboxing_evidence") or f.get("damage_photo") or f.get("damage_description_specific")
    )
    b.step("SLA-DG-04", "Unboxing media, damage photo, or a specific damage description?",
           "yes" if has_evidence else "no", "continue" if has_evidence else "stop")
    if not has_evidence:
        return b.done(
            "REJECT", "SLA-DG-04", ["SLA-DG-01"], ["customer_reports_damage", "unboxing_evidence"],
            "The claim is within the reporting window but does not meet the minimum evidence "
            "standard of SLA-DG-04: there is no unboxing media, no photo of the damage, and the "
            "description does not identify the type and location of the damage.",
            "NO_STANDARD_RESOLUTION", 0.75,
        )

    high_value = bool(f.get("high_value"))
    unboxing = bool(f.get("unboxing_evidence"))
    b.step("SLA-DG-03", "High-value order (≥ ₹5,000) without unboxing evidence?",
           f"order ₹{f.get('order_value_inr', 0):,.0f}; unboxing {'provided' if unboxing else 'not provided'}",
           "stop" if high_value and not unboxing else "continue")
    if high_value and not unboxing:
        supporting = ["SLA-DG-08"] + (["SLA-DG-05"] if pod == "INTACT" else [])
        return b.done(
            "ESCALATE", "SLA-DG-03", supporting, ["high_value", "unboxing_evidence", "pod_condition",
                                                  "agent_asserts_intact", "customer_reports_damage"],
            f"The claim was reported within the window ({_fmt_h(hours)}). The order value of "
            f"₹{f.get('order_value_inr', 0):,.0f} meets the SLA-DG-03 high-value threshold, which "
            "requires unboxing evidence, and none was provided. "
            + ("The PoD shows the package intact at handover. " if pod == "INTACT" else "")
            + "The requirement is unmet but the narrative is specific, so the record cannot settle "
            "fault either way: under SLA-DG-08 the case goes to manual review rather than being "
            "auto-approved or auto-rejected.",
            "MANUAL_REVIEW", 0.7,
        )

    if effective == "DAMAGED" and f.get("customer_reports_damage"):
        b.step("SLA-DG-06", "PoD shows external damage AND customer's damage is consistent with it?",
               "yes", "stop")
        return b.done(
            "APPROVE", "SLA-DG-06", ["SLA-DG-01", "SLA-DG-02", "SLA-DG-07"],
            ["pod_condition", "customer_reports_damage", "damage_photo", "hours_to_report"],
            f"The claim was reported {_fmt_h(hours)} after delivery, within the window. The PoD photo "
            "itself shows visible external package damage, and the customer's description and photo "
            "of the product damage are consistent with it. Under SLA-DG-06 the claim is approved "
            "without further evidence; the default remedy under SLA-DG-07 is a free replacement.",
            "REPLACEMENT_DEFAULT", 0.92,
        )

    if effective == "DAMAGED_CORROBORATED":
        b.step("SLA-DG-03", "Below ₹5,000 — resolvable on narrative + corroborating records?", "yes", "stop")
        return b.done(
            "APPROVE", "SLA-DG-03", ["SLA-PRI-01", "SLA-DG-04", "SLA-DG-07"],
            ["pod_record_doubted", "independent_damage_corroboration", "customer_reports_damage",
             "damage_photo", "hours_to_report"],
            f"The claim was reported within the window ({_fmt_h(hours)}). The PoD image is flagged "
            "unusable, which under SLA-PRI-01 is a documented reason not to rely on it. With the PoD "
            "discounted, a hub exception and/or the agent's own statement independently corroborate "
            "transit damage, and the customer's photo and specific description satisfy SLA-DG-04. "
            "As the order is below the ₹5,000 threshold, SLA-DG-03 allows resolution on this "
            "evidence; the default remedy is replacement (SLA-DG-07).",
            "REPLACEMENT_DEFAULT", 0.78,
        )

    if pod == "INTACT" and unboxing:
        b.step("SLA-DG-04", "PoD intact but unboxing evidence documents the damage?", "yes", "stop")
        return b.done(
            "APPROVE", "SLA-DG-04", ["SLA-DG-03", "SLA-DG-07"],
            ["unboxing_evidence", "pod_condition", "customer_reports_damage", "hours_to_report"],
            "The claim is within the window. The outer package was intact at handover, which is not "
            "inconsistent with internal damage, and the customer's unboxing evidence documents the "
            "damage as received — the strongest category of evidence under SLA-DG-04(a). The claim "
            "is approved with replacement as the default remedy.",
            "REPLACEMENT_DEFAULT", 0.68,
        )

    # PoD intact (or unusable without corroboration), no unboxing evidence
    b.step("SLA-DG-05/08", "PoD intact/unreliable, no unboxing evidence, specific narrative?",
           "yes — fault cannot be determined from the record", "stop")
    return b.done(
        "ESCALATE", "SLA-DG-08", ["SLA-DG-05", "SLA-DG-01"],
        ["pod_condition", "agent_asserts_intact", "customer_reports_damage", "unboxing_evidence"],
        f"The claim was reported within the window ({_fmt_h(hours)}). "
        + ("The PoD shows the package intact at handover" if pod == "INTACT"
           else "The PoD photo cannot be relied on and nothing independently corroborates transit damage")
        + " and there is no unboxing evidence, so SLA-DG-05 removes auto-approval. The customer's "
        "description is specific and plausible, so fault cannot be determined from the record: "
        "under SLA-DG-08 the case is escalated to manual review.",
        "MANUAL_REVIEW", 0.72,
    )


# ---------------------------------------------------------------------------
# COD mismatch — SLA section 4
# ---------------------------------------------------------------------------

def _cod(b: _Builder) -> Dict[str, Any]:
    f = b.facts
    hours = f.get("hours_to_report")
    total = f.get("invoice_total_inr") or 0.0
    claimed = f.get("claimed_collected_inr")
    status = f.get("recon_status")
    recon = f.get("recon_amount_inr")

    b.step("SLA-COD-01", "Reported within 24 hours of PoD?", f"{_fmt_h(hours)}",
           "continue" if f.get("within_window") else "stop")
    if f.get("within_window") is False:
        return b.done(
            "REJECT", "SLA-COD-01", ["SLA-GEN-03"], ["hours_to_report"],
            f"The COD mismatch was first reported {_fmt_h(hours)} after the PoD timestamp, outside "
            "the 24-hour window of SLA-COD-01 (cash is reconciled on a daily cycle). The claim is "
            "not eligible for review.",
            "NO_STANDARD_RESOLUTION", 0.9,
        )

    b.step("SLA-COD-03/06", "Is there a reconciliation record for the order?", str(status))
    if status != "RECORDED":
        if claimed is None:
            b.step("SLA-COD-02", "Does the customer state the amount collected?", "no", "stop")
            return b.done(
                "ESCALATE", "SLA-COD-06", ["SLA-COD-02", "SLA-COD-01"],
                ["recon_status", "claimed_collected_inr"],
                "No reconciliation record exists, so SLA-COD-06 would default to a customer-favourable "
                "refund — but the customer has not stated the amount collected (SLA-COD-02), so the "
                "disputed excess cannot be computed. Escalated to obtain the amount.",
                "MANUAL_REVIEW", 0.6,
            )
        excess = round(claimed - total, 2)
        b.step("SLA-COD-06", "Absent record → customer-favourable refund of disputed excess",
               f"₹{claimed:,.0f} − ₹{total:,.0f} = ₹{excess:,.2f}", "stop")
        if excess <= 0:
            return b.done(
                "REJECT", "SLA-COD-06", ["SLA-COD-01"], ["claimed_collected_inr", "recon_status"],
                "No reconciliation record exists, but the amount the customer states was collected does "
                "not exceed the invoice total, so there is no excess to refund.",
                "NO_CUSTOMER_ACTION", 0.7, 0.0,
            )
        return b.done(
            "APPROVE", "SLA-COD-06", ["SLA-COD-01", "SLA-COD-07", "SLA-COD-08"],
            ["recon_status", "claimed_collected_inr", "hours_to_report"],
            f"The claim was reported {_fmt_h(hours)} after delivery, within 24 hours. The delivery "
            "partner has no reconciliation record for this order (system failure), which SLA-COD-06 "
            "treats as an operational failure on the company side: the claim defaults to a "
            f"customer-favourable refund of the disputed excess, ₹{claimed:,.0f} − ₹{total:,.0f} = "
            f"₹{excess:,.2f}. SLA-COD-06 takes precedence over the ₹10 tolerance in SLA-COD-07. "
            "Refund within 5 business days (SLA-COD-08).",
            "REFUND", 0.85, excess,
        )

    diff = round(recon - total, 2)
    b.step("SLA-COD-07", "Reconciled discrepancy within ₹10 rounding tolerance?",
           f"₹{abs(diff):,.2f}", "stop" if 0 < abs(diff) <= COD_ROUNDING_TOLERANCE_INR else "continue")
    if 0 < abs(diff) <= COD_ROUNDING_TOLERANCE_INR:
        return b.done(
            "REJECT", "SLA-COD-07", ["SLA-COD-03", "SLA-COD-01"], ["recon_amount_inr", "invoice_total_inr"],
            f"The reconciliation log differs from the invoice by ₹{abs(diff):,.2f}, within the ₹10 "
            "rounding/change tolerance of SLA-COD-07, which is not eligible for formal dispute "
            "resolution.",
            "NO_STANDARD_RESOLUTION", 0.85,
        )

    if diff > 0:
        conflict = claimed is not None and abs(claimed - recon) > 0.01
        b.step("SLA-COD-04", "Reconciliation higher than invoice → refund the excess",
               f"₹{recon:,.0f} − ₹{total:,.0f} = ₹{diff:,.2f}"
               + (f" (customer claimed ₹{claimed:,.0f}; structured record governs)" if conflict else ""),
               "stop")
        return b.done(
            "APPROVE", "SLA-COD-04",
            ["SLA-COD-01", "SLA-COD-03", "SLA-COD-08"] + (["SLA-PRI-01"] if conflict else []),
            ["recon_amount_inr", "invoice_total_inr", "hours_to_report"]
            + (["agent_stated_amount_inr"] if conflict else ["claimed_collected_inr"]),
            f"The claim was reported within 24 hours ({_fmt_h(hours)}). The reconciliation log records "
            f"₹{recon:,.0f} against an invoice total of ₹{total:,.0f}, corroborating an overcharge. "
            + (f"The customer claims ₹{claimed:,.0f} was taken, but under SLA-PRI-01 the structured "
               "reconciliation record takes priority over the conflicting narrative. " if conflict else "")
            + f"Under SLA-COD-04 the refund is reconciliation amount − order total = ₹{diff:,.2f}, "
            "payable within 5 business days (SLA-COD-08).",
            "REFUND", 0.9 if not conflict else 0.82, diff,
        )

    if diff < 0:
        b.step("SLA-COD-05", "Reconciliation lower than invoice → undercharge, no customer action", "yes", "stop")
        return b.done(
            "REJECT", "SLA-COD-05", ["SLA-COD-01", "SLA-COD-03"],
            ["recon_amount_inr", "invoice_total_inr", "agent_stated_amount_inr", "claimed_collected_inr"],
            f"The claim was reported within 24 hours. The reconciliation log shows ₹{recon:,.0f} "
            f"collected against an invoice of ₹{total:,.0f} — an undercharge, not an overcharge. "
            "Under SLA-COD-05 this needs no customer-facing action; the company absorbs or audits "
            "the shortfall internally.",
            "NO_CUSTOMER_ACTION", 0.85, 0.0,
        )

    # Reconciliation matches the invoice
    corroboration = bool(f.get("customer_corroboration"))
    b.step("SLA-COD-03", "Log matches invoice — does the customer offer corroborating evidence?",
           "yes" if corroboration else "no", "continue" if corroboration else "stop")
    if not corroboration:
        return b.done(
            "REJECT", "SLA-COD-03", ["SLA-COD-01", "SLA-PRI-01"],
            ["recon_amount_inr", "invoice_total_inr", "claimed_collected_inr"],
            f"The reconciliation log records ₹{recon:,.0f}, matching the invoice total. The customer "
            "offers no corroborating evidence of the amount handed over, so under SLA-COD-03 the "
            "overcharge claim is presumptively rejected.",
            "NO_STANDARD_RESOLUTION", 0.85, 0.0,
        )

    confirming = f.get("sources_confirming_correct_payment", 0) or 0
    verifiable = f.get("corroboration_verifiable")
    b.step("SLA-COD-09", "Is the customer's evidence verifiable, and do ≥2 independent sources say the correct "
           "amount was paid?", f"verifiable: {'yes' if verifiable else 'no'}; confirming sources: {confirming}",
           "stop")
    return b.done(
        "ESCALATE", "SLA-COD-03", ["SLA-COD-09", "SLA-PRI-01", "SLA-COD-01"],
        ["recon_amount_inr", "agent_stated_amount_inr", "customer_corroboration", "claimed_collected_inr"],
        f"The reconciliation log (₹{recon:,.0f}) matches the invoice, which would ordinarily reject the "
        "claim under SLA-COD-03 — but the customer has supplied corroborating evidence, which displaces "
        "the presumption. "
        + ("That evidence cannot be verified (no link to the handover or capture metadata), while "
           f"{confirming} independent records say the correct amount was paid. " if not verifiable else "")
        + "Whether the claim is mistaken or knowingly false (SLA-COD-09 account-level review) is a "
        "factual question the record cannot settle, so the case is escalated to manual review.",
        "MANUAL_REVIEW", 0.62,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def adjudicate_rules(case: Dict[str, Any], facts: Optional[CaseFacts] = None,
                     retrieved_clause_ids: Optional[List[str]] = None) -> Adjudication:
    started = time.perf_counter()
    facts = facts or extract_facts(case)
    builder = _Builder(facts)

    if case.get("dispute_type") == "DAMAGED_GOODS":
        payload = _damaged_goods(builder)
    elif case.get("dispute_type") == "COD_MISMATCH":
        payload = _cod(builder)
    else:
        raise ValueError(f"Unsupported dispute type: {case.get('dispute_type')}")

    return Adjudication(
        case_id=case["case_id"],
        model=RULES_MODEL,
        sla_version=sla_version(),
        latency_seconds=round(time.perf_counter() - started, 4),
        retrieved_clause_ids=retrieved_clause_ids or [],
        engine="rules",
        trace=builder.trace,
        facts=facts.to_dict(),
        **payload,
    )
