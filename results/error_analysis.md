# Error analysis and consistency

Generated from 6 saved run(s) in `results/runs/`. Confidence intervals are 95% Wilson intervals over all predictions pooled per configuration.

## Accuracy and stability by configuration

| Configuration | Runs | Accuracy (mean ± sd) | 95% CI | Escalation recall | Pairwise agreement |
|---|---|---|---|---|---|
| counterfactual · gpt-oss-120b · cot | 1 | 75% ± 0% | 51%–90% | 50% | — |
| counterfactual · rules engine | 1 | 100% ± 0% | 81%–100% | 100% | — |
| pilot · gpt-oss-120b · cot | 1 | 70% ± 0% | 40%–89% | 0% | — |
| pilot · gpt-oss-120b · facts | 1 | 80% ± 0% | 49%–94% | 33% | — |
| pilot · gpt-oss-120b · zero_shot | 1 | 80% ± 0% | 49%–94% | 33% | — |
| pilot · rules engine | 1 | 100% ± 0% | 72%–100% | 100% | — |

## Disagreement guard (simulated)

If the LLM and the rules engine disagree, escalate to manual review. Simulated from the cross-check stored with every prediction — no new model calls. Caveat: the rules engine was written with the pilot cases visible, so pilot rows are in-sample; counterfactual rows are the fairer test.

| Configuration | n | Accuracy before → after | Escalation recall before → after | Escalated by guard | Errors fixed | Correct decisions sent to review |
|---|---|---|---|---|---|---|
| counterfactual · gpt-oss-120b · cot | 16 | 75% → 88% | 50% → 100% | 3 | 2 | 0 |
| pilot · gpt-oss-120b · zero_shot | 10 | 80% → 100% | 33% → 100% | 2 | 2 | 0 |
| pilot · gpt-oss-120b · facts | 10 | 80% → 100% | 33% → 100% | 2 | 2 | 0 |
| pilot · gpt-oss-120b · cot | 10 | 70% → 100% | 0% → 100% | 3 | 3 | 0 |

## Error taxonomy

| Error kind | Count | Share |
|---|---|---|
| Forced a decision where the reference escalates | 9 | 82% |
| Escalated where the reference decides | 1 | 9% |
| Approved where the reference rejects, or the reverse | 1 | 9% |

The rules-engine cross-check reached the reference decision on **11 of 11** LLM errors — the share a disagreement flag would have routed to review.

Cases most often wrong: COD-005 (3), DG-003 (2), DG-004 (2), CF-104 (1), CF-106 (1), CF-107 (1)

## Every error

| Case | Configuration | Kind | Predicted → Reference | Cited primary | Reference clauses | Missed decisive evidence | Conf. | Rules engine |
|---|---|---|---|---|---|---|---|---|
| CF-104 | counterfactual · gpt-oss-120b · cot | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.93 | ESCALATE |
| CF-106 | counterfactual · gpt-oss-120b · cot | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04 | — | 0.93 | REJECT |
| CF-107 | counterfactual · gpt-oss-120b · cot | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | — | 0.86 | ESCALATE |
| CF-110 | counterfactual · gpt-oss-120b · cot | polarity | APPROVE → REJECT | SLA-COD-04 | SLA-COD-07 | — | 0.85 | REJECT |
| COD-005 | pilot · gpt-oss-120b · cot | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | — | 0.96 | ESCALATE |
| COD-005 | pilot · gpt-oss-120b · facts | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | — | 0.96 | ESCALATE |
| COD-005 | pilot · gpt-oss-120b · zero_shot | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | AGENT-009, CUSTOMER-014 | 0.96 | ESCALATE |
| DG-003 | pilot · gpt-oss-120b · cot | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | — | 0.78 | ESCALATE |
| DG-003 | pilot · gpt-oss-120b · zero_shot | missed escalation | APPROVE → ESCALATE | SLA-DG-04 | SLA-DG-05, SLA-DG-08 | AGENT-003 | 0.78 | ESCALATE |
| DG-004 | pilot · gpt-oss-120b · cot | missed escalation | REJECT → ESCALATE | SLA-DG-03 | SLA-DG-03, SLA-DG-05, SLA-DG-08 | AGENT-004 | 0.93 | ESCALATE |
| DG-004 | pilot · gpt-oss-120b · facts | missed escalation | REJECT → ESCALATE | SLA-DG-03 | SLA-DG-03, SLA-DG-05, SLA-DG-08 | AGENT-004 | 0.93 | ESCALATE |

## Model rationales for the errors

**CF-104 · counterfactual · gpt-oss-120b · cot** (APPROVE, reference ESCALATE)

> The claim is within the 7‑day window extended by SLA-DG-02 as the PoD photo shows external damage; structured PoD evidence is reliable per SLA-PRI-01; the customer provided a specific damage description and a photo that matches the PoD damage, satisfying SLA-DG-04; SLA-DG-06 then mandates approval without further evidence; resolution follows SLA-DG-07 default free replacement.

**CF-106 · counterfactual · gpt-oss-120b · cot** (ESCALATE, reference REJECT)

> The claim was filed within 14.6 hours of PoD, meeting SLA-DG-01. Structured PoD and delivery logs are reliable per SLA-PRI-01. However, SLA-DG-04 is not met as the customer provided no unboxing or damage photos and the description lacks specificity. With an intact PoD photo and no unboxing evidence, SLA-DG-05 shifts decision to agent discretion, but the evidence remains contradictory and insufficient, invoking SLA-DG-08 to escalate for manual review. No refund is calculated.

**CF-107 · counterfactual · gpt-oss-120b · cot** (APPROVE, reference ESCALATE)

> The claim was reported 26 hours after PoD, within the 48‑hour window (SLA-DG-01). PoD evidence is reliable (SLA-PRI-01). Customer provided a specific damage description and a post‑delivery photo, meeting SLA-DG-04. Since the PoD shows an intact package, SLA-DG-06 does not trigger; the claim is governed by SLA-DG-05, allowing agent discretion, and the credible evidence supports approval. Resolution is a free replacement per SLA-DG-07.

**CF-110 · counterfactual · gpt-oss-120b · cot** (APPROVE, reference REJECT)

> The claim was filed 4.6 hours after PoD, satisfying SLA-COD-01. Structured reconciliation log (RECON-001) is reliable per SLA-PRI-01 and shows a collection of ₹1505, higher than the invoice ₹1500, matching the customer’s reported overcharge. SLA-COD-04 therefore mandates refund of the ₹5 excess, which is approved. The refund will be processed within the SLA‑COD‑08 window.

**COD-005 · pilot · gpt-oss-120b · cot** (REJECT, reference ESCALATE)

> The claim was filed 14.8 hours after PoD, satisfying SLA-COD-01. The reconciliation log (RECON-005) is structured evidence and, per SLA-PRI-01, overrides the customer's unverified photo and statement. The log matches the invoice amount, so SLA-COD-03 triggers a presumptive rejection as no corroborating evidence meets the burden. Consequently the claim is rejected with no refund.

**COD-005 · pilot · gpt-oss-120b · facts** (REJECT, reference ESCALATE)

> The claim was filed 14.8 hours after the PoD (2026-08-16T18:35 to 2026-08-17T09:20), within the 24‑hour SLA-COD-01 window. The reconciliation log (RECON-005) records the collected amount as ₹3,200, matching the invoice, which under SLA-COD-03 presumes rejection of an overcharge claim unless corroborating evidence is provided. The customer’s photo (CUSTOMER-014) lacks verifiable metadata and does not satisfy the corroboration requirement, and structured evidence (reconciliation log) is given priority per SLA-PRI-01. Therefore the claim is rejected.

**COD-005 · pilot · gpt-oss-120b · zero_shot** (REJECT, reference ESCALATE)

> The claim was reported 14h45m after the PoD (within the 24h window per SLA-COD-01). The reconciliation log (RECON-005) shows the collected amount equals the order total (3200 INR), matching the order. Under SLA-COD-03, this structured evidence presumes rejection of an overcharge claim unless corroborating evidence outweighs it; SLA-PRI-01 gives priority to the log, and no reason exists to doubt it. Hence the claim is rejected.

**DG-003 · pilot · gpt-oss-120b · cot** (APPROVE, reference ESCALATE)

> The claim was reported 14.6 hours after delivery, satisfying SLA-DG-01's 48‑hour window. Structured PoD evidence is reliable per SLA-PRI-01. Although no unboxing photo is provided, the customer's specific written description fulfills SLA-DG-04. Because the PoD shows an intact package and no unboxing evidence, SLA-DG-05 governs, placing the decision at agent discretion, and the narrative is deemed credible, leading to approval under SLA-DG-07's default free replacement.

**DG-003 · pilot · gpt-oss-120b · zero_shot** (APPROVE, reference ESCALATE)

> The PoD timestamp (2026-08-05T18:40) to the first customer message (2026-08-06T09:15) is 14h35m, within the 48‑hour window of SLA-DG-01. The customer’s written description is specific enough to meet SLA-DG-04’s evidence requirement. PoD shows an undamaged package, so SLA-DG-06 does not apply; SLA-DG-05 shifts the claim to agent discretion, but the satisfied evidence and lack of contradictory proof allow approval. Approved claims are resolved by free replacement per SLA-DG-07.

**DG-004 · pilot · gpt-oss-120b · cot** (REJECT, reference ESCALATE)

> The claim was reported 18.6 hours after delivery, satisfying the 48‑hour window of SLA‑DG‑01. Structured PoD evidence is reliable per SLA‑PRI‑01. While the customer gave a specific damage description meeting SLA‑DG‑04(c), the order value exceeds ₹5,000, so SLA‑DG‑03 mandates unboxing evidence, which the customer did not provide. Consequently the claim fails the mandatory evidence requirement and is rejected.

**DG-004 · pilot · gpt-oss-120b · facts** (REJECT, reference ESCALATE)

> The PoD timestamp (08 Aug 2026 15:50 IST) to first customer message (09 Aug 2026 10:25 IST) is 18.6 hours, within the 48‑hour window of SLA-DG-01. However, the order value ₹7,499 exceeds the ₹5,000 threshold, so SLA-DG-03 mandates unboxing evidence for a high‑value claim. The customer provided no unboxing photo/video, only a written description, which satisfies SLA-DG-04 but does not meet the stricter SLA-DG-03 requirement. Consequently the claim is ineligible and must be rejected.

