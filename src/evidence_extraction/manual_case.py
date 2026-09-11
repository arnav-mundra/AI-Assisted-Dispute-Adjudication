"""Build a dispute case from manual entry.

Produces exactly the dict shape `case_loader.get_case()` returns for pilot
cases, so a manually-entered dispute flows through the same clause retrieval,
adjudication and result rendering with no parallel code path.

This is a stand-in for Phase 2: a human types what the extraction module will
later read out of chat, email and delivery logs. The output contract is the
same either way.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

IST = timezone(timedelta(hours=5, minutes=30))

MANUAL_CASE_PREFIX = "MANUAL"
SLA_VERSION = "0.1"

DAMAGED_GOODS = "DAMAGED_GOODS"
COD_MISMATCH = "COD_MISMATCH"


def _stamp(moment: datetime) -> str:
    return moment.astimezone(IST).replace(microsecond=0).isoformat()


class _EvidenceIds:
    """MANUAL-001, MANUAL-002, ... in the order items are added."""

    def __init__(self) -> None:
        self._next = 0

    def take(self) -> str:
        self._next += 1
        return f"{MANUAL_CASE_PREFIX}-{self._next:03d}"


def build_manual_case(
    *,
    dispute_type: str,
    customer_narrative: str,
    hours_since_pod: float,
    order_value_inr: float,
    order_id: Optional[str] = None,
    agent_statement: str = "",
    # Damaged goods
    pod_shows_damage: bool = False,
    unboxing_evidence: bool = False,
    unboxing_description: str = "",
    prior_claims_90d: int = 0,
    # COD mismatch
    order_total_cod_inr: Optional[float] = None,
    claimed_amount_inr: Optional[float] = None,
    reconciliation_amount_inr: Optional[float] = None,
    reconciliation_available: bool = True,
    reconciliation_note: str = "",
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Assemble a case dict. Raises ValueError on inputs the schema cannot express."""
    if dispute_type not in (DAMAGED_GOODS, COD_MISMATCH):
        raise ValueError(f"Unsupported dispute_type: {dispute_type}")
    if not customer_narrative.strip():
        raise ValueError("A customer narrative is required — it is the claim itself.")
    if hours_since_pod < 0:
        raise ValueError("hours_since_pod cannot be negative.")

    now = now or datetime.now(IST)
    pod_time = now - timedelta(hours=hours_since_pod)

    ids = _EvidenceIds()
    case_id = f"{MANUAL_CASE_PREFIX}-{now.strftime('%Y%m%d%H%M%S')}"

    customer_evidence: List[Dict[str, Any]] = [
        {
            "evidence_id": ids.take(),
            "type": "CHAT_MESSAGE",
            "channel": "support_chat",
            "timestamp_ist": _stamp(now),
            "text": customer_narrative.strip(),
        }
    ]

    if unboxing_evidence:
        customer_evidence.append(
            {
                "evidence_id": ids.take(),
                "type": "PHOTO",
                "channel": "support_chat",
                "timestamp_ist": _stamp(now),
                "text": "Customer-supplied unboxing photo/video attached to the chat.",
                "photo_description": (
                    unboxing_description.strip()
                    or "Customer-supplied unboxing image of the product as received."
                ),
            }
        )

    agent_evidence: List[Dict[str, Any]] = []
    if agent_statement.strip():
        agent_evidence.append(
            {
                "evidence_id": ids.take(),
                "type": "AGENT_STATEMENT",
                "timestamp_ist": _stamp(now),
                "text": (
                    "Delivery agent statement recorded by the partner helpdesk: "
                    f"'{agent_statement.strip()}'"
                ),
            }
        )

    pod_description = (
        "Delivery photo shows visible external damage to the package "
        "(crushing, tearing or staining)."
        if pod_shows_damage
        else "Delivery photo shows the package intact: edges square, seals unbroken, "
             "no visible crushing, tearing or staining."
    )

    delivery_evidence: List[Dict[str, Any]] = [
        {
            "evidence_id": ids.take(),
            "type": "POD",
            "timestamp_ist": _stamp(pod_time),
            "otp_confirmed": True,
            "image_quality": "clear",
            "photo_description": pod_description,
        }
    ]

    order: Dict[str, Any] = {
        "order_id": (order_id or f"ORD-{case_id}").strip(),
        "order_value_inr": float(order_value_inr),
        "order_total_cod_inr": None,
        "entry_mode": "MANUAL",
    }

    if dispute_type == DAMAGED_GOODS:
        if prior_claims_90d:
            # SLA-DG-09 turns on the count, so it must be in the record to be weighed.
            delivery_evidence.append(
                {
                    "evidence_id": ids.take(),
                    "type": "DELIVERY_LOG",
                    "timestamp_ist": _stamp(pod_time),
                    "note": (
                        f"Account history: {prior_claims_90d} prior damaged-goods "
                        f"claim(s) from this customer in the rolling 90-day window."
                    ),
                }
            )
    else:
        total = float(order_total_cod_inr if order_total_cod_inr is not None else order_value_inr)
        order["order_total_cod_inr"] = total
        order["payment_mode"] = "COD"

        if claimed_amount_inr is not None:
            customer_evidence[0]["text"] += (
                f"\n\n[Amount stated by customer as collected: ₹{float(claimed_amount_inr):,.2f}; "
                f"order total per invoice: ₹{total:,.2f}.]"
            )

        if reconciliation_available and reconciliation_amount_inr is not None:
            delivery_evidence.append(
                {
                    "evidence_id": ids.take(),
                    "type": "RECONCILIATION_LOG",
                    "timestamp_ist": _stamp(pod_time + timedelta(hours=3)),
                    "status": "RECORDED",
                    "amount_collected_inr": float(reconciliation_amount_inr),
                    "note": reconciliation_note.strip()
                    or "Delivery-partner daily cash remittance entry matched to this order.",
                }
            )
        else:
            delivery_evidence.append(
                {
                    "evidence_id": ids.take(),
                    "type": "RECONCILIATION_LOG",
                    "timestamp_ist": _stamp(pod_time + timedelta(hours=3)),
                    "status": "UNAVAILABLE",
                    "amount_collected_inr": None,
                    "note": reconciliation_note.strip()
                    or "No reconciliation entry exists for this order.",
                }
            )

    return {
        "case_id": case_id,
        "dispute_type": dispute_type,
        "order": order,
        "customer_evidence": customer_evidence,
        "agent_evidence": agent_evidence,
        "delivery_evidence": delivery_evidence,
        "sla_version": SLA_VERSION,
    }


def is_manual_case(case: Dict[str, Any]) -> bool:
    return str(case.get("case_id", "")).startswith(f"{MANUAL_CASE_PREFIX}-")
