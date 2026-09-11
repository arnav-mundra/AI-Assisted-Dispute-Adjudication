# Phase 1 — Dispute Scenario Matrix v0.1

This document defines the controlled scenario space for the pilot dispute
dataset. Cases must be generated from this matrix rather than randomly
invented.

The pilot dataset contains 10 cases:
- 5 DAMAGED_GOODS
- 5 COD_MISMATCH

Decision distribution: 5 APPROVE, 2 REJECT, 3 ESCALATE.

The purpose of the pilot is to validate the case schema, SLA policy,
ground-truth process, evidence representation, and difficulty distribution
before scaling the dataset.

---

## 1. Pilot Distribution

| Case ID | Dispute Type | Difficulty | Primary Challenge | Expected Decision |
|---|---|---|---|---|
| DG-001 | DAMAGED_GOODS | EASY | Clear qualifying damage | APPROVE |
| DG-002 | DAMAGED_GOODS | EASY | Clear late/ineligible claim | REJECT |
| DG-003 | DAMAGED_GOODS | HARD | Conflicting evidence | ESCALATE |
| DG-004 | DAMAGED_GOODS | HARD | High-value evidence requirement | ESCALATE |
| DG-005 | DAMAGED_GOODS | HARD | Unreliable structured evidence, discounted | APPROVE |
| COD-001 | COD_MISMATCH | EASY | Clear overcharge | APPROVE |
| COD-002 | COD_MISMATCH | EASY | Clear undercharge | REJECT |
| COD-003 | COD_MISMATCH | HARD | Reconciliation discrepancy | APPROVE |
| COD-004 | COD_MISMATCH | HARD | Missing reconciliation log | APPROVE |
| COD-005 | COD_MISMATCH | ESCALATION | Conflicting corroborating evidence | ESCALATE |

---

## 2. Damaged-Goods Scenarios

### DG-001 — Clear qualifying damage

Conditions:
- Claim reported within 48 hours.
- Item value below ₹5,000.
- PoD shows visible external package damage.
- Customer evidence is consistent with the PoD damage.
- No contradictory evidence.

Relevant clauses:
- SLA-DG-01
- SLA-DG-06
- SLA-PRI-02

Expected decision:
- APPROVE

---

### DG-002 — Late claim without exception

Conditions:
- Claim reported more than 48 hours after PoD.
- PoD does not show external package damage.
- Item value below ₹5,000.
- Customer provides damage evidence.
- No evidence activates the 7-day exception.

Relevant clauses:
- SLA-DG-01
- SLA-PRI-02

Expected decision:
- REJECT

---

### DG-003 — Contradictory evidence

Conditions:
- Claim reported within 48 hours.
- PoD shows intact package.
- Customer provides a detailed and plausible damage narrative.
- No unboxing evidence.
- Evidence is insufficient to establish fault conclusively.

Relevant clauses:
- SLA-DG-05
- SLA-DG-08
- SLA-PRI-01

Expected decision:
- ESCALATE

---

### DG-004 — High-value item without mandatory evidence

Conditions:
- Order value is at least ₹5,000.
- Claim is within the applicable reporting window.
- PoD shows the package intact and undamaged.
- Customer has no unboxing evidence.
- Customer provides a specific damage description.
- No other evidence conclusively establishes the condition of the product at delivery.

Relevant clauses:
- SLA-DG-03
- SLA-DG-05
- SLA-DG-08
- SLA-PRI-01

Expected decision:
- ESCALATE

---

### DG-005 — Unreliable structured evidence

Conditions:
- Claim is within the reporting window.
- Order value is below ₹5,000.
- Customer narrative claims damage and is supported by a post-delivery photo.
- PoD nominally conflicts with the narrative.
- There is a documented reason to doubt the PoD evidence.
- Once the PoD is discounted, the remaining evidence is consistent and
  independently corroborates the customer.

Relevant clauses:
- SLA-DG-03
- SLA-DG-04
- SLA-PRI-01

Expected decision:
- APPROVE

Tests whether the reasoning engine applies the SLA-PRI-01 reliability exception
rather than deferring to structured evidence by default — and whether it then
stops escalating once the conflict is resolved.

---

## 3. COD-Mismatch Scenarios

### COD-001 — Clear overcharge

Conditions:
- Claim is within 24 hours.
- Order total is known.
- Reconciliation amount is higher than order total.
- No contradictory evidence.

Relevant clauses:
- SLA-COD-01
- SLA-COD-03
- SLA-COD-04
- SLA-COD-08

Expected decision:
- APPROVE

Sub-decision:
- Refund = reconciliation amount − order total.

---

### COD-002 — Clear undercharge

Conditions:
- Claim is within 24 hours.
- Reconciliation amount is lower than order total.
- No evidence of customer overpayment.

Relevant clauses:
- SLA-COD-01
- SLA-COD-05

Expected decision:
- REJECT

---

### COD-003 — Reconciliation conflict

Conditions:
- Customer claims an overcharge.
- Reconciliation log differs from the customer's claimed amount.
- Reconciliation amount is higher than order total.
- Customer evidence conflicts with the reconciliation amount.

Relevant clauses:
- SLA-COD-03
- SLA-COD-04
- SLA-PRI-01

Expected decision:
- APPROVE based on structured evidence.

Sub-decision:
- Refund = reconciliation amount − order total.

---

### COD-004 — Missing reconciliation log

Conditions:
- Claim is within 24 hours.
- Reconciliation log is absent.
- Customer claims an excess payment.
- No independent evidence conclusively disproves the claim.

Relevant clauses:
- SLA-COD-01
- SLA-COD-06
- SLA-COD-07
- SLA-PRI-03

Expected decision:
- APPROVE

Sub-decision:
- Refund the disputed excess amount.

---

### COD-005 — Conflicting corroborating evidence

Conditions:
- Claim is within 24 hours.
- Reconciliation evidence suggests one amount.
- Customer evidence suggests another and is not merely a bare assertion.
- Neither side's evidence is independently corroborated to the standard SLA-COD-09
  requires for a fraud finding.
- Available evidence does not establish a defensible automatic resolution.

Relevant clauses:
- SLA-COD-03
- SLA-COD-09
- SLA-PRI-01
- SLA-PRI-02

Expected decision:
- ESCALATE

---

## 4. Difficulty Definition

### EASY

The governing clause and outcome are clear.
Evidence sources are consistent and complete.

### HARD

The case requires cross-referencing multiple evidence sources,
thresholds, exceptions, or competing clauses.

### ESCALATION

The case contains insufficient, contradictory, or reliability-compromised
evidence such that a defensible automatic binary decision is not supported.

---

## 5. Generation Rules

1. Every case must have a unique `case_id`.
2. Every case must belong to exactly one supported dispute type.
3. Every evidence item must have a unique evidence ID.
4. Every timestamp must include enough information to normalize to IST.
5. Every case must reference exactly one SLA version.
6. Ground truth must not be included in the model-input representation.
7. Ground truth must be created independently of model predictions.
8. Every ground-truth clause ID must exist in the SLA.
9. Every ground-truth evidence ID must exist in the case.
10. Synthetic cases must not introduce policies or rules absent from the SLA.
11. Cases should contain realistic evidence rather than artificial clues that
    directly reveal the expected answer.
12. Cases must deliberately include both straightforward and challenging
    evidence patterns.