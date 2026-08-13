# Phase 0 — Ground Truth Schema v0.1

Ground truth is the reference adjudication against which model outputs are evaluated.
It must be created independently of the model being tested.

## Decision labels

- `APPROVE`: evidence satisfies the governing SLA conditions for approval.
- `REJECT`: evidence satisfies the governing SLA conditions for rejection/ineligibility.
- `ESCALATE`: the SLA/evidence does not support a defensible automatic binary decision, or explicitly requires manual review.

## Required ground-truth fields

| Field | Purpose |
|---|---|
| `case_id` | Joins the label to the case |
| `decision` | APPROVE / REJECT / ESCALATE |
| `governing_clause_ids` | One or more SLA clauses relied upon |
| `decisive_evidence_ids` | Evidence items that determine the outcome |
| `contradictory_evidence_ids` | Evidence that conflicts with the decision |
| `missing_evidence_ids` | Required/important evidence that is absent |
| `rationale` | Human/reference adjudicator explanation |
| `sub_decisions` | Fine-grained outputs such as refund amount or resolution type |
| `labeler_id` | Anonymous adjudicator identifier |
| `label_timestamp` | Timestamp of labeling |
| `policy_version` | SLA version used |

## Independence rule

For the held-out test set, the reference label must be finalized before model predictions are inspected.
If multiple human adjudicators are used, disagreement should be recorded rather than silently averaged away.
