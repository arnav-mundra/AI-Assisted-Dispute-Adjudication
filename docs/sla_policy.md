# Service Level Agreement (SLA) — Delivery, Returns & COD Policy
**Document type:** Draft / synthetic reference policy for research use
**Applies to:** D2C order fulfillment via third-party delivery partners (India operations)
**Version:** 0.1 (Phase 0 draft)
**Status:** For internal research/prototyping use only — not a real company's legal SLA

> **Note for this project:** This document is deliberately written the way a mid-size
> D2C brand's operations/legal team would write an internal SLA — specific, numbered,
> and enumerable — so each clause can be treated as a retrievable unit (`clause_id`)
> by the clause-matching module in Phase 3. Ambiguity and edge cases are intentionally
> left in a few places, since real SLAs are imperfect and the reasoning engine should
> be tested against that imperfection, not just clean cases.

---

## 1. Purpose & Scope

**SLA-GEN-01.** This SLA governs the resolution of customer disputes arising from
last-mile delivery of orders placed on the Company's D2C storefront, specifically:
(a) damaged-goods claims, and (b) cash-on-delivery (COD) amount mismatches. It binds
the Company, its logistics/delivery partners, and its customer support team.

**SLA-GEN-02.** This SLA does not cover: lost-in-transit claims, wrong-item claims,
size/fit returns, or disputes arising from prepaid payment gateway failures. These are
governed by separate policies and are out of scope for this research project.

**SLA-GEN-03.** All timestamps referenced in this document are in IST (UTC+5:30).
Delivery logs, chat timestamps, and Proof-of-Delivery (PoD) timestamps must be
normalized to IST before comparison.

---

## 2. Definitions

**SLA-DEF-01.** *Proof of Delivery (PoD)* — the delivery partner's system record at
handover, comprising: OTP confirmation (if applicable), a delivery photo, GPS
coordinates, and a timestamp.

**SLA-DEF-02.** *Damaged-Goods Claim* — a customer report that the product received
was damaged, broken, tampered with, or otherwise not in sellable condition at the
time of delivery.

**SLA-DEF-03.** *COD Mismatch* — a customer report that the amount collected by the
delivery agent at handover differs from the order total shown on the order
confirmation/invoice, in either direction (overcharge or undercharge).

**SLA-DEF-04.** *Reporting Window* — the period during which a customer may file a
claim, measured from the PoD timestamp.

**SLA-DEF-05.** *Unboxing Evidence* — photo or video evidence, provided by the
customer, showing the package and/or product condition, ideally captured at or near
the time of opening.

---

## 3. Damaged-Goods Claims

### 3.1 Eligibility & Reporting Window

**SLA-DG-01.** A damaged-goods claim is eligible for review only if reported within
**48 hours** of the PoD timestamp. Claims filed after 48 hours are presumptively
**ineligible**, unless SLA-DG-02 applies.

**SLA-DG-02.** *Exception:* if the delivery partner's PoD photo (SLA-DEF-01) itself
shows visible external package damage (crushed box, torn packaging, visible liquid
staining, etc.), the reporting window extends to **7 days**, since visible pre-existing
damage is evidence the issue may not be attributable to the customer.

**SLA-DG-03.** Claims for high-value items (order value ≥ ₹5,000) require unboxing
evidence (SLA-DEF-05) regardless of reporting window. Claims for items below this
threshold may be resolved on customer narrative + PoD photo alone if no unboxing
evidence is available, at the adjudicator's discretion.

The reporting-window extension under SLA-DG-02 does not waive this
evidence requirement.

### 3.2 Evidence Requirements

**SLA-DG-04.** A damaged-goods claim must include at least one of:
(a) unboxing photo/video (SLA-DEF-05),
(b) a photo of the damaged product taken after delivery, or
(c) a written description sufficiently specific to identify the type and location of
damage (e.g., "screen cracked in top-left corner" rather than "item damaged").

**SLA-DG-05.** If the PoD photo (SLA-DEF-01) shows the package intact and undamaged,
and the customer provides no unboxing evidence, the claim shifts to **agent
discretion** — it may still be approved based on narrative credibility and product
category (e.g., electronics vs. low-fragility goods), but is not auto-approved.

**SLA-DG-06.** If the PoD photo shows visible external damage AND the customer's
claim/photo is consistent with that damage (same product, matching damage
description), the claim should be **approved** without further evidence.

### 3.3 Resolution Outcomes

**SLA-DG-07.** Approved damaged-goods claims are resolved via one of: (a) free
replacement (default, subject to stock), (b) full refund if replacement stock is
unavailable within 5 business days, or (c) partial refund if the customer opts to
keep the item and the damage is cosmetic/non-functional (agent discretion, typically
20-40% of item value).

**SLA-DG-08.** If evidence is contradictory or insufficient to determine fault (e.g.,
PoD shows intact package, no unboxing video, but customer narrative is detailed and
consistent with a plausible in-transit cause) the case should be flagged as
**"insufficient evidence — escalate to manual review"** rather than auto-approved or
auto-rejected. This clause exists specifically to test whether the reasoning engine
abstains appropriately rather than forcing a binary decision (see Objective 5,
error analysis / bias testing).

**SLA-DG-09.** Repeat damaged-goods claims from the same customer (3+ in a rolling
90-day window) should be flagged for manual fraud review rather than resolved via
standard workflow, regardless of individual claim merit.

---

## 4. COD Mismatch Claims

### 4.1 Eligibility & Reporting Window

**SLA-COD-01.** A COD mismatch claim is eligible for review only if reported within
**24 hours** of the PoD timestamp, since cash reconciliation happens on a daily
cycle with the delivery partner.

**SLA-COD-02.** Claims must reference the specific order ID and state the amount
collected by the delivery agent vs. the amount shown on the order confirmation.

### 4.2 Evidence & Reconciliation

**SLA-COD-03.** The primary evidence source is the delivery partner's **cash
reconciliation log**, which records the amount the agent remitted to the delivery
partner for that order. If the reconciliation log matches the order total, the
customer's claim of overcharge is **presumptively rejected** unless the customer
provides corroborating evidence (e.g., a photo of the amount handed over, a chat
screenshot with the agent).

**SLA-COD-04.** If the reconciliation log shows an amount **higher** than the order
total, this corroborates a customer overcharge claim, and the excess amount should
be **refunded** to the customer's original payment method or store credit (customer's
choice) within 5 business days. The refund amount is calculated as:
reconciliation amount − order total.

**SLA-COD-05.** If the reconciliation log shows an amount **lower** than the order
total, this indicates either (a) an undercharge by the agent — no customer-facing
action needed, Company absorbs/investigates internally — or (b) a data entry error,
which should be flagged for internal audit but does not constitute a customer
dispute.

**SLA-COD-06.** If the delivery partner has **no reconciliation log** for the order
(system failure, agent non-compliance), the claim defaults to **customer-favorable
resolution**: refund the disputed excess amount, since the absence of records is an
operational failure on the Company/delivery-partner side, not the customer's burden
to prove.

When the reconciliation log is absent, SLA-COD-06 takes precedence over
SLA-COD-07, including where the disputed amount is ₹10 or less.

**SLA-COD-07.** Discrepancies of ≤ ₹10 are treated as rounding/change-related and are
**not eligible** for formal dispute resolution; agents should resolve these directly
with the customer at time of delivery.

### 4.3 Resolution Outcomes

**SLA-COD-08.** All approved COD mismatch refunds must be processed within **5
business days** of claim approval.

**SLA-COD-09.** SLA-COD-09. If a COD mismatch claim is found to be fraudulent 
based on at least two independent corroborating evidence sources
establishing that the customer paid the correct amount and that the
claimed mismatch is knowingly false, the case should be flagged for
account-level review, not merely rejected.

---

## 5. Adjudication Priority Rules

**SLA-PRI-01.** Where structured evidence (PoD, reconciliation logs) and unstructured
evidence (chat/email narrative) conflict, structured evidence takes priority **unless**
there is a specific, documented reason to doubt it (e.g., the PoD photo is blurry,
timestamped implausibly, or the log has a known system-failure flag for that day/route).

**SLA-PRI-02.** Every resolution — approve, reject, or escalate — must cite the
specific clause(s) relied upon (e.g., "SLA-DG-06") and the specific evidence items
that satisfied or failed to satisfy that clause. Resolutions without a cited clause
are considered non-compliant with this SLA for research-evaluation purposes.

Every cited clause_id and evidence_id must correspond to an actual clause
or evidence item present in the case and policy records. References to
non-existent or unverifiable evidence are non-compliant.

**SLA-PRI-03.** When two clauses appear to conflict for the same case, the more
specific clause governs over the more general one (e.g., SLA-DG-02's 7-day exception
governs over SLA-DG-01's 48-hour default when its condition is met).

---

## 6. Document Notes (for dataset construction)

This SLA is intentionally structured so that:
- Every clause has a stable `clause_id` (e.g., `SLA-DG-06`) for use as a retrieval
  target in the clause-matching module (Phase 3).
- Several clauses require **cross-referencing evidence** (PoD photo state + customer
  narrative + order value), so the reasoning engine cannot resolve cases by
  keyword-matching a single clause alone.
- Clauses SLA-DG-08 and SLA-DG-05 deliberately encode **agent discretion / escalation**
  rather than hard rules, to test whether the LLM over-confidently forces a decision
  where a human would escalate — directly relevant to Objective 5 (error analysis)
  and the explainability/hallucination concerns raised in the Dehghani et al. (2025)
  survey.
- Numeric thresholds (₹5,000 order value, ₹10 rounding tolerance, 24h/48h/7-day
  windows) are chosen to be realistic but are placeholders; revisit once literature
  review / any available industry benchmarks (Section 1 of project brief) suggest
  more representative values.
