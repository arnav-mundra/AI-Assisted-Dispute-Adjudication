# Phase 0 — Dispute Case Schema v0.1

This schema defines the canonical representation of one dispute case before any model is run.
The schema is designed to preserve raw evidence and prevent the reasoning layer from silently inventing facts.

## Required top-level fields

- `case_id`: unique stable identifier.
- `dispute_type`: `DAMAGED_GOODS` or `COD_MISMATCH`.
- `order`: order metadata and monetary values.
- `customer_evidence`: customer-side chat/email evidence.
- `agent_evidence`: delivery-agent statements/evidence.
- `delivery_evidence`: pickup, PoD, delivery and reconciliation records.
- `sla_version`: exact SLA version used for adjudication.
- `ground_truth`: reference label, kept separate from model input during evaluation.

## Evidence principle

Raw evidence must remain available. Derived fields such as `hours_since_delivery` may be added later by the extraction module, but they must never replace the original timestamps or source text.

## Leakage rule

`ground_truth` is never supplied to the model during evaluation. The evaluator joins predictions with ground truth only after inference.
