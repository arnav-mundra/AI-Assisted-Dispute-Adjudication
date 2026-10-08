# Draft cases — unlabelled

`draft_cases.json` holds 10 new cases (DG-011 to DG-015, COD-011 to COD-015) drafted on
2026-10-09 to grow the dataset beyond the 10 pilot cases. **They have no reference labels.**
They are not used by the evaluation, the app, or the tests until a person labels them.

## Why no labels

The drafts were written by Claude, which also helped build the pipeline. A label written by
the same hand would just restate one reading of the SLA, which is what the independence rule
in `docs/phase0/GROUND_TRUTH_SCHEMA.md` exists to prevent. For the same reason, the list below
says which SLA condition each case is built around, **not** what the outcome should be.

## What each case exercises

| Case | SLA area exercised | Notes for the labeller |
|---|---|---|
| DG-011 | SLA-DG-09 repeat claims | Delivery log records prior claims on the account |
| DG-012 | SLA-DG-03 high value + SLA-PRI-01 unusable PoD | Unboxing video provided; PoD photo is blurry |
| DG-013 | SLA-DG-04 evidence sufficiency | Vague complaint, no photo |
| DG-014 | SLA-DG-01 / DG-02 window and its exception | Reported ~5 days after PoD; PoD shows a crushed corner |
| DG-015 | SLA-DG-03 high value without unboxing evidence | Damage photo after opening, no video, PoD intact |
| COD-011 | SLA-COD-07 small discrepancy | ₹5 difference |
| COD-012 | SLA-COD-01 window vs SLA-COD-04 | Reported ~2 days after PoD; reconciliation is above invoice |
| COD-013 | SLA-COD-03 corroboration + SLA-PRI-01 record reliability | Customer photo of notes; reconciliation note reports a scanner outage |
| COD-014 | SLA-COD-09 fraud flag | Customer changes their account of payment; UPI gateway reference matches invoice |
| COD-015 | SLA-COD-02 claim completeness | No order ID or amounts stated |

## How to label them

1. Fill in `labeling_template.csv` (decision, governing clause IDs, decisive evidence IDs,
   rationale, your labeller ID) while reading `draft_cases.json` and `docs/sla_policy.md`.
   Do not look at model or rules-engine output for these cases first.
2. Convert the filled rows into the ground-truth schema (`docs/phase0/GROUND_TRUTH_SCHEMA.md`),
   ideally with a second labeller for agreement (`python -m src.validation.agreement`).
3. Only then move the cases and labels into a named dataset in `src/evaluation/datasets.py`.
