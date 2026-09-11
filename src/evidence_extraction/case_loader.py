"""Case and evidence access.

Phase 1: cases arrive pre-structured in `data/raw/pilot/pilot_cases.json`.
Phase 2 replaces the source of these dictionaries with evidence extracted from
raw chat, email and log documents. Everything downstream consumes the shapes
returned here — `evidence_items()` in particular — so that swap does not reach
past this module.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config.paths import (
    PILOT_CASES_FILE,
    PILOT_GROUND_TRUTH_FILE,
    ROOT,
    SLA_FILE,
)

# Re-exported for callers that still refer to these by their old names.
CASES_FILE = PILOT_CASES_FILE
GROUND_TRUTH_FILE = PILOT_GROUND_TRUTH_FILE

EVIDENCE_SECTIONS = ("customer_evidence", "agent_evidence", "delivery_evidence")

__all__ = [
    "ROOT",
    "SLA_FILE",
    "CASES_FILE",
    "GROUND_TRUTH_FILE",
    "EVIDENCE_SECTIONS",
    "load_cases",
    "case_ids",
    "get_case",
    "evidence_items",
    "evidence_ids",
    "find_evidence",
    "load_ground_truth",
    "get_ground_truth",
]


def _load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_cases() -> List[Dict[str, Any]]:
    return _load(CASES_FILE)


def case_ids() -> List[str]:
    return [case["case_id"] for case in load_cases()]


def get_case(case_id: str) -> Dict[str, Any]:
    for case in load_cases():
        if case["case_id"] == case_id:
            return case
    raise KeyError(f"Unknown case_id: {case_id}")


def evidence_items(case: Dict[str, Any]) -> List[Dict[str, Any]]:
    """All evidence items across the three sections, each tagged with its section."""
    items = []
    for section in EVIDENCE_SECTIONS:
        for item in case.get(section, []):
            tagged = dict(item)
            tagged["_section"] = section
            items.append(tagged)
    return items


def evidence_ids(case: Dict[str, Any]) -> List[str]:
    return [item["evidence_id"] for item in evidence_items(case) if item.get("evidence_id")]


def find_evidence(case: Dict[str, Any], evidence_id: str) -> Optional[Dict[str, Any]]:
    for item in evidence_items(case):
        if item.get("evidence_id") == evidence_id:
            return item
    return None


# ---------------------------------------------------------------------------
# Ground truth — never passed to the model. Used by the evaluation layer and
# the evaluation view, after inference only.
# ---------------------------------------------------------------------------

def load_ground_truth() -> List[Dict[str, Any]]:
    return _load(GROUND_TRUTH_FILE)


def get_ground_truth(case_id: str) -> Optional[Dict[str, Any]]:
    for label in load_ground_truth():
        if label["case_id"] == case_id:
            return label
    return None
