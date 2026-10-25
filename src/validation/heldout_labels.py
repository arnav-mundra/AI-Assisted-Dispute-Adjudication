"""Held-out labelling workflow: blind sheets, agreement, adjudication, final labels.

    python -m src.validation.heldout_labels kit
        -> data/labeled/heldout/annotator_A.csv, annotator_B.csv (blank) + case_views/*.md
    python -m src.validation.heldout_labels check --sheet data/labeled/heldout/annotator_A.csv
        -> lists invalid decisions, clause IDs, evidence IDs, resolution types, refunds
    python -m src.validation.heldout_labels compare
        -> data/labeled/heldout/agreement_report.md   (Cohen's kappa, clause agreement)
        -> data/labeled/heldout/adjudication.csv      (every disagreement, for a third person)
    python -m src.validation.heldout_labels finalize
        -> data/labeled/heldout/heldout_ground_truth.json  (GROUND_TRUTH_SCHEMA format)

Labels come only from the two annotator sheets and the third person's adjudication
sheet. Nothing here reads the design-intent file, runs the rules engine or calls a
model. Per GROUND_TRUTH_SCHEMA.md, each final label records both annotators' original
answers and how it was reached, so disagreement is kept rather than averaged away.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from src.config.paths import (
    HELDOUT_CASE_VIEWS_DIR,
    HELDOUT_CASES_FILE,
    HELDOUT_GROUND_TRUTH_FILE,
    HELDOUT_LABEL_DIR,
)
from src.reasoning_engine.result import RESOLUTION_TYPES
from src.validation.agreement import DECISIONS, PROCEDURAL_CLAUSES, _clause, _jaccard, _split, cohens_kappa, kappa_band
from src.validation.case_views import write_views
from src.validation.validate_pilot import collect_case_evidence_ids, extract_sla_clause_ids

ANNOTATOR_COLUMNS = ("case_id", "decision", "governing_clause_ids", "decisive_evidence_ids",
                     "resolution_type", "refund_amount_inr", "notes")
ANNOTATORS = {"A": "ANNOTATOR-A", "B": "ANNOTATOR-B"}
ADJUDICATION_COLUMNS = (
    "case_id", "issues",
    "A_decision", "B_decision", "A_clauses", "B_clauses", "A_resolution", "B_resolution",
    "A_refund", "B_refund", "A_evidence", "B_evidence", "A_notes", "B_notes",
    "final_decision", "final_governing_clause_ids", "final_decisive_evidence_ids",
    "final_resolution_type", "final_refund_amount_inr", "adjudicator_id", "adjudicator_notes",
)
IST = timezone(timedelta(hours=5, minutes=30))


def sheet_path(letter: str, label_dir: Path = HELDOUT_LABEL_DIR) -> Path:
    return label_dir / f"annotator_{letter}.csv"


def adjudication_path(label_dir: Path = HELDOUT_LABEL_DIR) -> Path:
    return label_dir / "adjudication.csv"


def load_cases(path: Path = HELDOUT_CASES_FILE) -> List[Dict[str, Any]]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _write_csv(path: Path, columns: Sequence[str], rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:  # BOM so Excel reads ₹ correctly
        writer = csv.DictWriter(file, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Blank sheets
# ---------------------------------------------------------------------------

def write_blank_sheets(cases: Sequence[Dict[str, Any]], label_dir: Path = HELDOUT_LABEL_DIR,
                       overwrite: bool = False) -> List[Path]:
    """One blank sheet per annotator. Never clobbers a sheet that already holds labels."""
    paths = []
    for letter in ANNOTATORS:
        path = sheet_path(letter, label_dir)
        if path.exists() and not overwrite and any(
                (row.get("decision") or "").strip() for row in _read_csv(path)):
            raise FileExistsError(f"{path} already contains labels; refusing to overwrite it")
        _write_csv(path, ANNOTATOR_COLUMNS, [{"case_id": case["case_id"]} for case in cases])
        paths.append(path)
    return paths


# ---------------------------------------------------------------------------
# Reading and checking a filled sheet
# ---------------------------------------------------------------------------

def _refund(value: str) -> Optional[float]:
    value = (value or "").strip().replace("₹", "").replace(",", "")
    return float(value) if value else None


def read_sheet(path: Path) -> Dict[str, Dict[str, Any]]:
    """Filled annotator sheet -> {case_id: normalised label}. Unparseable refunds stay as text."""
    labels = {}
    for row in _read_csv(path):
        refund_text = (row.get("refund_amount_inr") or "").strip()
        try:
            refund: Any = _refund(refund_text)
        except ValueError:
            refund = refund_text
        labels[row["case_id"].strip()] = {
            "case_id": row["case_id"].strip(),
            "decision": (row.get("decision") or "").strip().upper(),
            "governing_clause_ids": [_clause(c) for c in _split(row.get("governing_clause_ids") or "")],
            "decisive_evidence_ids": [e.upper() for e in _split(row.get("decisive_evidence_ids") or "")],
            "resolution_type": (row.get("resolution_type") or "").strip().upper(),
            "refund_amount_inr": refund,
            "notes": (row.get("notes") or "").strip(),
        }
    return labels


def check_labels(labels: Dict[str, Dict[str, Any]], cases: Sequence[Dict[str, Any]],
                 clause_ids: Optional[set] = None) -> List[str]:
    """Every problem that would make a sheet unusable, as readable lines (empty = OK)."""
    clause_ids = clause_ids if clause_ids is not None else extract_sla_clause_ids()
    by_id = {case["case_id"]: case for case in cases}
    problems = [f"{cid}: not a held-out case" for cid in labels if cid not in by_id]
    for cid, case in by_id.items():
        label = labels.get(cid)
        if label is None:
            problems.append(f"{cid}: row missing")
            continue
        if label["decision"] not in DECISIONS:
            problems.append(f"{cid}: decision '{label['decision'] or '(blank)'}' is not one of {', '.join(DECISIONS)}")
        if not label["governing_clause_ids"]:
            problems.append(f"{cid}: no governing_clause_ids")
        for clause in label["governing_clause_ids"]:
            if clause not in clause_ids:
                problems.append(f"{cid}: clause '{clause}' does not exist in docs/sla_policy.md")
        known = collect_case_evidence_ids(case)
        if not label["decisive_evidence_ids"]:
            problems.append(f"{cid}: no decisive_evidence_ids")
        for evidence_id in label["decisive_evidence_ids"]:
            if evidence_id not in known:
                problems.append(f"{cid}: evidence '{evidence_id}' is not in this case")
        if label["resolution_type"] not in RESOLUTION_TYPES:
            problems.append(f"{cid}: resolution_type '{label['resolution_type'] or '(blank)'}' "
                            f"is not one of {', '.join(RESOLUTION_TYPES)}")
        refund = label["refund_amount_inr"]
        if isinstance(refund, str):
            problems.append(f"{cid}: refund_amount_inr '{refund}' is not a number")
        elif refund is None and label["resolution_type"] in ("REFUND", "PARTIAL_REFUND"):
            problems.append(f"{cid}: {label['resolution_type']} needs a refund_amount_inr")
        elif refund is not None and refund < 0:
            problems.append(f"{cid}: refund_amount_inr is negative")
    return problems


# ---------------------------------------------------------------------------
# Agreement
# ---------------------------------------------------------------------------

def _clause_set(label: Dict[str, Any]) -> set:
    return set(label["governing_clause_ids"]) - PROCEDURAL_CLAUSES


def case_issues(a: Dict[str, Any], b: Dict[str, Any]) -> List[str]:
    """What a third person must settle for this case; empty when the annotators agree."""
    issues = []
    if a["decision"] != b["decision"]:
        issues.append("decision")
    if _clause_set(a) != _clause_set(b):
        issues.append("clauses")
    if a["resolution_type"] != b["resolution_type"]:
        issues.append("resolution")
    # Blank and 0 both mean "nothing refunded".
    if abs(float(a["refund_amount_inr"] or 0) - float(b["refund_amount_inr"] or 0)) > 0.005:
        issues.append("refund")
    return issues


def compare_sheets(a: Dict[str, Dict[str, Any]], b: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Kappa on decision plus clause, resolution and refund agreement over cases both labelled."""
    shared = [cid for cid in a if cid in b and a[cid]["decision"] in DECISIONS and b[cid]["decision"] in DECISIONS]
    rows = []
    for cid in shared:
        la, lb = a[cid], b[cid]
        rows.append({
            "case_id": cid, "a": la, "b": lb,
            "issues": case_issues(la, lb),
            "clause_jaccard": _jaccard(_clause_set(la), _clause_set(lb)),
            "evidence_jaccard": _jaccard(set(la["decisive_evidence_ids"]), set(lb["decisive_evidence_ids"])),
        })
    n = len(rows)
    kappa = cohens_kappa([r["a"]["decision"] for r in rows], [r["b"]["decision"] for r in rows])
    mean = lambda values: sum(values) / n if n else 0.0  # noqa: E731
    per_clause = {}
    for clause in sorted({c for r in rows for c in _clause_set(r["a"]) | _clause_set(r["b"])}):
        cited_a = [clause in _clause_set(r["a"]) for r in rows]
        cited_b = [clause in _clause_set(r["b"]) for r in rows]
        per_clause[clause] = {
            "a": sum(cited_a), "b": sum(cited_b), "both": sum(x and y for x, y in zip(cited_a, cited_b)),
            "kappa": cohens_kappa([str(x) for x in cited_a], [str(y) for y in cited_b]),
        }
    return {
        "n": n,
        "not_compared": sorted((set(a) | set(b)) - set(shared)),
        "raw_agreement": mean([r["a"]["decision"] == r["b"]["decision"] for r in rows]),
        "kappa": kappa,
        "kappa_band": kappa_band(kappa),
        "clause_jaccard": mean([r["clause_jaccard"] for r in rows]),
        "clause_exact": mean([_clause_set(r["a"]) == _clause_set(r["b"]) for r in rows]),
        "evidence_jaccard": mean([r["evidence_jaccard"] for r in rows]),
        "resolution_agreement": mean([r["a"]["resolution_type"] == r["b"]["resolution_type"] for r in rows]),
        "per_clause": per_clause,
        "rows": rows,
    }


def render_report(result: Dict[str, Any]) -> str:
    lines = ["# Held-out inter-annotator agreement", "",
             f"- Cases labelled by both annotators: **{result['n']}**",
             f"- Raw decision agreement: **{result['raw_agreement']:.0%}**",
             f"- Cohen's κ (decision): **{result['kappa']:.2f}** ({result['kappa_band']}, Landis & Koch)",
             f"- Governing clauses — mean Jaccard: {result['clause_jaccard']:.2f}; identical sets: "
             f"{result['clause_exact']:.0%} (SLA-PRI-02 excluded; sub-clause letters ignored)",
             f"- Decisive evidence — mean Jaccard: {result['evidence_jaccard']:.2f}",
             f"- Resolution type agreement: {result['resolution_agreement']:.0%}"]
    if result["not_compared"]:
        lines.append(f"- Not compared (missing or invalid decision on a sheet): {', '.join(result['not_compared'])}")

    lines += ["", "## Per-clause citation agreement", "",
              "| Clause | Cited by A | Cited by B | Both | κ |", "|---|---|---|---|---|"]
    for clause, stats in result["per_clause"].items():
        lines.append(f"| {clause} | {stats['a']} | {stats['b']} | {stats['both']} | {stats['kappa']:.2f} |")

    flagged = [r for r in result["rows"] if r["issues"]]
    lines += ["", "## Cases needing adjudication", ""]
    if not flagged:
        lines.append("None — every case agrees on decision, clauses, resolution and refund.")
    else:
        lines += ["Resolve each in `adjudication.csv` (third person, blind to model output and to the "
                  "design-intent file).", "",
                  "| Case | Issues | A | B | A clauses | B clauses |", "|---|---|---|---|---|---|"]
        for r in flagged:
            lines.append(f"| {r['case_id']} | {', '.join(r['issues'])} | {r['a']['decision']} | {r['b']['decision']} "
                         f"| {', '.join(sorted(_clause_set(r['a'])))} | {', '.join(sorted(_clause_set(r['b'])))} |")
    return "\n".join(lines) + "\n"


def _fmt_refund(value: Any) -> str:
    return "" if value is None else f"{value}"


def write_adjudication_sheet(result: Dict[str, Any], path: Path) -> int:
    """List every flagged case; keeps any resolution already typed into an existing sheet."""
    existing = {row["case_id"]: row for row in _read_csv(path)} if path.exists() else {}
    rows = []
    for r in result["rows"]:
        if not r["issues"]:
            continue
        a, b = r["a"], r["b"]
        row = {
            "case_id": r["case_id"], "issues": "; ".join(r["issues"]),
            "A_decision": a["decision"], "B_decision": b["decision"],
            "A_clauses": "; ".join(a["governing_clause_ids"]), "B_clauses": "; ".join(b["governing_clause_ids"]),
            "A_resolution": a["resolution_type"], "B_resolution": b["resolution_type"],
            "A_refund": _fmt_refund(a["refund_amount_inr"]), "B_refund": _fmt_refund(b["refund_amount_inr"]),
            "A_evidence": "; ".join(a["decisive_evidence_ids"]), "B_evidence": "; ".join(b["decisive_evidence_ids"]),
            "A_notes": a["notes"], "B_notes": b["notes"],
        }
        for column in ADJUDICATION_COLUMNS:
            if column.startswith("final_") or column.startswith("adjudicator_"):
                row[column] = existing.get(r["case_id"], {}).get(column, "")
        rows.append(row)
    _write_csv(path, ADJUDICATION_COLUMNS, rows)
    return len(rows)


# ---------------------------------------------------------------------------
# Final labels
# ---------------------------------------------------------------------------

def _union(*lists: Sequence[str]) -> List[str]:
    seen: List[str] = []
    for values in lists:
        seen += [v for v in values if v not in seen]
    return seen


def _rationale(a: Dict[str, Any], b: Dict[str, Any], adjudicator_note: str = "") -> str:
    parts = [f"Annotator A: {a['notes'] or '(no notes)'}", f"Annotator B: {b['notes'] or '(no notes)'}"]
    if adjudicator_note:
        parts.append(f"Adjudicator: {adjudicator_note}")
    return " | ".join(parts)


def _annotation_record(label: Dict[str, Any]) -> Dict[str, Any]:
    return {key: label[key] for key in ("decision", "governing_clause_ids", "decisive_evidence_ids",
                                         "resolution_type", "refund_amount_inr", "notes")}


def build_ground_truth(cases: Sequence[Dict[str, Any]], a: Dict[str, Dict[str, Any]],
                       b: Dict[str, Dict[str, Any]], adjudication: Dict[str, Dict[str, str]],
                       timestamp: str) -> List[Dict[str, Any]]:
    """Agreed cases pass through; every flagged case must carry a complete adjudication row."""
    labels, unresolved = [], []
    for case in cases:
        cid = case["case_id"]
        la, lb = a[cid], b[cid]
        issues = case_issues(la, lb)
        sub: Dict[str, Any]
        if not issues:
            decision, clauses = la["decision"], la["governing_clause_ids"]
            evidence = _union(la["decisive_evidence_ids"], lb["decisive_evidence_ids"])
            resolution, refund = la["resolution_type"], la["refund_amount_inr"]
            labeler_id, how, note = f"{ANNOTATORS['A']}+{ANNOTATORS['B']}", "AGREED", ""
        else:
            row = adjudication.get(cid, {})
            decision = (row.get("final_decision") or "").strip().upper()
            clauses = [_clause(c) for c in _split(row.get("final_governing_clause_ids") or "")]
            resolution = (row.get("final_resolution_type") or "").strip().upper()
            adjudicator = (row.get("adjudicator_id") or "").strip()
            evidence = [e.upper() for e in _split(row.get("final_decisive_evidence_ids") or "")] or _union(
                la["decisive_evidence_ids"], lb["decisive_evidence_ids"])
            refund_text = (row.get("final_refund_amount_inr") or "").strip()
            try:
                refund = _refund(refund_text)
            except ValueError:
                refund = refund_text  # check_labels reports it
            # The adjudicator's row is checked exactly like an annotator sheet.
            problems = check_labels({cid: {"decision": decision, "governing_clause_ids": clauses,
                                           "decisive_evidence_ids": evidence, "resolution_type": resolution,
                                           "refund_amount_inr": refund}}, [case])
            if problems or not adjudicator:
                unresolved.append("; ".join(problems) if problems else f"{cid}: no adjudicator_id")
                continue
            labeler_id, how, note = adjudicator, "ADJUDICATED", (row.get("adjudicator_notes") or "").strip()
        sub = {"resolution_type": resolution}
        if refund is not None:
            sub["refund_amount_inr"] = float(refund)
        labels.append({
            "case_id": cid,
            "decision": decision,
            "governing_clause_ids": clauses,
            "decisive_evidence_ids": evidence,
            "contradictory_evidence_ids": [],
            "missing_evidence_ids": [],
            "rationale": _rationale(la, lb, note),
            "sub_decisions": sub,
            "labeler_id": labeler_id,
            "label_timestamp": timestamp,
            "policy_version": case.get("sla_version", "0.1"),
            "annotation": {
                "outcome": how,
                "issues": issues,
                ANNOTATORS["A"]: _annotation_record(la),
                ANNOTATORS["B"]: _annotation_record(lb),
            },
        })
    if unresolved:
        raise ValueError("unresolved disagreements (fix these rows in adjudication.csv):\n  "
                         + "\n  ".join(unresolved))
    return labels


def _checked_sheets(cases: Sequence[Dict[str, Any]], label_dir: Path) -> Dict[str, Dict[str, Dict[str, Any]]]:
    sheets, problems = {}, []
    for letter in ANNOTATORS:
        labels = read_sheet(sheet_path(letter, label_dir))
        problems += [f"annotator_{letter}.csv  {p}" for p in check_labels(labels, cases)]
        sheets[letter] = labels
    if problems:
        raise SystemExit("fix these before comparing:\n  " + "\n  ".join(problems))
    return sheets


def main() -> None:
    parser = argparse.ArgumentParser(description="Held-out labelling workflow.")
    parser.add_argument("--label-dir", default=str(HELDOUT_LABEL_DIR))
    parser.add_argument("--cases", default=str(HELDOUT_CASES_FILE))
    sub = parser.add_subparsers(dest="command", required=True)
    kit = sub.add_parser("kit", help="Write blank annotator sheets and the Markdown case views.")
    kit.add_argument("--overwrite", action="store_true", help="Replace sheets even if they hold labels.")
    check = sub.add_parser("check", help="Validate one filled annotator sheet.")
    check.add_argument("--sheet", required=True)
    sub.add_parser("compare", help="Kappa + clause agreement; list disagreements for adjudication.")
    final = sub.add_parser("finalize", help="Write heldout_ground_truth.json from agreed + adjudicated labels.")
    final.add_argument("--out", default=str(HELDOUT_GROUND_TRUTH_FILE))
    final.add_argument("--overwrite", action="store_true",
                       help="Replace an existing ground-truth file (record why in a revision_note).")
    args = parser.parse_args()

    label_dir, cases = Path(args.label_dir), load_cases(Path(args.cases))

    if args.command == "kit":
        paths = write_blank_sheets(cases, label_dir, overwrite=args.overwrite)
        views = write_views(cases, label_dir / HELDOUT_CASE_VIEWS_DIR.name)
        print(f"blank sheets -> {', '.join(str(p) for p in paths)}; {len(views)} case views")
        return

    if args.command == "check":
        problems = check_labels(read_sheet(Path(args.sheet)), cases)
        print("\n".join(problems) if problems else f"{args.sheet}: OK ({len(cases)} cases)")
        raise SystemExit(1 if problems else 0)

    sheets = _checked_sheets(cases, label_dir)
    result = compare_sheets(sheets["A"], sheets["B"])

    if args.command == "compare":
        report = label_dir / "agreement_report.md"
        report.write_text(render_report(result), encoding="utf-8")
        flagged = write_adjudication_sheet(result, adjudication_path(label_dir))
        print(f"kappa {result['kappa']:.2f} ({result['kappa_band']}), agreement {result['raw_agreement']:.0%}, "
              f"clause Jaccard {result['clause_jaccard']:.2f} over {result['n']} cases; "
              f"{flagged} case(s) to adjudicate -> {adjudication_path(label_dir)}")
        return

    out = Path(args.out)
    if out.exists() and not args.overwrite:
        raise SystemExit(f"{out} exists; final labels are frozen. Use --overwrite only with a revision_note.")
    adjudication = ({row["case_id"]: row for row in _read_csv(adjudication_path(label_dir))}
                    if adjudication_path(label_dir).exists() else {})
    stamp = datetime.now(IST).replace(microsecond=0).isoformat()
    try:
        labels = build_ground_truth(cases, sheets["A"], sheets["B"], adjudication, stamp)
    except ValueError as exc:
        raise SystemExit(str(exc))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(labels, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    agreed = sum(l["annotation"]["outcome"] == "AGREED" for l in labels)
    print(f"wrote {len(labels)} labels ({agreed} agreed, {len(labels) - agreed} adjudicated) -> {out}")


if __name__ == "__main__":
    main()
