# Phase 1 — Pilot Case Schema v0.1

This document defines the concrete JSON representation used for the
10-case pilot dataset in `data/raw/pilot/pilot_cases.json`.

It implements the canonical Phase 0 Case Schema v0.1
(`docs/phase0/case_schema.json`) without changing its required
top-level fields.

---

## 1. Top-Level Structure

The file is a JSON list of 10 case objects. Each case must contain:

- `case_id`
- `dispute_type`
- `order`
- `customer_evidence`
- `agent_evidence`
- `delivery_evidence`
- `sla_version`

Ground truth is **not** part of a case. The 10 reference labels live in
`data/labeled/pilot/pilot_ground_truth.json` and are joined by `case_id`.
`src/validation/validate_pilot.py` fails the dataset if a `ground_truth`
key appears in a raw case.

---

## 2. Evidence Items

`customer_evidence`, `agent_evidence` and `delivery_evidence` are lists of
evidence items. Each item carries `evidence_id`, `type` and `timestamp_ist`
(ISO-8601 with `+05:30`, per SLA-GEN-03), plus type-specific fields.

Evidence IDs are unique across the pilot dataset:

| Prefix | Section | Meaning |
|---|---|---|
| `CUSTOMER-` | `customer_evidence` | Chat/email message or customer photo |
| `AGENT-` | `agent_evidence` | Delivery-agent statement |
| `POD-` | `delivery_evidence` | Proof of Delivery record (SLA-DEF-01) |
| `DELIVERY-` | `delivery_evidence` | Route/hub delivery log |
| `RECON-` | `delivery_evidence` | Cash reconciliation log (SLA-COD-03) |

---

## 3. Example (abridged, real case COD-004)

```json
{
  "case_id": "COD-004",
  "dispute_type": "COD_MISMATCH",
  "order": {
    "order_id": "ORD-2026-41377",
    "order_value_inr": 2350.00,
    "order_total_cod_inr": 2350.00,
    "payment_mode": "COD",
    "product_category": "KITCHENWARE",
    "city": "Kolkata"
  },
  "customer_evidence": [
    {
      "evidence_id": "CUSTOMER-012",
      "type": "CHAT_MESSAGE",
      "channel": "support_chat",
      "timestamp_ist": "2026-08-16T10:30:00+05:30",
      "text": "... the agent collected 2500 in cash ... invoice total is 2350 ..."
    }
  ],
  "agent_evidence": [
    {
      "evidence_id": "AGENT-010",
      "type": "AGENT_STATEMENT",
      "timestamp_ist": "2026-08-16T14:15:00+05:30",
      "text": "agent has not responded to the helpdesk request for a statement"
    }
  ],
  "delivery_evidence": [
    {
      "evidence_id": "POD-009",
      "type": "POD",
      "timestamp_ist": "2026-08-15T19:05:00+05:30",
      "otp_confirmed": true,
      "gps": "22.5726,88.3639",
      "image_quality": "clear",
      "photo_description": "Carton photographed at a flat entrance; packaging intact."
    },
    {
      "evidence_id": "RECON-004",
      "type": "RECONCILIATION_LOG",
      "timestamp_ist": "2026-08-16T09:00:00+05:30",
      "status": "UNAVAILABLE",
      "amount_collected_inr": null,
      "note": "No reconciliation entry exists for this AWB ... system outage ..."
    }
  ],
  "sla_version": "0.1"
}
```

---

## 4. Authoring Rules

Cases are generated from `docs/phase1/SCENARIO_MATRIX.md`, subject to its
§5 generation rules. In particular:

1. No fact, rule or threshold that is not present in `docs/sla_policy.md`.
2. The claim-report time is the timestamp of the first customer message — it is
   never pre-computed into a "reported within N hours" field, so the reasoning
   engine must derive the reporting window itself.
3. No clue text that names the expected decision or the governing clause.
4. Every evidence ID cited by ground truth must exist in the corresponding case.

Run `python -m src.validation.validate_pilot` after any edit to this dataset.
