"""CLI runner for the vertical slice.

    python -m src.evaluation.run_adjudication --case DG-001
    python -m src.evaluation.run_adjudication --all --out runs/pilot_run.json

Ground truth is loaded only to print the comparison column, after inference.
"""

import argparse
import json
import time
from pathlib import Path
from typing import List

from src.reasoning_engine.adjudicator import Adjudication, adjudicate, default_model
from src.evidence_extraction.case_loader import ROOT, get_case, load_cases, get_ground_truth


def run_one(case_id: str, model: str, top_k: int) -> Adjudication:
    return adjudicate(get_case(case_id), model=model, top_k=top_k)


def print_result(result: Adjudication) -> None:
    label = get_ground_truth(result.case_id)
    reference = label["decision"] if label else "—"
    match = "MATCH" if label and label["decision"] == result.decision else "DIFFERS"

    print(f"\n=== {result.case_id} ===")
    print(f"decision        : {result.decision}   (reference: {reference} -> {match})")
    print(f"primary clause  : {result.primary_clause_id}")
    print(f"supporting      : {', '.join(result.supporting_clause_ids) or '—'}")
    print(f"evidence used   : {', '.join(result.evidence_ids_used) or '—'}")
    print(f"resolution      : {result.resolution_type}"
          + (f" (₹{result.refund_amount_inr:,.2f})" if result.refund_amount_inr is not None else ""))
    print(f"confidence      : {result.confidence:.2f}")
    print(f"latency         : {result.latency_seconds}s   tokens: {result.usage}")
    print(f"rationale       : {result.rationale}")
    if result.warnings:
        print(f"warnings        : {result.warnings}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Adjudicate pilot dispute cases.")
    parser.add_argument("--case", help="Case ID, e.g. DG-001")
    parser.add_argument("--all", action="store_true", help="Run all pilot cases")
    parser.add_argument("--model", default=default_model())
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--out", help="Write results to this JSON file")
    parser.add_argument(
        "--delay", type=float, default=5.0,
        help="Seconds to wait between cases in an --all run (provider throttling).",
    )
    args = parser.parse_args()

    if not args.case and not args.all:
        parser.error("pass --case CASE_ID or --all")

    case_ids: List[str] = (
        [case["case_id"] for case in load_cases()] if args.all else [args.case]
    )

    results: List[Adjudication] = []
    failures: List[str] = []

    for index, case_id in enumerate(case_ids):
        if index:
            time.sleep(args.delay)  # free-tier providers throttle rapid sequential calls
        try:
            result = run_one(case_id, args.model, args.top_k)
        except Exception as exc:  # one bad case must not lose the whole run
            failures.append(f"{case_id}: {exc}")
            print(f"\n=== {case_id} ===\nFAILED: {exc}")
            continue
        results.append(result)
        print_result(result)

    if args.all:
        agreed = sum(
            1
            for result in results
            if (label := get_ground_truth(result.case_id)) and label["decision"] == result.decision
        )
        print(f"\nAgreement with frozen reference labels: {agreed}/{len(results)}")
        if failures:
            print(f"Cases that failed to run ({len(failures)}): {failures}")

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps([result.to_dict() for result in results], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
