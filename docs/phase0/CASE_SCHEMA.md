# Phase 0 — Dispute Case Schema v0.1

This schema defines the canonical representation of one dispute case before any model is run.
The schema is designed to preserve raw evidence and prevent the reasoning layer from silently inventing facts.

The machine-readable form is `docs/phase0/case_schema.json`.

## Required top-level fields

- `case_id`: unique stable identifier (e.g. `DG-001`, `COD-004`).
- `dispute_type`: `DAMAGED_GOODS` or `COD_MISMATCH`.
- `order`: order metadata and monetary values.
- `customer_evidence`: customer-side chat/email/photo evidence.
- `agent_evidence`: delivery-agent statements/evidence.
- `delivery_evidence`: PoD, delivery/route logs and cash reconciliation records.
- `sla_version`: exact SLA version used for adjudication.

`ground_truth` is **not** a field of a case. Reference labels live in `data/labeled/`
(e.g. `data/labeled/pilot/pilot_ground_truth.json`) and are joined to cases by `case_id`
after inference. A case object carrying a `ground_truth` key is invalid.

## Evidence representation

Each of `customer_evidence`, `agent_evidence` and `delivery_evidence` is a **list** of
evidence items. Every item is a self-contained record:

| Field | Required | Purpose |
|---|---|---|
| `evidence_id` | yes | Unique, stable ID (`CUSTOMER-001`, `AGENT-003`, `POD-005`, `RECON-004`, `DELIVERY-005`). Ground truth cites these IDs. |
| `type` | yes | `CHAT_MESSAGE`, `PHOTO`, `AGENT_STATEMENT`, `POD`, `DELIVERY_LOG`, `RECONCILIATION_LOG` |
| `timestamp_ist` | yes | ISO-8601 with `+05:30`, per SLA-GEN-03 |
| `text` / `photo_description` | no | Source narrative or a description of image content |
| `status`, `amount_collected_inr` | no | Reconciliation records: `RECORDED` / `UNAVAILABLE`, and the amount remitted |
| `image_quality`, `reliability_note` | no | Documented reason to doubt structured evidence, per SLA-PRI-01 |

Evidence IDs are unique across the whole dataset, not just within a case, so a label can
reference an evidence item unambiguously.

## Evidence principle

Raw evidence must remain available. Derived fields such as `hours_since_delivery` may be added later by the extraction module, but they must never replace the original timestamps or source text.

## Leakage rule

`ground_truth` is never supplied to the model during evaluation. The evaluator joins predictions with ground truth only after inference.
