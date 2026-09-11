"""Lexical clause retrieval: case text -> the SLA clauses worth putting in the prompt.

Deliberately simple and inspectable (TF-style overlap with an inverse-document
weight, plus a dispute-type family prior). Phase 3 replaces the scorer with
sentence-transformer embeddings + FAISS; the interface here is what the
reasoning engine consumes, so that swap does not touch the adjudicator.

Nothing here is case-specific: the same scoring runs for all ten pilot cases.
"""

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List

from src.evidence_extraction.case_loader import evidence_items
from src.clause_matching.sla_clauses import Clause, load_clauses

TOKEN = re.compile(r"[a-z][a-z0-9-]+")
CLAUSE_REFERENCE = re.compile(r"\bSLA-(?:GEN|DEF|DG|COD|PRI)-\d{2}\b")

STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "was", "were", "not", "any",
    "are", "from", "has", "have", "had", "its", "his", "her", "she", "him",
    "you", "your", "they", "them", "their", "but", "all", "can", "may", "must",
    "shall", "should", "would", "there", "then", "than", "when", "where",
    "which", "who", "whom", "into", "onto", "out", "over", "under", "per",
    "each", "one", "two", "did", "does", "done", "been", "being", "such",
    "only", "also", "same", "other", "within", "without", "because",
}

# Adjudication priority rules and timestamp normalization apply to every case,
# so they are always in context. This is a policy-level rule, not a per-case one.
ALWAYS_INCLUDE = {"SLA-PRI-01", "SLA-PRI-02", "SLA-PRI-03", "SLA-GEN-03"}

# Eligibility gates: every claim of a given type must be tested against its
# reporting window before anything else, whether or not the case narrative
# happens to use words that score well against the clause text. Also policy-level.
ELIGIBILITY_GATES = {
    "DAMAGED_GOODS": {"SLA-DG-01", "SLA-DG-02"},
    "COD_MISMATCH": {"SLA-COD-01"},
}

FAMILY_FOR_DISPUTE = {
    "DAMAGED_GOODS": "DG",
    "COD_MISMATCH": "COD",
}

FAMILY_MATCH_BONUS = 0.45
FAMILY_MISMATCH_PENALTY = 0.35


@dataclass
class RetrievedClause:
    clause: Clause
    score: float
    reason: str

    @property
    def clause_id(self) -> str:
        return self.clause.clause_id


def tokenize(text: str) -> List[str]:
    return [t for t in TOKEN.findall(text.lower()) if t not in STOPWORDS and len(t) > 2]


def case_query_text(case: Dict[str, Any]) -> str:
    """Everything the retriever is allowed to see: the case, never the label."""
    parts: List[str] = [case.get("dispute_type", "").replace("_", " ")]

    order = case.get("order", {})
    parts.append(" ".join(str(v) for v in order.values() if v is not None))

    for item in evidence_items(case):
        for field in ("type", "text", "photo_description", "note", "reliability_note", "status"):
            value = item.get(field)
            if value:
                parts.append(str(value))

    return " ".join(parts)


def _document_frequencies(clauses: Dict[str, Clause]) -> Counter:
    frequencies: Counter = Counter()
    for clause in clauses.values():
        for token in set(tokenize(clause.text)):
            frequencies[token] += 1
    return frequencies


def retrieve(case: Dict[str, Any], top_k: int = 14) -> List[RetrievedClause]:
    clauses = load_clauses()
    frequencies = _document_frequencies(clauses)
    total_docs = len(clauses)

    query_tokens = set(tokenize(case_query_text(case)))
    target_family = FAMILY_FOR_DISPUTE.get(case.get("dispute_type", ""))

    scored: List[RetrievedClause] = []

    for clause in clauses.values():
        clause_tokens = tokenize(clause.text)
        if not clause_tokens:
            continue

        overlap = query_tokens & set(clause_tokens)
        raw = sum(
            math.log(1 + total_docs / (1 + frequencies[token]))
            for token in overlap
        )
        score = raw / math.sqrt(len(set(clause_tokens)))

        if target_family and clause.family in {"DG", "COD"}:
            if clause.family == target_family:
                score += FAMILY_MATCH_BONUS
            else:
                score -= FAMILY_MISMATCH_PENALTY

        scored.append(RetrievedClause(clause=clause, score=round(score, 4), reason="lexical match"))

    scored.sort(key=lambda item: item.score, reverse=True)

    selected: Dict[str, RetrievedClause] = {}

    for item in scored[:top_k]:
        selected[item.clause_id] = item

    pinned = {clause_id: "always in context (adjudication rule)" for clause_id in ALWAYS_INCLUDE}
    for clause_id in ELIGIBILITY_GATES.get(case.get("dispute_type", ""), set()):
        pinned[clause_id] = "always in context (eligibility gate)"

    for clause_id, reason in sorted(pinned.items()):
        if clause_id not in clauses:
            continue
        if clause_id in selected:
            selected[clause_id].reason = reason
        else:
            selected[clause_id] = RetrievedClause(
                clause=clauses[clause_id], score=0.0, reason=reason
            )

    # One-hop citation expansion: clauses in this SLA qualify each other by ID
    # (SLA-COD-06 names SLA-COD-07; SLA-DG-01 names SLA-DG-02). A clause that a
    # retrieved clause depends on must be in context, or the model is reasoning
    # about a rule it cannot read.
    for item in list(selected.values()):
        for referenced in set(CLAUSE_REFERENCE.findall(item.clause.text)):
            if referenced == item.clause_id or referenced in selected:
                continue
            if referenced in clauses:
                selected[referenced] = RetrievedClause(
                    clause=clauses[referenced],
                    score=0.0,
                    reason=f"cross-referenced by {item.clause_id}",
                )

    return sorted(selected.values(), key=lambda item: (-item.score, item.clause_id))
