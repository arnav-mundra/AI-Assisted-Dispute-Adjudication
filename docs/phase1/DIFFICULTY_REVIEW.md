# Phase 1 — Difficulty Distribution Review

Checklist item: *Difficulty distribution reviewed against the matrix (EASY / HARD / ESCALATION)*.
Prepared 2026-10-09 by Claude from `SCENARIO_MATRIX.md`, the frozen pilot labels and the
counterfactual labels. **Needs sign-off by a project member before the checklist box is ticked.**

## Pilot: difficulty × decision

| Difficulty | APPROVE | REJECT | ESCALATE | Total |
|---|---|---|---|---|
| EASY | 2 (DG-001, COD-001) | 2 (DG-002, COD-002) | 0 | 4 |
| HARD | 3 (DG-005, COD-003, COD-004) | 0 | 2 (DG-003, DG-004) | 5 |
| ESCALATION | 0 | 0 | 1 (COD-005) | 1 |
| **Total** | 5 | 2 | 3 | 10 |

Both dispute types have all three decisions (DG: 2/1/2, COD: 3/1/1). The matrix's stated
distribution (5 APPROVE, 2 REJECT, 3 ESCALATE) matches the labels.

## Findings

1. **DG-003 and DG-004 are tagged HARD but meet the ESCALATION definition.** Section 4 defines
   ESCALATION as "insufficient, contradictory, or reliability-compromised evidence such that a
   defensible automatic binary decision is not supported". DG-003 ("conflicting evidence") and
   DG-004 (required unboxing evidence missing) are exactly that, and both are labelled ESCALATE.
   As tagged, *ESCALATION difficulty* has one case and *HARD* mixes decidable and undecidable
   cases, so any "accuracy by difficulty" figure is distorted. **Suggested fix:** retag both as
   ESCALATION (giving EASY 4 / HARD 3 / ESCALATION 3), or record why they stay HARD.
2. **No HARD REJECT.** Every hard case either approves or escalates, so the pilot never tests a
   hard *rejection*, such as an exception whose condition is nearly but not quite met. All
   rejections are EASY. The counterfactual set adds 7 rejections, but most come from simple
   timing edits (EASY-like).
3. **REJECT is thin (2/10).** A model biased toward rejecting can only lose two cases on the
   pilot. This matters because every LLM error so far was a forced REJECT or APPROVE where
   the reference escalates (see `results/error_analysis.md`).
4. **Only one COD escalation in total.** The pilot has one (COD-005) and the counterfactual set
   has none, so COD escalation recall rests on a single case.
5. **Clause coverage.** Reference labels never cite SLA-COD-02 (claim completeness),
   SLA-DG-07 (resolution options) or SLA-PRI-03 (specific-over-general), even with the
   counterfactual set included. The pilot alone also never cites SLA-DG-02 or SLA-DG-09.
   The draft cases in `data/synthetic/drafts/` target several of these gaps (COD-015: COD-02;
   DG-014: DG-02 and PRI-03; DG-011: DG-09).

## Recommendations before scaling

- Resolve finding 1 in the matrix (a tag change, not a label change, so no `revision_note` is needed).
- When labelling the drafts or adding cases, aim for at least two HARD REJECT and two more COD
  ESCALATE cases.
- Report escalation recall with its confidence interval: with 3–4 escalation cases per set,
  one case moves it by 25–33 points.
