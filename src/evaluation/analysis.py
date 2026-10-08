"""Error analysis and run-to-run consistency over saved experiment runs (Phase 6-7).

    python -m src.evaluation.analysis                      # every saved run
    python -m src.evaluation.analysis --dataset counterfactual
    python -m src.evaluation.analysis --out results/error_analysis.md

Reads results/runs/*.json only - it makes no model calls. Labels are joined
here, after inference, exactly as in `metrics.score_run`.
"""

from __future__ import annotations

import argparse
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.config.paths import RESULTS_DIR
from src.evaluation.datasets import load_dataset
from src.evaluation.experiment import list_runs
from src.evaluation.metrics import score_run
from src.reasoning_engine import safeguards

ERROR_KINDS = {
    "missed_escalation": "Forced a decision where the reference escalates",
    "over_escalation": "Escalated where the reference decides",
    "polarity": "Approved where the reference rejects, or the reverse",
    "unparsed": "No valid decision returned",
}


def wilson_interval(successes: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """95% Wilson score interval - well behaved at the small n of this study."""
    if not n:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def error_kind(predicted: str, reference: str) -> Optional[str]:
    if predicted == reference:
        return None
    if predicted not in {"APPROVE", "REJECT", "ESCALATE"}:
        return "unparsed"
    if reference == "ESCALATE":
        return "missed_escalation"
    if predicted == "ESCALATE":
        return "over_escalation"
    return "polarity"


def config_key(run: Dict[str, Any]) -> Tuple[str, str, str, str, str]:
    config = run.get("config", {})
    safeguards_on = (["guard"] if config.get("guard") else []) + (
        [f"conf ≥ {config['min_confidence']:.2f}"] if config.get("min_confidence") else [])
    return (config.get("dataset", ""), config.get("engine", ""),
            config.get("model", ""), config.get("prompt_style", ""), " · ".join(safeguards_on))


def describe(key: Tuple[str, str, str, str, str]) -> str:
    dataset, engine, model, style, safeguards_on = key
    if engine == "rules":
        return f"{dataset} · rules engine"
    return f"{dataset} · {model.split('/')[-1]} · {style}" + (f" · {safeguards_on}" if safeguards_on else "")


def _unguarded(run: Dict[str, Any]) -> bool:
    config = run.get("config", {})
    return config.get("engine") == "llm" and not config.get("guard") and not config.get("min_confidence")


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

def collect_errors(runs: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """One row per wrong prediction, joined to its reference label."""
    labels_by_dataset: Dict[str, Dict[str, Dict[str, Any]]] = {}
    rows: List[Dict[str, Any]] = []

    for run in runs:
        dataset = run.get("config", {}).get("dataset", "")
        if dataset not in labels_by_dataset:
            _, labels = load_dataset(dataset)
            labels_by_dataset[dataset] = {l["case_id"]: l for l in labels}
        labels = labels_by_dataset[dataset]

        for pred in run.get("predictions", []):
            label = labels.get(pred["case_id"])
            if not label:
                continue
            kind = error_kind(pred.get("decision", "UNPARSED"), label["decision"])
            if not kind:
                continue
            cross = pred.get("cross_check") or {}
            rules_decision = cross.get("rules_decision")
            rows.append({
                "run_id": run.get("run_id", ""),
                "config": describe(config_key(run)),
                "case_id": pred["case_id"],
                "kind": kind,
                "predicted": pred.get("decision", "UNPARSED"),
                "reference": label["decision"],
                "primary_clause": pred.get("primary_clause_id", ""),
                "reference_clauses": label.get("governing_clause_ids", []),
                "missed_evidence": sorted(set(label.get("decisive_evidence_ids", []))
                                          - set(pred.get("evidence_ids_used") or [])),
                "confidence": float(pred.get("confidence") or 0.0),
                "rules_decision": rules_decision,
                "rules_correct": rules_decision == label["decision"] if rules_decision else None,
                "rationale": (pred.get("rationale") or "").strip(),
            })
    return rows


# ---------------------------------------------------------------------------
# Consistency
# ---------------------------------------------------------------------------

def consistency(runs: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Per configuration: how stable decisions are across repeated runs."""
    groups: Dict[Tuple[str, str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for run in runs:
        groups[config_key(run)].append(run)

    summaries = []
    for key, members in sorted(groups.items()):
        accuracies = [m["metrics"]["decision_accuracy"] for m in members if m.get("metrics", {}).get("n")]
        decisions: Dict[str, List[str]] = defaultdict(list)
        for member in members:
            for pred in member.get("predictions", []):
                decisions[pred["case_id"]].append(pred.get("decision", "UNPARSED"))

        unstable = {case: dict(Counter(votes)) for case, votes in decisions.items() if len(set(votes)) > 1}
        # Mean pairwise agreement of decisions per case, averaged over cases.
        pairwise = []
        for votes in decisions.values():
            if len(votes) < 2:
                continue
            pairs = [(a, b) for i, a in enumerate(votes) for b in votes[i + 1:]]
            pairwise.append(sum(a == b for a, b in pairs) / len(pairs))

        n_cases = members[0].get("metrics", {}).get("n", 0) if members else 0
        correct_total = sum(round(a * n_cases) for a in accuracies)
        mean = sum(accuracies) / len(accuracies) if accuracies else 0.0
        spread = (math.sqrt(sum((a - mean) ** 2 for a in accuracies) / (len(accuracies) - 1))
                  if len(accuracies) > 1 else 0.0)
        summaries.append({
            "config": describe(key),
            "runs": len(members),
            "accuracy_mean": mean,
            "accuracy_sd": spread,
            "accuracy_ci": wilson_interval(correct_total, n_cases * len(accuracies)),
            "escalation_recall_mean": (sum(m["metrics"].get("escalation_recall", 0.0) for m in members)
                                       / len(members)),
            "pairwise_agreement": sum(pairwise) / len(pairwise) if pairwise else None,
            "unstable_cases": unstable,
        })
    return summaries


# ---------------------------------------------------------------------------
# Disagreement guard (simulated offline from the saved cross-check)
# ---------------------------------------------------------------------------

def guarded(prediction: Dict[str, Any], min_confidence: float = 0.0, guard: bool = True) -> Dict[str, Any]:
    """The saved LLM decision with the live safeguards applied (see reasoning_engine/safeguards.py)."""
    return safeguards.apply_to_dict(prediction, guard=guard, min_confidence=min_confidence)


def _effect(run: Dict[str, Any], guard: bool, min_confidence: float) -> Dict[str, Any]:
    _, labels = load_dataset(run["config"]["dataset"])
    before = score_run(run["predictions"], labels)
    after = score_run([guarded(p, min_confidence, guard) for p in run["predictions"]], labels)
    flips = [(b, a) for b, a in zip(before["per_case"], after["per_case"]) if b["predicted"] != a["predicted"]]
    return {
        "config": describe(config_key(run)),
        "run_id": run.get("run_id", ""),
        "n": before["n"],
        "accuracy_before": before.get("decision_accuracy", 0.0),
        "accuracy_after": after.get("decision_accuracy", 0.0),
        "escalation_recall_before": before.get("escalation_recall", 0.0),
        "escalation_recall_after": after.get("escalation_recall", 0.0),
        "escalated_by_guard": len(flips),
        "errors_fixed": sum(1 for b, a in flips if a["correct"]),
        "correct_sent_to_review": sum(1 for b, a in flips if b["correct"]),
    }


def guard_effect(runs: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Per unguarded LLM run: decision metrics before and after the disagreement guard."""
    return [_effect(run, guard=True, min_confidence=0.0) for run in runs if _unguarded(run)]


FLOORS = (0.5, 0.6, 0.7, 0.8, 0.9, 0.95)


def confidence_floor_sweep(runs: Sequence[Dict[str, Any]],
                           floors: Sequence[float] = FLOORS) -> List[Dict[str, Any]]:
    """Pooled over unguarded LLM runs: what each confidence floor alone would have done."""
    eligible = [run for run in runs if _unguarded(run)]
    rows = []
    for floor in floors:
        effects = [_effect(run, guard=False, min_confidence=floor) for run in eligible]
        n = sum(e["n"] for e in effects)
        if not n:
            continue
        rows.append({
            "floor": floor,
            "n": n,
            "accuracy_before": sum(e["accuracy_before"] * e["n"] for e in effects) / n,
            "accuracy_after": sum(e["accuracy_after"] * e["n"] for e in effects) / n,
            "escalated": sum(e["escalated_by_guard"] for e in effects),
            "errors_fixed": sum(e["errors_fixed"] for e in effects),
            "correct_sent_to_review": sum(e["correct_sent_to_review"] for e in effects),
        })
    return rows


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _pct(value: Optional[float]) -> str:
    return "—" if value is None else f"{value:.0%}"


def render_report(runs: Sequence[Dict[str, Any]]) -> str:
    errors = collect_errors(runs)
    stability = consistency(runs)
    lines = ["# Error analysis and consistency", "",
             f"Generated from {len(runs)} saved run(s) in `results/runs/`. "
             "Confidence intervals are 95% Wilson intervals over all predictions pooled per configuration.", ""]

    lines += ["## Accuracy and stability by configuration", "",
              "| Configuration | Runs | Accuracy (mean ± sd) | 95% CI | Escalation recall | Pairwise agreement |",
              "|---|---|---|---|---|---|"]
    for row in stability:
        low, high = row["accuracy_ci"]
        lines.append(f"| {row['config']} | {row['runs']} | {row['accuracy_mean']:.0%} ± {row['accuracy_sd']:.0%} "
                     f"| {low:.0%}–{high:.0%} | {_pct(row['escalation_recall_mean'])} "
                     f"| {_pct(row['pairwise_agreement'])} |")
    unstable = [(r["config"], r["unstable_cases"]) for r in stability if r["unstable_cases"]]
    if unstable:
        lines += ["", "Cases whose decision changed between repeats of the same configuration:", ""]
        for config, cases in unstable:
            for case_id, votes in sorted(cases.items()):
                lines.append(f"- **{config}** · {case_id}: "
                             + ", ".join(f"{d}×{n}" for d, n in sorted(votes.items())))

    guard = guard_effect(runs)
    if guard:
        lines += ["", "## Disagreement guard (simulated)", "",
                  "If the LLM and the rules engine disagree, escalate to manual review. Simulated from the "
                  "cross-check stored with every prediction — no new model calls. Caveat: the rules engine "
                  "was written with the pilot cases visible, so pilot rows are in-sample; counterfactual "
                  "rows are the fairer test.", "",
                  "| Configuration | n | Accuracy before → after | Escalation recall before → after "
                  "| Escalated by guard | Errors fixed | Correct decisions sent to review |",
                  "|---|---|---|---|---|---|---|"]
        for row in guard:
            lines.append(f"| {row['config']} | {row['n']} | {row['accuracy_before']:.0%} → {row['accuracy_after']:.0%} "
                         f"| {row['escalation_recall_before']:.0%} → {row['escalation_recall_after']:.0%} "
                         f"| {row['escalated_by_guard']} | {row['errors_fixed']} | {row['correct_sent_to_review']} |")

    sweep = confidence_floor_sweep(runs)
    if sweep:
        lines += ["", "## Confidence floor (simulated)", "",
                  "Escalate any LLM ruling whose own confidence is below the floor. Pooled over every "
                  "unguarded LLM run above. A floor only helps if the model is less confident when it is "
                  "wrong — compare the two right-hand columns.", "",
                  "| Floor | Predictions | Accuracy before → after | Escalated | Errors fixed "
                  "| Correct rulings sent to review |",
                  "|---|---|---|---|---|---|"]
        for row in sweep:
            lines.append(f"| {row['floor']:.2f} | {row['n']} | {row['accuracy_before']:.0%} → "
                         f"{row['accuracy_after']:.0%} | {row['escalated']} | {row['errors_fixed']} "
                         f"| {row['correct_sent_to_review']} |")

    lines += ["", "## Error taxonomy", ""]
    if not errors:
        lines.append("No wrong decisions in the selected runs.")
        return "\n".join(lines) + "\n"

    kinds = Counter(e["kind"] for e in errors)
    lines += ["| Error kind | Count | Share |", "|---|---|---|"]
    for kind, description in ERROR_KINDS.items():
        if kinds[kind]:
            lines.append(f"| {description} | {kinds[kind]} | {kinds[kind] / len(errors):.0%} |")

    guarded = [e for e in errors if e["rules_correct"] is not None]
    if guarded:
        caught = sum(1 for e in guarded if e["rules_correct"])
        lines += ["", f"The rules-engine cross-check reached the reference decision on **{caught} of "
                      f"{len(guarded)}** LLM errors — the share a disagreement flag would have routed to review."]

    by_case = Counter(e["case_id"] for e in errors)
    lines += ["", "Cases most often wrong: "
              + ", ".join(f"{case} ({n})" for case, n in by_case.most_common(6)), ""]

    lines += ["## Every error", "",
              "| Case | Configuration | Kind | Predicted → Reference | Cited primary | Reference clauses "
              "| Missed decisive evidence | Conf. | Rules engine |",
              "|---|---|---|---|---|---|---|---|---|"]
    for e in sorted(errors, key=lambda e: (e["case_id"], e["config"])):
        lines.append(f"| {e['case_id']} | {e['config']} | {e['kind'].replace('_', ' ')} "
                     f"| {e['predicted']} → {e['reference']} | {e['primary_clause'] or '—'} "
                     f"| {', '.join(e['reference_clauses'])} | {', '.join(e['missed_evidence']) or '—'} "
                     f"| {e['confidence']:.2f} | {e['rules_decision'] or '—'} |")

    lines += ["", "## Model rationales for the errors", ""]
    seen = set()
    for e in sorted(errors, key=lambda e: (e["case_id"], e["config"])):
        if (e["case_id"], e["config"]) in seen:
            continue
        seen.add((e["case_id"], e["config"]))
        lines += [f"**{e['case_id']} · {e['config']}** ({e['predicted']}, reference {e['reference']})", "",
                  f"> {e['rationale'] or '(empty)'}", ""]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Error analysis and consistency over saved runs.")
    parser.add_argument("--dataset", default=None, help="Only runs on this dataset.")
    parser.add_argument("--engine", choices=["llm", "rules"], default=None)
    parser.add_argument("--since", default=None, help="Only runs created at or after this ISO time.")
    parser.add_argument("--out", default=str(RESULTS_DIR / "error_analysis.md"))
    args = parser.parse_args()

    runs = list_runs(args.dataset)
    if args.engine:
        runs = [r for r in runs if r.get("config", {}).get("engine") == args.engine]
    if args.since:
        runs = [r for r in runs if r.get("created_at", "") >= args.since]

    report = render_report(runs)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"{len(runs)} run(s) analysed -> {out}")


if __name__ == "__main__":
    main()
