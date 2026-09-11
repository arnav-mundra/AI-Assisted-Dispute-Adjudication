"""A manually entered case must be indistinguishable in shape from a pilot case."""

import json

import pytest

from src.config.paths import CASE_SCHEMA_FILE
from src.evidence_extraction.case_loader import EVIDENCE_SECTIONS, evidence_ids, evidence_items
from src.evidence_extraction.manual_case import build_manual_case, is_manual_case
from src.reasoning_engine.adjudicator import build_case_view, build_user_prompt
from src.clause_matching.clause_retrieval import retrieve


def damaged_case(**overrides):
    kwargs = dict(
        dispute_type="DAMAGED_GOODS",
        customer_narrative="The box was crushed and the lamp base is cracked.",
        hours_since_pod=8.0,
        order_value_inr=2499.0,
        pod_shows_damage=True,
    )
    kwargs.update(overrides)
    return build_manual_case(**kwargs)


def cod_case(**overrides):
    kwargs = dict(
        dispute_type="COD_MISMATCH",
        customer_narrative="The agent collected 1700 but my invoice says 1500.",
        hours_since_pod=5.0,
        order_value_inr=1500.0,
        order_total_cod_inr=1500.0,
        claimed_amount_inr=1700.0,
        reconciliation_amount_inr=1700.0,
    )
    kwargs.update(overrides)
    return build_manual_case(**kwargs)


@pytest.mark.parametrize("case", [damaged_case(), cod_case()])
def test_manual_case_matches_the_case_schema(case):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(CASE_SCHEMA_FILE.read_text(encoding="utf-8"))
    errors = [e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(case)]
    assert not errors, errors


@pytest.mark.parametrize("case", [damaged_case(), cod_case()])
def test_manual_case_works_with_the_shared_pipeline_helpers(case):
    assert set(EVIDENCE_SECTIONS) <= set(case)
    assert evidence_ids(case), "no evidence IDs produced"
    assert all(item["evidence_id"].startswith("MANUAL-") for item in evidence_items(case))
    assert is_manual_case(case)

    # The same retrieval and prompt construction pilot cases use.
    retrieved = retrieve(case)
    assert retrieved
    prompt = build_user_prompt(case, retrieved)
    for evidence_id in evidence_ids(case):
        assert evidence_id in prompt


@pytest.mark.parametrize("case", [damaged_case(), cod_case()])
def test_manual_case_carries_no_ground_truth(case):
    assert "ground_truth" not in case
    assert "ground_truth" not in build_case_view(case)


def test_cod_case_without_a_reconciliation_log_records_its_absence():
    case = cod_case(reconciliation_available=False, reconciliation_amount_inr=None)
    logs = [i for i in evidence_items(case) if i["type"] == "RECONCILIATION_LOG"]
    assert len(logs) == 1
    assert logs[0]["status"] == "UNAVAILABLE"
    assert logs[0]["amount_collected_inr"] is None


def test_reporting_window_is_derived_from_timestamps_not_stated():
    case = damaged_case(hours_since_pod=71.5)
    prompt = build_user_prompt(case, retrieve(case))
    assert "71.5" not in prompt, "the elapsed interval must not be handed to the model"


def test_empty_narrative_is_rejected():
    with pytest.raises(ValueError):
        damaged_case(customer_narrative="   ")
