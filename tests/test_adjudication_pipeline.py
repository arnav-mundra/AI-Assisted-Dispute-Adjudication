"""Offline tests for the adjudication pipeline. No API calls are made."""

import pytest

from src.reasoning_engine.adjudicator import (
    build_case_view,
    build_user_prompt,
    extract_json,
    validate_payload,
)
from src.evidence_extraction.case_loader import evidence_ids, get_case, get_ground_truth, load_cases
from src.clause_matching.clause_retrieval import retrieve
from src.clause_matching.sla_clauses import load_clauses


def test_every_clause_in_the_sla_is_parsed():
    clauses = load_clauses()
    for clause_id in ["SLA-GEN-03", "SLA-DEF-01", "SLA-DG-06", "SLA-COD-06", "SLA-PRI-01"]:
        assert clause_id in clauses, f"{clause_id} not parsed"
    assert "approved" in clauses["SLA-DG-06"].text
    # The qualifying paragraph under SLA-DG-03 must stay attached to it.
    assert "does not waive" in clauses["SLA-DG-03"].text


def test_retrieval_prefers_the_matching_clause_family():
    dg_ids = [item.clause_id for item in retrieve(get_case("DG-001"))]
    cod_ids = [item.clause_id for item in retrieve(get_case("COD-001"))]

    assert sum(1 for cid in dg_ids if "-DG-" in cid) > sum(1 for cid in dg_ids if "-COD-" in cid)
    assert sum(1 for cid in cod_ids if "-COD-" in cid) > sum(1 for cid in cod_ids if "-DG-" in cid)


def test_retrieval_always_includes_the_priority_rules():
    for case in load_cases():
        retrieved = {item.clause_id for item in retrieve(case)}
        assert {"SLA-PRI-01", "SLA-PRI-03", "SLA-GEN-03"} <= retrieved, case["case_id"]


def test_retrieval_surfaces_the_governing_clause_for_every_case():
    """The reference primary clauses must at least be reachable by the retriever."""
    misses = []
    for case in load_cases():
        label = get_ground_truth(case["case_id"])
        retrieved = {item.clause_id for item in retrieve(case)}
        for clause_id in label["governing_clause_ids"]:
            if clause_id not in retrieved:
                misses.append(f"{case['case_id']}: {clause_id}")
    assert not misses, f"governing clauses not retrieved: {misses}"


def test_case_view_and_prompt_contain_no_ground_truth():
    for case in load_cases():
        view = build_case_view(case)
        assert "ground_truth" not in view

        prompt = build_user_prompt(case, retrieve(case))
        label = get_ground_truth(case["case_id"])

        assert "ground_truth" not in prompt
        assert label["rationale"][:60] not in prompt
        assert "decisive_evidence_ids" not in prompt


def test_build_case_view_rejects_a_leaking_case():
    case = dict(get_case("DG-001"))
    case["ground_truth"] = {"decision": "APPROVE"}
    with pytest.raises(ValueError):
        build_case_view(case)


def test_adjudication_view_never_touches_ground_truth():
    """The live demo page must not be able to leak the answer."""
    from src.config.paths import ROOT

    source = (ROOT / "app" / "ui" / "adjudication_page.py").read_text(encoding="utf-8")
    assert "ground_truth" not in source
    assert "get_ground_truth" not in source


def test_every_registered_provider_declares_its_configuration():
    from src.llm import provider_status

    rows = provider_status()
    assert {row["name"] for row in rows} >= {"anthropic", "groq"}
    for row in rows:
        assert row["env_var"], row["name"]
        assert row["models"], row["name"]


def test_extract_json_tolerates_code_fences_and_prose():
    assert extract_json('```json\n{"decision": "APPROVE"}\n```')["decision"] == "APPROVE"
    assert extract_json('Here you go:\n{"decision": "REJECT"}')["decision"] == "REJECT"


def test_validate_payload_catches_hallucinated_ids():
    case = get_case("DG-001")
    allowed = [item.clause_id for item in retrieve(case)]

    good = {
        "decision": "APPROVE",
        "primary_clause_id": "SLA-DG-06",
        "supporting_clause_ids": ["SLA-DG-01"],
        "evidence_ids_used": evidence_ids(case)[:2],
        "rationale": "x",
        "confidence": 0.8,
    }
    assert validate_payload(good, case, allowed) == []

    bad = dict(good)
    bad["primary_clause_id"] = "SLA-DG-99"
    bad["evidence_ids_used"] = ["CUSTOMER-999"]
    bad["decision"] = "MAYBE"
    bad["confidence"] = 4
    problems = validate_payload(bad, case, allowed)

    assert any("SLA-DG-99" in p for p in problems)
    assert any("CUSTOMER-999" in p for p in problems)
    assert any("MAYBE" in p for p in problems)
    assert any("confidence" in p for p in problems)
