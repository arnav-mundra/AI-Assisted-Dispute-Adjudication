"""Render dispute cases as plain Markdown, one file per case, for human annotators.

    python -m src.validation.case_views
        -> data/labeled/heldout/case_views/HO-001.md ... (from data/raw/heldout/heldout_cases.json)

    python -m src.validation.case_views --cases <file.json> --out <dir>

The view is a faithful re-layout of the case file: every field is shown, nothing is
summarised, interpreted or computed (no "hours since delivery", no clause hints), and
no label, design-intent or engine output is read. Customer text is shown verbatim,
including typos, Hinglish and any adversarial instructions it contains.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.config.paths import HELDOUT_CASES_FILE, HELDOUT_CASE_VIEWS_DIR

SECTIONS = (
    ("customer_evidence", "Customer evidence"),
    ("agent_evidence", "Delivery-agent evidence"),
    ("delivery_evidence", "Delivery and payment records"),
)
TYPE_NAMES = {
    "CHAT_MESSAGE": "Chat / email message",
    "PHOTO": "Photo or video",
    "AGENT_STATEMENT": "Delivery-agent statement",
    "POD": "Proof of delivery (PoD)",
    "DELIVERY_LOG": "Delivery-partner record",
    "RECONCILIATION_LOG": "Cash reconciliation log",
}
DISPUTE_NAMES = {"DAMAGED_GOODS": "Damaged goods", "COD_MISMATCH": "COD amount mismatch"}
ORDER_FIELDS = (
    ("order_id", "Order ID"),
    ("order_value_inr", "Order value (₹)"),
    ("order_total_cod_inr", "COD amount on invoice (₹)"),
    ("payment_mode", "Payment mode"),
    ("product_category", "Product category"),
    ("product_name", "Product"),
    ("city", "City"),
)
FIELD_NAMES = {
    "otp_confirmed": "OTP confirmed",
    "gps": "GPS",
    "pickup_timestamp_ist": "Pickup time",
    "amount_collected_inr": "Amount collected (₹)",
    "status": "Log status",
    "media_kind": "Media",
}
SHOWN_SEPARATELY = {"evidence_id", "type", "timestamp_ist", "text", "photo_description"}
# Escape only what would change how the text renders, so the raw .md stays readable too.
_MD_SPECIAL = re.compile(r"([\\`*<|])")
_LINE_START = re.compile(r"^(\s*)([#>+-])")


def _escape(text: str) -> str:
    return _LINE_START.sub(r"\1\\\2", _MD_SPECIAL.sub(r"\\\1", text))


def _when(stamp: str) -> str:
    try:
        return datetime.fromisoformat(stamp).strftime("%Y-%m-%d %H:%M IST")
    except ValueError:
        return stamp


def _value(key: str, value: Any) -> str:
    if value is None:
        return "— (none recorded)"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float) and key.endswith("_inr"):
        return f"{value:,.2f}"
    if isinstance(value, str) and key.endswith("timestamp_ist"):
        return _when(value)
    return _escape(str(value))


def _label(key: str) -> str:
    if key in FIELD_NAMES:
        return FIELD_NAMES[key]
    words = key.replace("_ist", "").replace("_inr", " (₹)").replace("_", " ")
    return words[:1].upper() + words[1:]


def _quote(text: str) -> List[str]:
    return [f"> {_escape(line)}" if line.strip() else ">" for line in text.split("\n")]


def _evidence(item: Dict[str, Any]) -> List[str]:
    kind = TYPE_NAMES.get(item.get("type", ""), item.get("type", ""))
    lines = [f"### {item['evidence_id']} · {kind} · {_when(item['timestamp_ist'])}"]
    fields = [f"- **{_label(key)}:** {_value(key, value)}"
              for key, value in item.items() if key not in SHOWN_SEPARATELY]
    if fields:
        lines += ["", *fields]
    if item.get("text"):
        lines += ["", "**Text:**", "", *_quote(item["text"])]
    if item.get("photo_description"):
        lines += ["", "**What the image shows:**", "", *_quote(item["photo_description"])]
    return lines + [""]


def render_case(case: Dict[str, Any]) -> str:
    dispute = DISPUTE_NAMES.get(case["dispute_type"], case["dispute_type"])
    lines = [f"# {case['case_id']} — {dispute}", "",
             f"SLA version: {case.get('sla_version', '—')} · Label this case using `docs/sla_policy.md` only.",
             "", "## Order", "", "| Field | Value |", "|---|---|"]
    order = case["order"]
    for key, name in ORDER_FIELDS:
        if key in order:
            lines.append(f"| {name} | {_value(key, order[key])} |")
    for key, value in order.items():
        if key not in dict(ORDER_FIELDS):
            lines.append(f"| {_label(key)} | {_value(key, value)} |")

    items = [(section, item) for section, _ in SECTIONS for item in case.get(section, [])]
    lines += ["", "## Timeline (all evidence, oldest first)", "",
              "| When (IST) | Evidence ID | Kind |", "|---|---|---|"]
    for _, item in sorted(items, key=lambda pair: pair[1]["timestamp_ist"]):
        lines.append(f"| {_when(item['timestamp_ist'])} | {item['evidence_id']} | "
                     f"{TYPE_NAMES.get(item['type'], item['type'])} |")

    for section, title in SECTIONS:
        lines += ["", f"## {title}", ""]
        section_items = case.get(section, [])
        if not section_items:
            lines.append("_None in this case._")
        for item in section_items:
            lines += _evidence(item)
    return "\n".join(lines).rstrip() + "\n"


def write_views(cases: List[Dict[str, Any]], out_dir: Path) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for case in cases:
        path = out_dir / f"{case['case_id']}.md"
        path.write_text(render_case(case), encoding="utf-8")
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Render cases as Markdown for annotators.")
    parser.add_argument("--cases", default=str(HELDOUT_CASES_FILE))
    parser.add_argument("--out", default=str(HELDOUT_CASE_VIEWS_DIR))
    args = parser.parse_args()
    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    paths = write_views(cases, Path(args.out))
    print(f"wrote {len(paths)} case views -> {args.out}")


if __name__ == "__main__":
    main()
