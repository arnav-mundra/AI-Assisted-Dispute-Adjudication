"""Clause retrieval: case evidence -> the SLA clauses worth putting in the prompt.

Four rankers, all case-agnostic (no case IDs, no labels):

* ``lexical`` — IDF-weighted token overlap with a dispute-family prior (Phase 1).
* ``bm25``    — Okapi BM25 over clause text, same family prior.
* ``dense``   — sentence-transformer cosine similarity. Optional: used only when
                ``sentence-transformers`` is installed and the model is available
                locally (see requirements-ml.txt); otherwise silently skipped.
* ``hybrid``  — reciprocal-rank fusion of the above, plus *fact-conditioned
                expansion*: facts read by the evidence extractor (e.g. "the
                reconciliation log is missing", "order ≥ ₹5,000") pull in the
                clauses whose trigger condition they satisfy.

Every method then adds the always-on priority rules, the eligibility gate for
the dispute type, and one hop of explicit clause cross-references. The
interface (`retrieve` -> List[RetrievedClause]) is what the reasoning engine
consumes, so rankers can change without touching the adjudicator.
"""

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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


# ---------------------------------------------------------------------------
# Rankers
# ---------------------------------------------------------------------------

METHODS = ("lexical", "bm25", "dense", "hybrid")
BM25_K1 = 1.4
BM25_B = 0.75
RRF_K = 20
DENSE_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def _family_adjust(clause: Clause, target_family: Optional[str], bonus: float, penalty: float) -> float:
    if target_family and clause.family in {"DG", "COD"}:
        return bonus if clause.family == target_family else -penalty
    return 0.0


def _rank_lexical(case: Dict[str, Any], clauses: Dict[str, Clause]) -> Dict[str, float]:
    frequencies = _document_frequencies(clauses)
    total_docs = len(clauses)
    query_tokens = set(tokenize(case_query_text(case)))
    target_family = FAMILY_FOR_DISPUTE.get(case.get("dispute_type", ""))

    scores: Dict[str, float] = {}
    for clause in clauses.values():
        clause_tokens = tokenize(clause.text)
        if not clause_tokens:
            continue
        overlap = query_tokens & set(clause_tokens)
        raw = sum(math.log(1 + total_docs / (1 + frequencies[token])) for token in overlap)
        score = raw / math.sqrt(len(set(clause_tokens)))
        score += _family_adjust(clause, target_family, FAMILY_MATCH_BONUS, FAMILY_MISMATCH_PENALTY)
        scores[clause.clause_id] = round(score, 4)
    return scores


def _rank_bm25(case: Dict[str, Any], clauses: Dict[str, Clause]) -> Dict[str, float]:
    docs = {cid: tokenize(c.text) for cid, c in clauses.items()}
    avg_len = sum(len(d) for d in docs.values()) / max(len(docs), 1)
    frequencies = _document_frequencies(clauses)
    n = len(docs)
    query = Counter(tokenize(case_query_text(case)))
    target_family = FAMILY_FOR_DISPUTE.get(case.get("dispute_type", ""))

    scores: Dict[str, float] = {}
    for cid, tokens in docs.items():
        if not tokens:
            continue
        tf = Counter(tokens)
        score = 0.0
        for term in query:
            if term not in tf:
                continue
            idf = math.log(1 + (n - frequencies[term] + 0.5) / (frequencies[term] + 0.5))
            freq = tf[term]
            score += idf * freq * (BM25_K1 + 1) / (freq + BM25_K1 * (1 - BM25_B + BM25_B * len(tokens) / avg_len))
        score += _family_adjust(clauses[cid], target_family, 2.0, 1.5)
        scores[cid] = round(score, 4)
    return scores


_DENSE: Dict[str, Any] = {}


def dense_available() -> bool:
    """True when sentence-transformers and its model can be loaded locally."""
    if "ok" not in _DENSE:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            _DENSE["model"] = SentenceTransformer(DENSE_MODEL_NAME)
            _DENSE["ok"] = True
        except Exception:  # noqa: BLE001 - optional dependency
            _DENSE["ok"] = False
    return bool(_DENSE["ok"])


def _rank_dense(case: Dict[str, Any], clauses: Dict[str, Clause]) -> Dict[str, float]:
    if not dense_available():
        return {}
    model = _DENSE["model"]
    ids = list(clauses)
    key = tuple(ids)
    if _DENSE.get("key") != key:
        _DENSE["key"] = key
        _DENSE["matrix"] = model.encode([clauses[c].text for c in ids], normalize_embeddings=True)
    query = model.encode([case_query_text(case)], normalize_embeddings=True)[0]
    sims = _DENSE["matrix"] @ query
    target_family = FAMILY_FOR_DISPUTE.get(case.get("dispute_type", ""))
    return {
        cid: round(float(sim) + _family_adjust(clauses[cid], target_family, 0.15, 0.1), 4)
        for cid, sim in zip(ids, sims)
    }


def fact_triggered_clauses(case: Dict[str, Any]) -> Dict[str, str]:
    """Clauses whose trigger condition is satisfied by an extracted fact."""
    from src.evidence_extraction.extractor import extract_facts

    f = extract_facts(case)
    hits: Dict[str, str] = {}

    def add(clause_id: str, why: str) -> None:
        hits.setdefault(clause_id, why)

    if case.get("dispute_type") == "DAMAGED_GOODS":
        pod = f.get("pod_condition")
        if pod == "DAMAGED":
            add("SLA-DG-06", "fact: PoD photo shows external damage")
            add("SLA-DG-02", "fact: PoD photo shows external damage")
        elif pod == "INTACT":
            add("SLA-DG-05", "fact: PoD photo shows package intact")
            add("SLA-DG-08", "fact: PoD intact — fault may be undeterminable")
        elif pod == "UNUSABLE":
            add("SLA-DG-08", "fact: PoD photo unusable")
        value = f.get("order_value_inr") or 0.0
        add("SLA-DG-03", f"fact: order value ₹{value:,.0f} "
                         f"{'≥' if f.get('high_value') else '<'} ₹5,000 evidence threshold")
        if f.get("unboxing_evidence") or f.get("damage_photo") or f.get("damage_description_specific"):
            add("SLA-DG-04", "fact: customer damage evidence on file")
        if (f.get("prior_claims_90d") or 0) > 0:
            add("SLA-DG-09", "fact: prior damaged-goods claims on account")
        if f.get("within_window"):
            add("SLA-DG-07", "fact: eligible claim — resolution options apply")
    elif case.get("dispute_type") == "COD_MISMATCH":
        direction = f.get("recon_vs_invoice")
        if direction == "NO_RECORD":
            add("SLA-COD-06", "fact: no reconciliation record")
        elif direction == "HIGHER":
            add("SLA-COD-04", "fact: reconciliation above invoice")
            add("SLA-COD-08", "fact: refund timeline applies")
        elif direction == "LOWER":
            add("SLA-COD-05", "fact: reconciliation below invoice")
        elif direction == "MATCH":
            add("SLA-COD-03", "fact: reconciliation matches invoice")
        if f.get("customer_corroboration"):
            add("SLA-COD-03", "fact: customer supplied corroborating evidence")
            add("SLA-COD-09", "fact: contested amount with corroboration on both sides")
        excess = f.get("claimed_excess_inr")
        if excess is not None and abs(excess) <= 10:
            add("SLA-COD-07", "fact: disputed amount ≤ ₹10")
    return hits


def rank(case: Dict[str, Any], method: str = "hybrid") -> Dict[str, float]:
    """Score every clause with one ranker. `hybrid` fuses the others by RRF."""
    clauses = load_clauses()
    if method == "lexical":
        return _rank_lexical(case, clauses)
    if method == "bm25":
        return _rank_bm25(case, clauses)
    if method == "dense":
        return _rank_dense(case, clauses)
    if method != "hybrid":
        raise ValueError(f"unknown retrieval method '{method}'; choose from {METHODS}")

    fused: Dict[str, float] = {}
    for scorer in (_rank_lexical, _rank_bm25, _rank_dense):
        scores = scorer(case, clauses)
        ordered = sorted(scores, key=lambda cid: scores[cid], reverse=True)
        for position, cid in enumerate(ordered):
            fused[cid] = fused.get(cid, 0.0) + 1.0 / (RRF_K + position + 1)
    return {cid: round(score, 4) for cid, score in fused.items()}


def retrieve(
    case: Dict[str, Any],
    top_k: int = 14,
    method: str = "hybrid",
    use_facts: Optional[bool] = None,
) -> List[RetrievedClause]:
    """Top-k clauses for the case, plus pinned rules, gates, fact triggers and cross-references."""
    clauses = load_clauses()
    scores = rank(case, method)
    if use_facts is None:
        use_facts = method == "hybrid"

    ordered = sorted(scores, key=lambda cid: scores[cid], reverse=True)
    reason = {"lexical": "lexical match", "bm25": "BM25 match", "dense": "semantic match",
              "hybrid": "hybrid rank (lexical + BM25" + (" + dense" if dense_available() else "") + ")"}[method]

    selected: Dict[str, RetrievedClause] = {
        cid: RetrievedClause(clause=clauses[cid], score=scores[cid], reason=reason)
        for cid in ordered[:top_k]
    }

    def ensure(clause_id: str, why: str, override: bool = True) -> None:
        if clause_id not in clauses:
            return
        if clause_id in selected:
            if override:
                selected[clause_id].reason = why
        else:
            selected[clause_id] = RetrievedClause(clause=clauses[clause_id],
                                                  score=scores.get(clause_id, 0.0), reason=why)

    for clause_id in sorted(ALWAYS_INCLUDE):
        ensure(clause_id, "always in context (adjudication rule)")
    for clause_id in sorted(ELIGIBILITY_GATES.get(case.get("dispute_type", ""), set())):
        ensure(clause_id, "always in context (eligibility gate)")
    if use_facts:
        for clause_id, why in fact_triggered_clauses(case).items():
            ensure(clause_id, why, override=False)

    # One-hop citation expansion: a clause another retrieved clause names by ID
    # must be readable, or the model reasons about a rule it cannot see.
    for item in list(selected.values()):
        for referenced in sorted(set(CLAUSE_REFERENCE.findall(item.clause.text))):
            if referenced != item.clause_id and referenced not in selected:
                ensure(referenced, f"cross-referenced by {item.clause_id}")

    return sorted(selected.values(), key=lambda item: (-item.score, item.clause_id))


def governing_recall(method: str, top_k: int, use_facts: Optional[bool] = None,
                     cases: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Share of reference governing clauses that reach the prompt. Evaluation only."""
    from src.evidence_extraction.case_loader import get_ground_truth, load_cases

    hit = total = 0
    sizes: List[int] = []
    misses: List[str] = []
    for case in cases or load_cases():
        label = get_ground_truth(case["case_id"])
        if not label:
            continue
        got = {item.clause_id for item in retrieve(case, top_k=top_k, method=method, use_facts=use_facts)}
        sizes.append(len(got))
        for clause_id in label["governing_clause_ids"]:
            total += 1
            if clause_id in got:
                hit += 1
            else:
                misses.append(f"{case['case_id']}:{clause_id}")
    return {
        "method": method, "top_k": top_k, "use_facts": bool(use_facts if use_facts is not None else method == "hybrid"),
        "recall": hit / total if total else 0.0, "hits": hit, "total": total,
        "mean_context_size": sum(sizes) / len(sizes) if sizes else 0.0, "misses": misses,
    }
