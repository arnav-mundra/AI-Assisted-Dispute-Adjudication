"""Second-labeller workflow: blind template export and inter-annotator agreement.

    python -m src.validation.agreement export --dataset pilot
        -> data/labeled/<dataset>/second_labeler_template.csv  (blind: no first-labeller fields)

    python -m src.validation.agreement compare --dataset pilot --second <filled.csv>
        -> results/agreement_<dataset>.md  (Cohen's kappa, clause overlap, every disagreement)

Per GROUND_TRUTH_SCHEMA.md, disagreements are recorded, never averaged away, and
the frozen first-labeller file is not modified.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from src.config.paths import RESULTS_DIR, ROOT
from src.evaluation.datasets import DATASETS, load_dataset

DECISIONS = ("APPROVE", "REJECT", "ESCALATE")
PROCEDURAL_CLAUSES = frozenset({"SLA-PRI-02"})
TEMPLATE_COLUMNS = ("case_id", "dispute_type", "decision", "governing_clause_ids",
                    "decisive_evidence_ids", "rationale", "labeler_id")


def _split(value: str) -> List[str]:
    return [part.strip() for part in value.replace(",", ";").split(";") if part.strip()]


def template_path(dataset: str) -> Path:
    return ROOT / "data" / "labeled" / dataset / "second_labeler_template.csv"


def export_template(dataset: str, out: Path, cases_file: Optional[Path] = None) -> Path:
    """Blind template for a named dataset, or for any case file (e.g. unlabelled drafts)."""
    cases = json.loads(cases_file.read_text(encoding="utf-8")) if cases_file else load_dataset(dataset)[0]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as file:  # BOM so Excel reads ₹ correctly
        writer = csv.DictWriter(file, fieldnames=TEMPLATE_COLUMNS)
        writer.writeheader()
        for case in cases:
            writer.writerow({"case_id": case["case_id"], "dispute_type": case["dispute_type"]})
    return out


def load_second_labels(path: Path) -> List[Dict[str, Any]]:
    """A filled CSV template, or a JSON file in the ground-truth schema."""
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    labels = []
    for row in rows:
        decision = (row.get("decision") or "").strip().upper()
        if not decision:
            continue
        labels.append({
            "case_id": row["case_id"].strip(),
            "decision": decision,
            "governing_clause_ids": _split(row.get("governing_clause_ids") or ""),
            "decisive_evidence_ids": _split(row.get("decisive_evidence_ids") or ""),
            "rationale": (row.get("rationale") or "").strip(),
            "labeler_id": (row.get("labeler_id") or "").strip(),
        })
    return labels


def cohens_kappa(first: Sequence[str], second: Sequence[str]) -> float:
    n = len(first)
    if not n:
        return 0.0
    observed = sum(a == b for a, b in zip(first, second)) / n
    first_counts, second_counts = Counter(first), Counter(second)
    expected = sum(first_counts[c] * second_counts[c] for c in set(first) | set(second)) / (n * n)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


def kappa_band(kappa: float) -> str:
    """Landis & Koch (1977) descriptive bands."""
    for threshold, band in ((0.8, "almost perfect"), (0.6, "substantial"), (0.4, "moderate"),
                            (0.2, "fair"), (0.0, "slight")):
        if kappa > threshold:
            return band
    return "poor"


def _jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a | b else 1.0


def compare(first: Sequence[Dict[str, Any]], second: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    first_by_id = {l["case_id"]: l for l in first}
    rows = []
    invalid = []
    for label in second:
        if label["decision"] not in DECISIONS:
            invalid.append(label["case_id"])
            continue
        reference = first_by_id.get(label["case_id"])
        if not reference:
            continue
        clauses_a = set(reference.get("governing_clause_ids", [])) - PROCEDURAL_CLAUSES
        clauses_b = set(label.get("governing_clause_ids", [])) - PROCEDURAL_CLAUSES
        rows.append({
            "case_id": label["case_id"],
            "first": reference["decision"],
            "second": label["decision"],
            "agree": reference["decision"] == label["decision"],
            "clause_jaccard": _jaccard(clauses_a, clauses_b),
            "evidence_jaccard": _jaccard(set(reference.get("decisive_evidence_ids", [])),
                                         set(label.get("decisive_evidence_ids", []))),
            "first_clauses": sorted(clauses_a),
            "second_clauses": sorted(clauses_b),
            "second_rationale": label.get("rationale", ""),
        })
    n = len(rows)
    kappa = cohens_kappa([r["first"] for r in rows], [r["second"] for r in rows])
    return {
        "n": n,
        "unlabelled": sorted(set(first_by_id) - {r["case_id"] for r in rows} - set(invalid)),
        "invalid": invalid,
        "raw_agreement": sum(r["agree"] for r in rows) / n if n else 0.0,
        "kappa": kappa,
        "kappa_band": kappa_band(kappa),
        "clause_jaccard": sum(r["clause_jaccard"] for r in rows) / n if n else 0.0,
        "evidence_jaccard": sum(r["evidence_jaccard"] for r in rows) / n if n else 0.0,
        "rows": rows,
    }


def render(result: Dict[str, Any], dataset: str) -> str:
    lines = [f"# Inter-annotator agreement — {dataset}", "",
             f"- Cases compared: **{result['n']}**",
             f"- Raw decision agreement: **{result['raw_agreement']:.0%}**",
             f"- Cohen's κ (decision): **{result['kappa']:.2f}** ({result['kappa_band']}, Landis & Koch)",
             f"- Mean governing-clause overlap (Jaccard, SLA-PRI-02 excluded): {result['clause_jaccard']:.2f}",
             f"- Mean decisive-evidence overlap (Jaccard): {result['evidence_jaccard']:.2f}"]
    if result["unlabelled"]:
        lines.append(f"- Not yet labelled by the second labeller: {', '.join(result['unlabelled'])}")
    if result["invalid"]:
        lines.append(f"- Invalid decision values (ignored): {', '.join(result['invalid'])}")

    disagreements = [r for r in result["rows"] if not r["agree"]]
    lines += ["", "## Decision disagreements", ""]
    if not disagreements:
        lines.append("None.")
    else:
        lines += ["Recorded, not resolved. Adjudicate each one and log any label change as a "
                  "`revision_note` in the ground-truth file.", "",
                  "| Case | First labeller | Second labeller | First clauses | Second clauses | Second rationale |",
                  "|---|---|---|---|---|---|"]
        for r in disagreements:
            rationale = r["second_rationale"].replace("|", "/").replace("\n", " ")
            lines.append(f"| {r['case_id']} | {r['first']} | {r['second']} | {', '.join(r['first_clauses'])} "
                         f"| {', '.join(r['second_clauses'])} | {rationale} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Second-labeller template and agreement.")
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export", help="Write a blind labelling template.")
    export.add_argument("--dataset", choices=sorted(DATASETS), default="pilot")
    export.add_argument("--out", default=None)
    export.add_argument("--cases", default=None, help="Any case file instead of a named dataset.")
    comp = sub.add_parser("compare", help="Score a filled template against the frozen labels.")
    comp.add_argument("--dataset", choices=sorted(DATASETS), default="pilot")
    comp.add_argument("--second", required=True, help="Filled CSV template or ground-truth JSON.")
    comp.add_argument("--out", default=None)
    args = parser.parse_args()

    if args.command == "export":
        cases_file = Path(args.cases) if args.cases else None
        if cases_file and not args.out:
            parser.error("--cases needs --out")
        path = export_template(args.dataset, Path(args.out) if args.out else template_path(args.dataset), cases_file)
        print(f"blind template -> {path}")
        return

    _, first = load_dataset(args.dataset)
    result = compare(first, load_second_labels(Path(args.second)))
    out = Path(args.out) if args.out else RESULTS_DIR / f"agreement_{args.dataset}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(result, args.dataset), encoding="utf-8")
    print(f"kappa {result['kappa']:.2f} ({result['kappa_band']}), agreement {result['raw_agreement']:.0%} "
          f"over {result['n']} cases -> {out}")


if __name__ == "__main__":
    main()
