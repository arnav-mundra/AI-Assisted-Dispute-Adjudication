"""SLA-grounded adjudication of one dispute case.

The model decides. Nothing here maps a case_id to an outcome, and ground truth
is never loaded in this module - see the assertion in `build_case_view`.

Vendor specifics live in `src/llm`; this module only knows `LLMProvider`.
"""

import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from src.clause_matching.clause_retrieval import RetrievedClause, retrieve
from src.clause_matching.sla_clauses import load_clauses, sla_version
from src.config.paths import ENV_FILE
from src.evidence_extraction.case_loader import evidence_ids, evidence_items
from src.llm import (
    LLMProvider,
    ProviderResponse,
    ProviderUnavailable,
    available_models,
    provider_for_model,
)

load_dotenv(ENV_FILE)

DEFAULT_MODEL = os.getenv("ADJUDICATION_MODEL", "openai/gpt-oss-120b")
MAX_TOKENS = 3000

VALID_DECISIONS = {"APPROVE", "REJECT", "ESCALATE"}


def default_model() -> str:
    """The configured model if its provider is usable, else the first that is."""
    usable = available_models()
    if DEFAULT_MODEL in usable or not usable:
        return DEFAULT_MODEL
    return usable[0]


SYSTEM_PROMPT = """You are an SLA-grounded dispute adjudicator for a D2C e-commerce company \
operating in India. You resolve damaged-goods and COD-mismatch disputes.

Adjudicate strictly on the SLA clauses and the case evidence supplied in the user message.

Rules:
1. Use ONLY the clauses provided. Never cite a clause ID that is not in the supplied list.
2. Cite ONLY evidence IDs that appear in the case. Never invent an evidence ID.
3. All timestamps are IST (UTC+05:30). Reporting windows run from the Proof-of-Delivery
   timestamp to the FIRST customer message. Compute that interval yourself; it is not given.
4. Where a clause states a formula (for example a refund amount), apply the formula rather
   than the amount a party asserts.
5. Choose ESCALATE only when you can name the specific factual question the record cannot
   answer, or when a clause requires manual review. State that question in the rationale.
   Do not escalate merely because a party is unreachable or evidence is self-serving.
6. `primary_clause_id` is the single clause that determines the outcome - the one that, if
   struck from the SLA, would change your decision. `supporting_clause_ids` are the other
   clauses you actually relied on (eligibility windows, evidence sufficiency, priority
   rules). Do not cite SLA-PRI-02: it is a rule about citing, not a ground of decision.
7. `confidence` is your calibrated probability that a careful human adjudicator applying
   this SLA would reach the same decision. Use the full range; do not default to 0.9.

Respond with a single JSON object and nothing else - no prose, no code fences:

{
  "decision": "APPROVE" | "REJECT" | "ESCALATE",
  "primary_clause_id": "SLA-XX-NN",
  "supporting_clause_ids": ["SLA-XX-NN", ...],
  "evidence_ids_used": ["...", ...],
  "rationale": "3-6 sentences: the window computation, the governing clause, and why the evidence satisfies or fails it.",
  "resolution_type": "REPLACEMENT_DEFAULT" | "REFUND" | "PARTIAL_REFUND" | "NO_CUSTOMER_ACTION" | "NO_STANDARD_RESOLUTION" | "MANUAL_REVIEW",
  "refund_amount_inr": <number or null>,
  "confidence": <number between 0 and 1>
}"""


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

    def to_dict(self) -> Dict[str, Any]:
        data = self.__dict__.copy()
        data.pop("raw_response", None)
        return data


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def build_case_view(case: Dict[str, Any]) -> Dict[str, Any]:
    """The model's view of the case. Asserts the leakage rule rather than trusting it."""
    if "ground_truth" in case:
        raise ValueError(
            f"{case.get('case_id')}: ground_truth present in case passed to the model."
        )

    return {
        "case_id": case["case_id"],
        "dispute_type": case["dispute_type"],
        "order": case["order"],
        "evidence": [
            {key: value for key, value in item.items() if key != "_section"}
            | {"section": item["_section"]}
            for item in evidence_items(case)
        ],
        "sla_version": case["sla_version"],
    }


def build_user_prompt(case: Dict[str, Any], clauses: List[RetrievedClause]) -> str:
    clause_block = "\n\n".join(
        f"[{item.clause_id}]\n{item.clause.text}" for item in clauses
    )

    return f"""RETRIEVED SLA CLAUSES (SLA v{sla_version()}) - the only clauses you may cite:

{clause_block}

ALLOWED CLAUSE IDS: {", ".join(item.clause_id for item in clauses)}

--- DISPUTE CASE ---
{json.dumps(build_case_view(case), indent=2, ensure_ascii=False)}
--- END CASE ---

ALLOWED EVIDENCE IDS: {", ".join(evidence_ids(case))}

Adjudicate this case. Respond with the JSON object only."""


# ---------------------------------------------------------------------------
# Model call - vendor-agnostic
# ---------------------------------------------------------------------------

TRANSIENT_MARKERS = (
    "503", "overloaded", "unavailable", "high demand",
    "429", "rate limit", "timeout",
)


def _call_with_retry(
    provider: LLMProvider,
    model: str,
    messages: List[Dict[str, str]],
    attempts: int = 5,
) -> ProviderResponse:
    """Providers throttle and briefly 503. A live demo should ride that out."""
    last_error: Optional[Exception] = None

    for attempt in range(attempts):
        try:
            return provider.complete(
                system=SYSTEM_PROMPT,
                messages=messages,
                model=model,
                max_tokens=MAX_TOKENS,
                temperature=0.0,
            )
        except ProviderUnavailable:
            raise
        except Exception as exc:  # noqa: BLE001 - re-raised below if not transient
            message = str(exc).lower()
            if not any(marker in message for marker in TRANSIENT_MARKERS):
                raise
            last_error = exc
            if attempt < attempts - 1:
                time.sleep(min(2 ** attempt * 3, 30))

    raise RuntimeError(
        f"{provider.label} was unavailable after {attempts} attempts: {last_error}"
    )


# ---------------------------------------------------------------------------
# Response parsing and grounding validation
# ---------------------------------------------------------------------------

def extract_json(raw: str) -> Dict[str, Any]:
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def validate_payload(
    payload: Dict[str, Any],
    case: Dict[str, Any],
    allowed_clause_ids: List[str],
) -> List[str]:
    """Structural + grounding checks. Returns human-readable problems."""
    problems: List[str] = []

    known_clauses = set(load_clauses())
    case_evidence = set(evidence_ids(case))

    decision = payload.get("decision")
    if decision not in VALID_DECISIONS:
        problems.append(f"decision '{decision}' is not one of {sorted(VALID_DECISIONS)}")

    primary = payload.get("primary_clause_id")
    if not primary:
        problems.append("primary_clause_id is missing")
    elif primary not in known_clauses:
        problems.append(f"primary_clause_id '{primary}' does not exist in the SLA")
    elif primary not in allowed_clause_ids:
        problems.append(f"primary_clause_id '{primary}' was not among the retrieved clauses")

    supporting = payload.get("supporting_clause_ids") or []
    if not isinstance(supporting, list):
        problems.append("supporting_clause_ids must be a list")
        supporting = []
    for clause_id in supporting:
        if clause_id not in known_clauses:
            problems.append(f"supporting clause '{clause_id}' does not exist in the SLA")
    if primary in supporting:
        problems.append(f"'{primary}' is cited as both primary and supporting")

    used = payload.get("evidence_ids_used") or []
    if not isinstance(used, list):
        problems.append("evidence_ids_used must be a list")
        used = []
    for evidence_id in used:
        if evidence_id not in case_evidence:
            problems.append(f"evidence ID '{evidence_id}' does not exist in this case")
    if not used:
        problems.append("no evidence IDs cited (SLA-PRI-02 requires them)")

    if not payload.get("rationale"):
        problems.append("rationale is empty")

    confidence = payload.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
        problems.append(f"confidence '{confidence}' is not a number between 0 and 1")

    return problems


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def adjudicate(
    case: Dict[str, Any],
    model: str = DEFAULT_MODEL,
    top_k: int = 12,
    repair_attempts: int = 1,
) -> Adjudication:
    clauses = retrieve(case, top_k=top_k)
    allowed = [item.clause_id for item in clauses]

    provider = provider_for_model(model)
    messages: List[Dict[str, str]] = [
        {"role": "user", "content": build_user_prompt(case, clauses)}
    ]

    started = time.perf_counter()
    response = _call_with_retry(provider, model, messages)
    raw, usage = response.text, response.usage

    warnings: List[str] = []
    payload: Dict[str, Any] = {}

    for attempt in range(repair_attempts + 1):
        try:
            payload = extract_json(raw)
            problems = validate_payload(payload, case, allowed)
        except json.JSONDecodeError:
            payload = {}
            problems = ["response was not valid JSON"]

        if not problems or attempt == repair_attempts:
            warnings.extend(problems)
            break

        messages = messages + [
            {"role": "assistant", "content": raw},
            {
                "role": "user",
                "content": (
                    "Your response had these problems:\n- "
                    + "\n- ".join(problems)
                    + "\n\nReturn a corrected JSON object only, using only the allowed "
                    "clause IDs and evidence IDs listed earlier."
                ),
            },
        ]
        retry = _call_with_retry(provider, model, messages)
        raw = retry.text
        usage = {key: usage.get(key, 0) + value for key, value in retry.usage.items()}
        warnings.append(f"repaired after: {'; '.join(problems)}")

    latency = time.perf_counter() - started

    refund = payload.get("refund_amount_inr")
    confidence = payload.get("confidence")

    return Adjudication(
        case_id=case["case_id"],
        decision=str(payload.get("decision", "UNPARSED")),
        primary_clause_id=str(payload.get("primary_clause_id", "")),
        supporting_clause_ids=list(payload.get("supporting_clause_ids") or []),
        evidence_ids_used=list(payload.get("evidence_ids_used") or []),
        rationale=str(payload.get("rationale", "")),
        resolution_type=str(payload.get("resolution_type", "")),
        refund_amount_inr=float(refund) if isinstance(refund, (int, float)) else None,
        confidence=float(confidence) if isinstance(confidence, (int, float)) else 0.0,
        model=model,
        sla_version=sla_version(),
        latency_seconds=round(latency, 2),
        retrieved_clause_ids=allowed,
        warnings=warnings,
        raw_response=raw,
        usage=usage,
    )
