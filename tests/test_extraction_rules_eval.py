"""Offline tests for Phase 2 extraction, the rules engine, hybrid retrieval,
the LLM path (via a mock provider), and Phase 6 scoring. No network calls."""

import json

import pytest

from src.clause_matching.clause_retrieval import governing_recall, retrieve
from src.evaluation.datasets import load_dataset
from src.evaluation.metrics import PROCEDURAL_CLAUSES, baselines, score_case, score_run
from src.evidence_extraction.case_loader import get_case, get_ground_truth, load_cases
from src.evidence_extraction.extractor import claimed_amount, classify_package, extract_facts
from src.llm.provider import LLMProvider, ProviderResponse, register
from src.reasoning_engine import adjudicator
from src.reasoning_engine.adjudicator import adjudicate, build_user_prompt
from src.reasoning_engine.rules_engine import adjudicate_rules


# ---------------------------------------------------------------- extraction

@pytest.mark.parametrize("text,expected", [
    ("All visible edges and corners are square, tape seal unbroken, no dents, tears or staining.", "INTACT"),
    ("The top-right corner of the box is visibly crushed inward and one side flap is torn open.", "DAMAGED"),
    ("Opened carton with a dark wet stain across the base.", "DAMAGED"),
    ("Sealed brown carton held by the consignee. Box edges are undamaged.", "INTACT"),
])
def test_package_condition_handles_negation(text, expected):
    assert classify_package(text) == expected


@pytest.mark.parametrize("text,invoice,expected", [
    ("my invoice says 1500 rupees but the delivery agent took 1700 from me", 1500, 1700),
    ("The invoice is 1800 but I gave the agent two 1000-rupee notes and he returned nothing, "
     "so 2000 was taken. I want the 200 rupees difference back.", 1800, 2000),
    ("My invoice total is 2350 but the agent collected 2500 in cash. That is 150 rupees more.", 2350, 2500),
    ("I think it was more than the invoice of 2200.", 2200, None),
    ("Invoice was Rs. 1,500 but the delivery boy charged me ₹1,700 in cash", 1500, 1700),
    ("order ORD-2026-41004 — invoice 1500, agent took 1700", 1500, 1700),
])
def test_claimed_amount_extraction(text, invoice, expected):
    assert claimed_amount(text, invoice) == expected


def test_reporting_window_facts():
    late = extract_facts(get_case("DG-002"))
    assert late.get("within_window") is False and late.get("reporting_window_h") == 48
    damaged = extract_facts(get_case("DG-001"))
    assert damaged.get("pod_condition") == "DAMAGED" and damaged.get("reporting_window_h") == 168


def test_unusable_pod_with_corroboration():
    facts = extract_facts(get_case("DG-005"))
    assert facts.get("pod_condition") == "UNUSABLE"
    assert facts.get("independent_damage_corroboration") is True
    assert {"AGENT-005", "DELIVERY-005"} <= set(facts.facts["independent_damage_corroboration"].sources)


def test_every_fact_source_is_real_evidence():
    from src.evidence_extraction.case_loader import evidence_ids
    for case in load_cases():
        valid = set(evidence_ids(case))
        for fact in extract_facts(case).facts.values():
            assert set(fact.sources) <= valid, (case["case_id"], fact.key, fact.sources)


# --------------------------------------------------------------- rules engine

@pytest.mark.parametrize("dataset", ["pilot", "counterfactual"])
def test_rules_engine_matches_reference_decisions(dataset):
    cases, labels = load_dataset(dataset)
    by_id = {l["case_id"]: l for l in labels}
    for case in cases:
        result = adjudicate_rules(case)
        assert result.decision == by_id[case["case_id"]]["decision"], case["case_id"]
        assert result.trace, "rules engine must explain itself"


def test_rules_refund_uses_formula_not_claim():
    result = adjudicate_rules(get_case("COD-003"))   # customer claims ₹200, log says ₹100
    assert result.refund_amount_inr == 100.0


# ------------------------------------------------------------------- retrieval

def test_hybrid_retrieval_reaches_every_governing_clause_with_small_k():
    assert governing_recall("hybrid", top_k=4)["recall"] == 1.0


@pytest.mark.parametrize("method", ["lexical", "bm25", "hybrid"])
def test_every_method_keeps_priority_rules(method):
    for case in load_cases():
        got = {item.clause_id for item in retrieve(case, top_k=6, method=method)}
        assert {"SLA-PRI-01", "SLA-PRI-03", "SLA-GEN-03"} <= got


# ------------------------------------------------------------------- scoring

def test_procedural_clause_excluded_from_scoring_cod005():
    """COD-005's label lists SLA-PRI-02; a model told not to cite it must not be penalised."""
    label = get_ground_truth("COD-005")
    assert "SLA-PRI-02" in label["governing_clause_ids"]
    assert "SLA-PRI-02" in PROCEDURAL_CLAUSES
    pred = {"case_id": "COD-005", "decision": "ESCALATE", "primary_clause_id": "SLA-COD-03",
            "supporting_clause_ids": ["SLA-COD-09", "SLA-PRI-01"], "evidence_ids_used": [],
            "confidence": 0.6}
    row = score_case(pred, label)
    assert row["clause_fn"] == 0 and row["clause_fp"] == 0


def test_score_run_and_baselines():
    cases, labels = load_dataset("pilot")
    preds = [adjudicate_rules(c).to_dict() for c in cases]
    metrics = score_run(preds, labels)
    assert metrics["decision_accuracy"] == 1.0
    assert metrics["refund_accuracy"] == 1.0
    base = baselines(labels)
    assert base["majority_class"]["label"] == "APPROVE"
    assert base["majority_class"]["escalation_recall"] == 0.0


# ------------------------------------------------------------ LLM path (mock)

class MockProvider(LLMProvider):
    name = "mock"
    label = "Mock"
    env_var = "MOCK_API_KEY"
    models = ["mock/echo"]
    replies = []

    def _complete(self, system, messages, model, max_tokens, temperature):
        text = self.replies.pop(0) if self.replies else "{}"
        return ProviderResponse(text=text, model=model, provider=self.name, input_tokens=10, output_tokens=5)


@pytest.fixture
def mock_llm(monkeypatch):
    provider = MockProvider()
    register(provider)
    monkeypatch.setenv("MOCK_API_KEY", "x")
    yield provider
    MockProvider.replies = []
    from src.llm import provider as registry
    registry._REGISTRY.pop("mock", None)
    if "mock" in registry._ORDER:
        registry._ORDER.remove("mock")


GOOD = {
    "decision": "APPROVE", "primary_clause_id": "SLA-COD-04",
    "supporting_clause_ids": ["SLA-COD-01"], "evidence_ids_used": ["RECON-001"],
    "rationale": "Log shows ₹1,700 vs ₹1,500.", "resolution_type": "REFUND",
    "refund_amount_inr": 200, "confidence": 0.8,
}


@pytest.mark.parametrize("style", ["zero_shot", "facts", "cot"])
def test_llm_path_each_prompt_style(mock_llm, style):
    payload = dict(GOOD, analysis=["window ok", "log higher"]) if style == "cot" else GOOD
    MockProvider.replies = [json.dumps(payload)]
    result = adjudicate(get_case("COD-001"), model="mock/echo", prompt_style=style)
    assert result.decision == "APPROVE" and result.engine == "llm"
    assert result.cross_check["agrees"] is True
    assert result.facts and not result.warnings
    if style == "cot":
        assert len(result.trace) == 2


def test_llm_disagreement_is_flagged(mock_llm):
    MockProvider.replies = [json.dumps(dict(GOOD, decision="REJECT", primary_clause_id="SLA-COD-03"))]
    result = adjudicate(get_case("COD-001"), model="mock/echo")
    assert result.cross_check["agrees"] is False
    assert result.cross_check["rules_decision"] == "APPROVE"


def test_llm_hallucinated_ids_trigger_repair(mock_llm):
    bad = dict(GOOD, evidence_ids_used=["RECEIPT-999"])
    MockProvider.replies = [json.dumps(bad), json.dumps(GOOD)]
    result = adjudicate(get_case("COD-001"), model="mock/echo")
    assert result.evidence_ids_used == ["RECON-001"]
    assert any(w.startswith("repaired after") for w in result.warnings)


def test_auto_engine_falls_back_to_rules_without_a_key(monkeypatch):
    monkeypatch.setattr(adjudicator, "llm_ready", lambda model: False)
    result = adjudicate(get_case("DG-001"), model="openai/gpt-oss-120b", engine="auto")
    assert result.engine == "rules" and result.decision == "APPROVE"
    assert any("rules engine" in w for w in result.warnings)


def test_facts_appear_only_in_fact_prompts():
    case = get_case("COD-001")
    clauses = retrieve(case)
    assert "EXTRACTED FACTS" not in build_user_prompt(case, clauses, "zero_shot")
    assert "EXTRACTED FACTS" in build_user_prompt(case, clauses, "facts")
    assert '"analysis"' in build_user_prompt(case, clauses, "cot")
