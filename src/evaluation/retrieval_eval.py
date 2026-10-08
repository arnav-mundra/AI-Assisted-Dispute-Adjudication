"""Compare clause retrievers against the reference governing clauses (Phase 3).

    python -m src.evaluation.retrieval_eval          # -> results/retrieval_comparison.md

Two views per retriever and k:

- ranker recall:   share of reference clauses in the method's own top-k ranking -
                   the quality of the ranker alone.
- context recall:  share that actually reaches the prompt after `retrieve` adds the
                   always-on rules, eligibility gates, fact-triggered clauses and
                   cross-references - what the model really sees, and how many
                   clauses it costs (a context of all 29 clauses scores 100%).

SLA-PRI-02 is procedural and excluded, as in `metrics.py`. No model calls.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Sequence

from src.clause_matching.clause_retrieval import METHODS, dense_available, rank, retrieve
from src.clause_matching.sla_clauses import load_clauses
from src.config.paths import RESULTS_DIR
from src.evaluation.datasets import load_dataset
from src.evaluation.metrics import PROCEDURAL_CLAUSES

KS = (4, 8, 12)
EXPERIMENT_SETTINGS = {"method": "hybrid", "top_k": 12}  # what experiment.py uses by default


def _gold(label: Dict[str, Any]) -> set:
    return set(label.get("governing_clause_ids", [])) - PROCEDURAL_CLAUSES


def evaluate(dataset: str, method: str, top_k: int) -> Dict[str, Any]:
    cases, labels = load_dataset(dataset)
    gold_by_id = {l["case_id"]: _gold(l) for l in labels}
    ranker_hits = context_hits = total = 0
    sizes: List[int] = []
    misses: Dict[str, List[str]] = {}
    for case in cases:
        gold = gold_by_id.get(case["case_id"], set())
        if not gold:
            continue
        scores = rank(case, method)
        top = set(sorted(scores, key=lambda cid: scores[cid], reverse=True)[:top_k])
        context = {item.clause_id for item in retrieve(case, top_k=top_k, method=method)}
        sizes.append(len(context))
        total += len(gold)
        ranker_hits += len(gold & top)
        context_hits += len(gold & context)
        missing = sorted(gold - context)
        if missing:
            misses[case["case_id"]] = missing
    return {
        "dataset": dataset, "method": method, "top_k": top_k, "references": total,
        "ranker_recall": ranker_hits / total if total else 0.0,
        "context_recall": context_hits / total if total else 0.0,
        "mean_context": sum(sizes) / len(sizes) if sizes else 0.0,
        "misses": misses,
    }


def case_check(dataset: str, case_ids: Sequence[str], method: str, top_k: int) -> List[Dict[str, Any]]:
    """For named cases: which reference clauses reached the prompt, and why each got there."""
    cases, labels = load_dataset(dataset)
    by_id = {c["case_id"]: c for c in cases}
    gold_by_id = {l["case_id"]: _gold(l) for l in labels}
    rows = []
    for case_id in case_ids:
        if case_id not in by_id:
            continue
        reasons = {item.clause_id: item.reason for item in retrieve(by_id[case_id], top_k=top_k, method=method)}
        for clause_id in sorted(gold_by_id.get(case_id, set())):
            rows.append({"case_id": case_id, "clause_id": clause_id, "retrieved": clause_id in reasons,
                         "reason": reasons.get(clause_id, "—")})
    return rows


def render(results: Sequence[Dict[str, Any]], checks: Sequence[Dict[str, Any]]) -> str:
    n_clauses = len(load_clauses())
    lines = ["# Clause retrieval comparison", "",
             f"Reference governing clauses (SLA-PRI-02 excluded) vs. what each retriever returns. "
             f"The SLA has {n_clauses} clauses. Dense embeddings "
             + ("were available." if dense_available() else "were **not** installed, so `dense` and the dense "
                "part of `hybrid` fall back.") + "", "",
             "**Ranker recall** is the method's own top-k. **Context recall** is what reaches the prompt after "
             "pinned rules, gates, fact triggers and cross-references are added; *mean context* is what that "
             "costs in clauses.", ""]
    for dataset in sorted({r["dataset"] for r in results}):
        lines += [f"## {dataset}", "",
                  "| Retriever | k | Ranker recall | Context recall | Mean context (clauses) |",
                  "|---|---|---|---|---|"]
        for r in [r for r in results if r["dataset"] == dataset]:
            lines.append(f"| {r['method']} | {r['top_k']} | {r['ranker_recall']:.0%} | {r['context_recall']:.0%} "
                         f"| {r['mean_context']:.1f} |")
        misses = [r for r in results if r["dataset"] == dataset and r["misses"]]
        if misses:
            lines += ["", "Reference clauses that never reached the prompt:", ""]
            for r in misses:
                lines.append(f"- {r['method']} k={r['top_k']}: "
                             + "; ".join(f"{cid} → {', '.join(c)}" for cid, c in sorted(r["misses"].items())))
        lines.append("")

    if checks:
        lines += [f"## Did the escalation cases see their clauses? "
                  f"({EXPERIMENT_SETTINGS['method']}, k={EXPERIMENT_SETTINGS['top_k']}, as in the experiments)", "",
                  "| Case | Reference clause | In the prompt | Why it was included |", "|---|---|---|---|"]
        for row in checks:
            lines.append(f"| {row['case_id']} | {row['clause_id']} | {'yes' if row['retrieved'] else '**no**'} "
                         f"| {row['reason']} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare clause retrievers on the labelled datasets.")
    parser.add_argument("--out", default=str(RESULTS_DIR / "retrieval_comparison.md"))
    args = parser.parse_args()

    methods = [m for m in METHODS if m != "dense" or dense_available()]
    results = [evaluate(dataset, method, k)
               for dataset in ("pilot", "counterfactual") for method in methods for k in KS]
    checks = case_check("pilot", ["DG-003", "DG-004", "COD-005"], **EXPERIMENT_SETTINGS)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(results, checks), encoding="utf-8")
    print(f"{len(results)} configurations -> {out}")


if __name__ == "__main__":
    main()
