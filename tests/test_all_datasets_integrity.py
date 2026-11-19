"""The integrity checks of validate_pilot.py, applied to all three sets (pilot, counterfactual, held-out).

The paper states that the validator passes on all 60 cases and their labels; this test is what makes that true
for the counterfactual and held-out sets, which validate_pilot.py does not read.
"""

import pytest

from src.evaluation.datasets import load_dataset
from src.validation.validate_pilot import (VALID_DECISIONS, VALID_DISPUTE_TYPES, collect_case_evidence_ids,
                                           extract_sla_clause_ids)

LABEL_ONLY = {"decision", "governing_clause_ids", "decisive_evidence_ids", "contradictory_evidence_ids",
              "missing_evidence_ids", "rationale", "sub_decisions", "ground_truth"}
EVIDENCE_FIELDS = ("decisive_evidence_ids", "contradictory_evidence_ids", "missing_evidence_ids")
SIZES = {"pilot": 10, "counterfactual": 16, "heldout": 34}


@pytest.mark.parametrize("name", sorted(SIZES))
def test_dataset_is_consistent(name):
    cases, labels = load_dataset(name)
    assert len(cases) == len(labels) == SIZES[name]
    by_case = {c["case_id"]: c for c in cases}
    assert len(by_case) == len(cases), "duplicate case IDs"
    assert set(by_case) == {l["case_id"] for l in labels}, "case and label IDs differ"
    clauses = extract_sla_clause_ids()
    for case in cases:
        assert case["dispute_type"] in VALID_DISPUTE_TYPES, case["case_id"]
        assert not LABEL_ONLY & set(case), f"{case['case_id']}: label field in the model's input"
        assert collect_case_evidence_ids(case), f"{case['case_id']}: no evidence"
    for label in labels:
        cid = label["case_id"]
        assert label["decision"] in VALID_DECISIONS, cid
        assert label["governing_clause_ids"], f"{cid}: no governing clause"
        assert set(label["governing_clause_ids"]) <= clauses, f"{cid}: unknown clause"
        evidence = collect_case_evidence_ids(by_case[cid])
        for field in EVIDENCE_FIELDS:
            assert set(label.get(field) or []) <= evidence, f"{cid}: {field} names evidence not in the case"


def test_sixty_cases_in_total():
    assert sum(len(load_dataset(n)[0]) for n in SIZES) == 60
