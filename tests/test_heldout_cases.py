"""Integrity of the held-out set: schema, IDs, references, blindness of the labelling kit."""

import json
import re

import pytest

from src.config.paths import (
    CASE_SCHEMA_FILE,
    HELDOUT_CASE_VIEWS_DIR,
    HELDOUT_CASES_FILE,
    HELDOUT_GROUND_TRUTH_FILE,
    PILOT_CASES_FILE,
    ROOT,
)
from src.evaluation import datasets
from src.validation.case_views import render_case
from src.validation.heldout_labels import ANNOTATOR_COLUMNS, ANNOTATORS, check_labels, read_sheet, sheet_path
from src.validation.validate_pilot import collect_case_evidence_ids, extract_sla_clause_ids

INTENT_FILE = ROOT / "data" / "design_intent" / "heldout_intent.json"
MATRIX_FILE = ROOT / "docs" / "phase2" / "SCENARIO_MATRIX_V2.md"
LABEL_KEYS = {"decision", "governing_clause_ids", "decisive_evidence_ids", "rationale",
              "sub_decisions", "intended_decision", "expected_decision", "label"}


@pytest.fixture(scope="module")
def cases():
    return json.loads(HELDOUT_CASES_FILE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def by_id(cases):
    return {case["case_id"]: case for case in cases}


def test_held_out_set_has_34_cases_split_evenly(cases):
    assert [c["case_id"] for c in cases] == [f"HO-{n:03d}" for n in range(1, 35)]
    types = [c["dispute_type"] for c in cases]
    assert types.count("DAMAGED_GOODS") == 17 and types.count("COD_MISMATCH") == 17


def test_cases_conform_to_case_schema(cases):
    jsonschema = pytest.importorskip("jsonschema")
    validator = jsonschema.Draft202012Validator(json.loads(CASE_SCHEMA_FILE.read_text(encoding="utf-8")))
    failures = [f"{case['case_id']}: {'/'.join(map(str, e.absolute_path))}: {e.message}"
                for case in cases for e in validator.iter_errors(case)]
    assert not failures, "\n".join(failures)


def test_case_and_evidence_ids_are_unique(cases):
    assert len({c["case_id"] for c in cases}) == len(cases)
    seen, duplicates = {}, []
    for case in cases:
        for section in ("customer_evidence", "agent_evidence", "delivery_evidence"):
            for item in case[section]:
                if item["evidence_id"] in seen:
                    duplicates.append(f"{item['evidence_id']} in {seen[item['evidence_id']]} and {case['case_id']}")
                seen[item["evidence_id"]] = case["case_id"]
    assert not duplicates, "\n".join(duplicates)


def test_no_overlap_with_pilot_ids_or_orders(cases):
    pilot = json.loads(PILOT_CASES_FILE.read_text(encoding="utf-8"))
    pilot_evidence = set().union(*(collect_case_evidence_ids(c) for c in pilot))
    held_evidence = set().union(*(collect_case_evidence_ids(c) for c in cases))
    assert not pilot_evidence & held_evidence
    for key in ("order_id", "city", "product_name"):
        assert not {c["order"][key] for c in pilot} & {c["order"][key] for c in cases}, key


def test_order_ids_quoted_in_text_match_the_case(cases):
    for case in cases:
        for item in case["customer_evidence"]:
            for quoted in re.findall(r"ORD-\d{4}-\d{5}", item.get("text", "")):
                assert quoted == case["order"]["order_id"], (case["case_id"], quoted)


def test_case_file_carries_no_labels(cases):
    for case in cases:
        assert not LABEL_KEYS & set(case), case["case_id"]


def test_design_intent_covers_every_case_and_cites_real_clauses(cases):
    intent = json.loads(INTENT_FILE.read_text(encoding="utf-8"))
    assert "NOT GROUND TRUTH" in intent["_NOTE"]
    assert [c["case_id"] for c in intent["cases"]] == [c["case_id"] for c in cases]
    clause_ids = extract_sla_clause_ids()
    for entry in intent["cases"]:
        assert entry["intended_decision"] in {"APPROVE", "REJECT", "ESCALATE"}
        assert set(entry["intended_clauses"]) <= clause_ids, entry["case_id"]


def test_scenario_matrix_lists_every_case_without_decisions(cases):
    rows = [line for line in MATRIX_FILE.read_text(encoding="utf-8").splitlines()
            if re.match(r"^\| HO-\d{3} \|", line)]
    assert [r.split("|")[1].strip() for r in rows] == [c["case_id"] for c in cases]
    for row in rows:
        assert not re.search(r"\b(APPROVE|REJECT|ESCALATE)\b", row), row


def test_annotator_sheets_cover_every_case_and_reference_real_ids(by_id):
    clause_ids = extract_sla_clause_ids()
    for letter in ANNOTATORS:
        path = sheet_path(letter)
        header = path.read_text(encoding="utf-8-sig").splitlines()[0]
        assert tuple(header.split(",")) == ANNOTATOR_COLUMNS
        labels = read_sheet(path)
        assert list(labels) == list(by_id)
        filled = {cid: label for cid, label in labels.items() if label["decision"]}
        problems = check_labels(filled, [by_id[cid] for cid in filled], clause_ids)
        assert not problems, f"annotator_{letter}.csv:\n" + "\n".join(problems)


def test_ground_truth_references_exist_once_written(by_id):
    if not HELDOUT_GROUND_TRUTH_FILE.exists():
        pytest.skip("held-out labels not finalised yet")
    labels = json.loads(HELDOUT_GROUND_TRUTH_FILE.read_text(encoding="utf-8"))
    clause_ids = extract_sla_clause_ids()
    assert sorted(l["case_id"] for l in labels) == sorted(by_id)
    for label in labels:
        known = collect_case_evidence_ids(by_id[label["case_id"]])
        for field in ("decisive_evidence_ids", "contradictory_evidence_ids", "missing_evidence_ids"):
            assert set(label[field]) <= known, (label["case_id"], field)
        assert set(label["governing_clause_ids"]) <= clause_ids, label["case_id"]
        assert label["labeler_id"]
        assert label["annotation"]["outcome"] in {"AGREED", "ADJUDICATED"}


def test_case_views_are_current(cases):
    for case in cases:
        view = HELDOUT_CASE_VIEWS_DIR / f"{case['case_id']}.md"
        assert view.read_text(encoding="utf-8") == render_case(case), (
            f"{view.name} is stale: python -m src.validation.case_views")


def test_case_views_show_every_evidence_item_and_nothing_sealed(cases):
    for case in cases:
        view = (HELDOUT_CASE_VIEWS_DIR / f"{case['case_id']}.md").read_text(encoding="utf-8")
        for evidence_id in collect_case_evidence_ids(case):
            assert f"### {evidence_id} " in view
        assert "intended" not in view.lower() and "design intent" not in view.lower()


def test_heldout_dataset_is_gated_on_final_labels(monkeypatch, tmp_path):
    spec = dict(datasets.DATASETS["heldout"], labels=tmp_path / "missing.json")
    monkeypatch.setitem(datasets.DATASETS, "heldout", spec)
    assert "heldout" not in datasets.available_datasets()
    assert len(datasets.load_cases("heldout")) == 34
    with pytest.raises(FileNotFoundError):
        datasets.load_dataset("heldout")
