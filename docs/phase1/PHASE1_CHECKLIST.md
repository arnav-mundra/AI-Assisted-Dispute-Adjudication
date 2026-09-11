# Phase 1 Completion Checklist

Pilot stage (10 cases) — must be complete before the dataset is scaled.

- [x] Scenario matrix v0.1 defined (`docs/phase1/SCENARIO_MATRIX.md`)
- [x] Pilot case schema v0.1 defined (`docs/phase1/PILOT_CASE_SCHEMA.md`)
- [x] Case schema reconciled with the validator (evidence lists, no `ground_truth` in cases)
- [x] 10 pilot cases authored (`data/raw/pilot/pilot_cases.json`)
- [x] 10 ground-truth labels authored (`data/labeled/pilot/pilot_ground_truth.json`)
- [x] Pilot dataset tracked in git (`.gitignore` negation for `data/raw/pilot/`)
- [x] Structural validator passes (`python -m src.validation.validate_pilot`)
- [x] Case-vs-schema test added (`tests/test_pilot_cases_schema.py`)
- [x] Full test suite run on Python 3.11 (`python -m pytest -v` — 5 passed)
- [ ] Second-labeler review of the 10 pilot labels (inter-annotator agreement)
- [ ] Difficulty distribution reviewed against the matrix (EASY / HARD / ESCALATION)
- [ ] Freeze pilot dataset, then scale to the full dataset

## Pilot exit criteria

1. Every ground-truth decision is derivable from the case evidence and the SLA alone —
   no clue text, no rule that is absent from `docs/sla_policy.md`.
2. Every cited clause ID and evidence ID resolves (SLA-PRI-02).
3. All three decisions (APPROVE / REJECT / ESCALATE) and both dispute types are represented.
4. Validation is reproducible from a clean checkout.
