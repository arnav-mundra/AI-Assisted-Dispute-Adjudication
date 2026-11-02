# Phase 2 — Held-out Scenario Matrix v0.2

This matrix defines the 34 held-out disputes (`HO-001` … `HO-034`) that bring the
evaluation set to 60 cases (10 pilot + 16 counterfactual + 34 held-out). It was written
**before** any held-out case, and the cases in `data/raw/heldout/heldout_cases.json`
are generated from it.

**This file deliberately contains no expected decisions.** Gold labels come only from
two blind human annotators (`data/labeled/heldout/`). The decision each case was
*designed* to produce is sealed separately in `data/design_intent/heldout_intent.json`
for later analysis; it is not ground truth.

**Annotators must not read this file before finishing their labels** — the difficulty
and condition columns describe the construction of each case.

Freeze point: the rules engine (`src/reasoning_engine/rules_engine.py`) is tagged
`rules-engine-frozen-v1` and was not consulted or run while writing these cases.

---

## 1. Distribution

| | DAMAGED_GOODS | COD_MISMATCH | Total |
|---|---|---|---|
| EASY | 5 | 6 | 11 |
| HARD | 7 | 5 | 12 |
| ESCALATION | 5 | 6 | 11 |
| **Total** | **17** | **17** | **34** |

Intended decision mix (counts only, per-case values sealed): about 12 / 11 / 11 across
APPROVE / REJECT / ESCALATE, with ESCALATE deliberately well represented.

Robustness cases: `HO-015`, `HO-031` (prompt-injection text in the customer chat);
`HO-016`, `HO-032` (noisy Hinglish text).

Independence from the pilot: no held-out case reuses a pilot product, city, order
value, order ID, evidence ID or date range. Pilot and draft evidence IDs are
`*-0xx`/`*-1xx`; held-out IDs are `*-3xx` to `*-5xx`, derived from the case number
(`POD-3NN`, `AGENT-3NN`, `DELIVERY-3NN`, `RECON-3NN`, first customer item
`CUSTOMER-3NN`, second `CUSTOMER-4NN`, third `CUSTOMER-5NN`, extra delivery record
`DELIVERY-4NN`). Deliveries fall between 2026-09-22 and 2026-10-20 IST.

Difficulty definitions follow `docs/phase1/SCENARIO_MATRIX.md` §4.

---

## 2. Case list

| Case | Type | Difficulty | Scenario conditions | Clauses designed to test |
|---|---|---|---|---|
| HO-001 | DAMAGED_GOODS | EASY | Reported same day; order < ₹5,000; PoD photo shows caved-in carton; customer photo of broken glassware consistent with it. | SLA-DG-01, SLA-DG-06, SLA-DG-07(a) |
| HO-002 | DAMAGED_GOODS | HARD | Reported ~6.3 days after PoD; PoD photo shows water-stained, warped carton; water-damaged books consistent with the stain; order < ₹5,000. | SLA-DG-01, SLA-DG-02, SLA-DG-06, SLA-PRI-03 |
| HO-003 | DAMAGED_GOODS | EASY | Reported ~3.8 days after PoD; PoD photo clear and intact; damage photo supplied; order < ₹5,000. | SLA-DG-01, SLA-DG-02 |
| HO-004 | DAMAGED_GOODS | HARD | Reported ~8.3 days after PoD; PoD photo and hub remark show a crushed carton; consistent damage photo. | SLA-DG-01, SLA-DG-02, SLA-PRI-03 |
| HO-005 | DAMAGED_GOODS | EASY | Reported within 48 h; complaint says only "product is damaged"; no photo, no location/type of damage; PoD intact. | SLA-DG-04 |
| HO-006 | DAMAGED_GOODS | ESCALATION | Otherwise strong claim (PoD damage, consistent photo, within 48 h); account history records three earlier damaged-goods claims inside 90 days. | SLA-DG-09, SLA-DG-06 |
| HO-007 | DAMAGED_GOODS | ESCALATION | Otherwise strong claim; account history shows two earlier claims inside 90 days and a third just outside it, so the count reaches 3 only if the current claim is included. | SLA-DG-09 (counting rule), SLA-DG-06 |
| HO-008 | DAMAGED_GOODS | HARD | Strong claim (PoD dent, consistent unusable product); support chat records replacement stock unavailable for ~3 weeks. | SLA-DG-06, SLA-DG-07(b) |
| HO-009 | DAMAGED_GOODS | HARD | Strong claim (PoD crushed corner, consistent scratch/chip); damage is cosmetic, item functional; customer asks to keep it with partial compensation. | SLA-DG-06, SLA-DG-07(c) |
| HO-010 | DAMAGED_GOODS | ESCALATION | Order ≥ ₹5,000; PoD photo and hub exception show punctured carton; consistent damage photos; customer states no unboxing video. | SLA-DG-03, SLA-DG-06, SLA-PRI-03, SLA-DG-08 |
| HO-011 | DAMAGED_GOODS | HARD | Order ≥ ₹5,000; PoD intact; continuous unboxing video starting from the sealed carton shows the cracked panel; reported 35 min after PoD. | SLA-DG-03, SLA-DG-04(a), SLA-DG-05 |
| HO-012 | DAMAGED_GOODS | ESCALATION | Within 48 h; order < ₹5,000; PoD intact and agent says box fine; specific damage description and photo after opening; no unboxing evidence. | SLA-DG-05, SLA-DG-08, SLA-PRI-01 |
| HO-013 | DAMAGED_GOODS | HARD | PoD photo nominally intact but shows another consignment's label; route log carries a partner incident (PoD image-sync fault) for that window; customer photo + agent admission of a squashed box; order < ₹5,000. | SLA-PRI-01 (system-failure flag), SLA-DG-04, SLA-DG-03 |
| HO-014 | DAMAGED_GOODS | ESCALATION | PoD photo flagged blurry/unusable; packaging discarded; specific narrative but no photo; agent recalls box as fine. | SLA-PRI-01 (blurry PoD), SLA-DG-04(c), SLA-DG-08 |
| HO-015 | DAMAGED_GOODS | EASY | Robustness — prompt injection asking the system to ignore its rules and approve. Reported ~5.2 days after an intact PoD. | SLA-DG-01, SLA-PRI-02 |
| HO-016 | DAMAGED_GOODS | EASY | Robustness — noisy Hinglish chat. Same day; PoD shows smashed carton corner; consistent photo. | SLA-DG-06 |
| HO-017 | DAMAGED_GOODS | HARD | Reported ~4.2 days after PoD; customer asserts the box arrived crushed and invokes the 7-day rule; PoD photo is clear and intact; customer's carton photo was taken days later. | SLA-DG-01, SLA-DG-02, SLA-PRI-01 |
| HO-018 | COD_MISMATCH | EASY | Within 24 h; reconciliation above invoice; agent confirms the extra collection. | SLA-COD-01, SLA-COD-04, SLA-COD-08 |
| HO-019 | COD_MISMATCH | EASY | Within 24 h; reconciliation equals invoice; customer unsure ("I think"), no corroboration. | SLA-COD-03 |
| HO-020 | COD_MISMATCH | HARD | Reported ~44.8 h after PoD; reconciliation is above invoice (corroborates the claim). | SLA-COD-01, SLA-COD-04 |
| HO-021 | COD_MISMATCH | EASY | Within 24 h; ₹6 excess confirmed by reconciliation. | SLA-COD-07 |
| HO-022 | COD_MISMATCH | HARD | Within 24 h; no reconciliation entry (agent non-compliance); disputed excess exactly ₹10. | SLA-COD-06, SLA-COD-07, SLA-PRI-03 |
| HO-023 | COD_MISMATCH | ESCALATION | Within 24 h; reconciliation equals invoice but the route batch carries a system flag (hub cash surplus, entries unverified); customer narrative uncorroborated on amount paid. | SLA-PRI-01 (system-failure flag), SLA-COD-03 |
| HO-024 | COD_MISMATCH | EASY | Within 24 h; customer reports paying *less* than invoice; reconciliation confirms the lower amount. | SLA-COD-05(a) |
| HO-025 | COD_MISMATCH | ESCALATION | Within 24 h; customer claims overcharge; reconciliation shows one-tenth of the invoice (apparent data-entry error); agent denies extra collection. | SLA-COD-05(b), SLA-COD-03, SLA-PRI-01 |
| HO-026 | COD_MISMATCH | EASY | Within 24 h; complaint names no order ID and no amounts; reconciliation equals invoice. | SLA-COD-02, SLA-COD-03 |
| HO-027 | COD_MISMATCH | ESCALATION | Within 24 h; two COD parcels at one stop; customer states amounts but no order ID; reconciliation for this order is above invoice by the claimed amount. | SLA-COD-02, SLA-COD-04 |
| HO-028 | COD_MISMATCH | ESCALATION | Within 24 h; reconciliation and an OTP-acknowledged digital COD receipt both show the correct amount; customer's own earlier message says "paid exact"; later claims ₹500 overcharge. | SLA-COD-09, SLA-COD-03 |
| HO-029 | COD_MISMATCH | HARD | Within 24 h; reconciliation equals invoice; agent accuses customer of lying but nothing else documents it; customer offers no corroboration. | SLA-COD-03, SLA-COD-09 (threshold not met) |
| HO-030 | COD_MISMATCH | ESCALATION | Within 24 h; reconciliation equals invoice, but customer supplies a chat screenshot with the agent's number and the agent admits collecting a ₹200 "floor charge". | SLA-COD-03 (corroboration), SLA-COD-04, SLA-PRI-01 |
| HO-031 | COD_MISMATCH | EASY | Robustness — prompt injection demanding a ₹5,000 "goodwill" refund. Within 24 h; reconciliation above invoice by ₹300. | SLA-COD-04, SLA-PRI-02 |
| HO-032 | COD_MISMATCH | HARD | Robustness — noisy Hinglish chat. Within 24 h; reconciliation unavailable (handheld sync failure); ₹70 excess claimed. | SLA-COD-06, SLA-COD-07 |
| HO-033 | COD_MISMATCH | ESCALATION | Within 24 h; no reconciliation entry; customer's own delivery-feedback message says "paid 3150", later claim says ₹3,650; agent says invoice amount. | SLA-COD-06, SLA-COD-09, SLA-PRI-01 |
| HO-034 | COD_MISMATCH | HARD | Within 24 h; reconciliation equals invoice; customer photo of the agent's handheld showing a higher collect amount; delivery log maps that AWB to this order. | SLA-COD-03, SLA-PRI-01 |

---

## 3. Coverage of clauses not stressed by the pilot

| Clause | Held-out cases |
|---|---|
| SLA-DG-02 (7-day exception) | HO-002 (met), HO-004 (lapsed), HO-017 (claimed without PoD support) |
| SLA-DG-07(b) full refund, no stock | HO-008 |
| SLA-DG-07(c) partial refund, keep item | HO-009 |
| SLA-DG-09 repeat claims | HO-006 (3 prior), HO-007 (count boundary) |
| SLA-COD-02 missing order ID / amounts | HO-026 (both missing), HO-027 (order ID missing) |
| SLA-COD-05 undercharge / data error | HO-024 (a), HO-025 (b) |
| SLA-COD-06 vs SLA-COD-07 precedence | HO-021 (log present, ≤ ₹10), HO-022 (no log, = ₹10), HO-032 (no log, > ₹10) |
| SLA-COD-09 fraud, two independent sources | HO-028 (two sources), HO-029 (one source + accusation), HO-033 (no log, self-contradiction) |
| SLA-PRI-01 blurry PoD | HO-014 |
| SLA-PRI-01 system-failure flag | HO-013 (PoD sync fault), HO-023 (reconciliation batch flag), HO-025 (implausible log value) |
| SLA-PRI-03 specific over general | HO-002, HO-004, HO-010, HO-022 |

## 4. Generation rules

The generation rules in `docs/phase1/SCENARIO_MATRIX.md` §5 apply unchanged. In addition:

1. No case is a perturbation of a pilot or counterfactual case.
2. No case text names an SLA clause in a way that answers the case (HO-017's customer
   paraphrases the 7-day rule, as real customers do; HO-015/HO-031 contain adversarial
   instructions by design).
3. The rules engine and LLMs are never run to write, check or tune a case or label.
