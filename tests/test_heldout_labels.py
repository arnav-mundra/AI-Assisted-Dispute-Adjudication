"""Held-out labelling workflow on throwaway fixture labels in a temp dir.

The labels written here are arbitrary test fixtures, not judgements about the cases;
they never touch data/labeled/heldout/.
"""

import csv
import json

import pytest

from src.config.paths import HELDOUT_CASES_FILE
from src.validation.heldout_labels import (
    ADJUDICATION_COLUMNS,
    ANNOTATOR_COLUMNS,
    adjudication_path,
    build_ground_truth,
    check_labels,
    compare_sheets,
    read_sheet,
    sheet_path,
    write_adjudication_sheet,
    write_blank_sheets,
)

REQUIRED_GT_FIELDS = ("case_id", "decision", "governing_clause_ids", "decisive_evidence_ids",
                      "contradictory_evidence_ids", "missing_evidence_ids", "rationale",
                      "sub_decisions", "labeler_id", "label_timestamp", "policy_version")
STAMP = "2026-11-01T10:00:00+05:30"


@pytest.fixture(scope="module")
def cases():
    return json.loads(HELDOUT_CASES_FILE.read_text(encoding="utf-8"))[:4]


def _fill(path, cases, decisions, clause="SLA-PRI-01"):
    rows = []
    for case, decision in zip(cases, decisions):
        pod = next(i for i in case["delivery_evidence"] if i["type"] == "POD")
        rows.append({"case_id": case["case_id"], "decision": decision, "governing_clause_ids": clause,
                     "decisive_evidence_ids": pod["evidence_id"], "resolution_type": "MANUAL_REVIEW",
                     "refund_amount_inr": "", "notes": f"fixture {decision.lower()}"})
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=ANNOTATOR_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def test_blank_sheets_are_blind_and_never_clobber_labels(tmp_path, cases):
    paths = write_blank_sheets(cases, tmp_path)
    for path in paths:
        rows = list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
        assert tuple(rows[0]) == ANNOTATOR_COLUMNS
        assert [r["case_id"] for r in rows] == [c["case_id"] for c in cases]
        assert all(not any(v for k, v in r.items() if k != "case_id") for r in rows)
    _fill(sheet_path("A", tmp_path), cases, ["ESCALATE"] * 4)
    with pytest.raises(FileExistsError):
        write_blank_sheets(cases, tmp_path)


def test_check_flags_bad_ids_and_values(tmp_path, cases):
    path = tmp_path / "a.csv"
    _fill(path, cases, ["ESCALATE", "MAYBE", "REJECT", "APPROVE"], clause="SLA-DG-07(b)")
    labels = read_sheet(path)
    assert labels[cases[0]["case_id"]]["governing_clause_ids"] == ["SLA-DG-07"]
    labels[cases[2]["case_id"]]["decisive_evidence_ids"] = ["POD-999"]
    labels[cases[3]["case_id"]]["governing_clause_ids"] = ["SLA-XX-99"]
    labels[cases[3]["case_id"]]["resolution_type"] = "REFUND"
    problems = "\n".join(check_labels(labels, cases))
    assert "MAYBE" in problems and "POD-999" in problems and "SLA-XX-99" in problems
    assert "needs a refund_amount_inr" in problems
    assert cases[0]["case_id"] + ":" not in problems


def test_compare_kappa_and_adjudication_flow(tmp_path, cases):
    _fill(sheet_path("A", tmp_path), cases, ["APPROVE", "REJECT", "ESCALATE", "APPROVE"])
    _fill(sheet_path("B", tmp_path), cases, ["APPROVE", "REJECT", "ESCALATE", "REJECT"])
    a, b = read_sheet(sheet_path("A", tmp_path)), read_sheet(sheet_path("B", tmp_path))

    result = compare_sheets(a, b)
    assert result["n"] == 4 and result["raw_agreement"] == 0.75
    assert 0 < result["kappa"] < 1 and result["clause_jaccard"] == 1.0
    flagged = [r["case_id"] for r in result["rows"] if r["issues"]]
    assert flagged == [cases[3]["case_id"]]

    path = adjudication_path(tmp_path)
    assert write_adjudication_sheet(result, path) == 1
    with pytest.raises(ValueError, match=cases[3]["case_id"]):
        build_ground_truth(cases, a, b, {}, STAMP)

    rows = list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
    rows[0].update(final_decision="ESCALATE", final_governing_clause_ids="SLA-PRI-01",
                   final_resolution_type="MANUAL_REVIEW", adjudicator_id="ADJUDICATOR-C",
                   adjudicator_notes="fixture")
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=ADJUDICATION_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    write_adjudication_sheet(result, path)  # re-running compare keeps the resolution
    kept = list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
    assert kept[0]["final_decision"] == "ESCALATE"

    labels = build_ground_truth(cases, a, b, {r["case_id"]: r for r in kept}, STAMP)
    assert [l["case_id"] for l in labels] == [c["case_id"] for c in cases]
    for label in labels:
        assert all(field in label for field in REQUIRED_GT_FIELDS)
        assert label["label_timestamp"] == STAMP
    assert labels[0]["labeler_id"] == "ANNOTATOR-A+ANNOTATOR-B"
    assert labels[0]["annotation"]["outcome"] == "AGREED"
    last = labels[3]
    assert last["decision"] == "ESCALATE" and last["labeler_id"] == "ADJUDICATOR-C"
    assert last["annotation"]["outcome"] == "ADJUDICATED"
    assert last["annotation"]["ANNOTATOR-A"]["decision"] == "APPROVE"
    assert last["annotation"]["ANNOTATOR-B"]["decision"] == "REJECT"
    assert "Adjudicator: fixture" in last["rationale"]


def test_blank_and_zero_refunds_agree(tmp_path, cases):
    _fill(sheet_path("A", tmp_path), cases, ["REJECT"] * 4)
    _fill(sheet_path("B", tmp_path), cases, ["REJECT"] * 4)
    a, b = read_sheet(sheet_path("A", tmp_path)), read_sheet(sheet_path("B", tmp_path))
    b[cases[0]["case_id"]]["refund_amount_inr"] = 0.0
    assert not any(r["issues"] for r in compare_sheets(a, b)["rows"])
