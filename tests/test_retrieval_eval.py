from src.evaluation.retrieval_eval import case_check, evaluate


def test_context_recall_never_below_ranker_recall():
    result = evaluate("pilot", "lexical", 8)
    assert 0.0 <= result["ranker_recall"] <= result["context_recall"] <= 1.0
    assert result["references"] > 0 and result["mean_context"] >= 8


def test_case_check_reports_every_reference_clause():
    rows = case_check("pilot", ["COD-005"], method="lexical", top_k=12)
    # COD-005 references SLA-COD-03, SLA-COD-09 and SLA-PRI-01 (SLA-PRI-02 is procedural, excluded).
    assert {r["clause_id"] for r in rows} == {"SLA-COD-03", "SLA-COD-09", "SLA-PRI-01"}
    assert next(r for r in rows if r["clause_id"] == "SLA-PRI-01")["retrieved"] is True
