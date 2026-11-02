"""The adjudication result contract shared by every engine (LLM, rules, hybrid)."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

VALID_DECISIONS = {"APPROVE", "REJECT", "ESCALATE"}

RESOLUTION_TYPES = (
    "REPLACEMENT_DEFAULT",
    "REFUND",
    "PARTIAL_REFUND",
    "NO_CUSTOMER_ACTION",
    "NO_STANDARD_RESOLUTION",
    "MANUAL_REVIEW",
)


@dataclass
class Adjudication:
    case_id: str
    decision: str
    primary_clause_id: str
    supporting_clause_ids: List[str]
    evidence_ids_used: List[str]
    rationale: str
    resolution_type: str
    refund_amount_inr: Optional[float]
    confidence: float
    model: str
    sla_version: str
    latency_seconds: float
    retrieved_clause_ids: List[str]
    warnings: List[str] = field(default_factory=list)
    raw_response: str = ""
    usage: Dict[str, int] = field(default_factory=dict)
    # Added in the Phase 2-4 build-out. Defaults keep older run files loadable.
    engine: str = "llm"                    # llm | rules | hybrid
    prompt_style: str = ""                 # zero_shot | facts | cot (LLM engines only)
    trace: List[Dict[str, str]] = field(default_factory=list)
    facts: Dict[str, Any] = field(default_factory=dict)
    cross_check: Dict[str, Any] = field(default_factory=dict)
    safeguard: Dict[str, Any] = field(default_factory=dict)  # set when a safeguard overrode the model

    def to_dict(self) -> Dict[str, Any]:
        data = self.__dict__.copy()
        data.pop("raw_response", None)
        return data

    @property
    def cited_clause_ids(self) -> List[str]:
        cited = [self.primary_clause_id] if self.primary_clause_id else []
        return cited + [c for c in self.supporting_clause_ids if c and c not in cited]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Adjudication":
        known = {name for name in cls.__dataclass_fields__}
        return cls(**{key: value for key, value in data.items() if key in known})
