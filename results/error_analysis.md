# Error analysis and consistency

Generated from 12 saved run(s) in `results/runs/`. Confidence intervals are 95% Wilson intervals over all predictions pooled per configuration.

## Accuracy and stability by configuration

| Configuration | Runs | Accuracy (mean ± sd) | 95% CI | Escalation recall | Pairwise agreement |
|---|---|---|---|---|---|
| counterfactual · gpt-oss-120b · zero_shot · hybrid k=12 | 1 | 81% ± 0% | 57%–93% | 50% | — |
| counterfactual · qwen3.8-27b · cot · hybrid k=12 | 1 | 69% ± 0% | 44%–86% | 50% | — |
| counterfactual · rules engine | 1 | 100% ± 0% | 81%–100% | 100% | — |
| pilot · gpt-oss-120b · cot · hybrid k=12 | 1 | 90% ± 0% | 60%–98% | 67% | — |
| pilot · gpt-oss-120b · facts · hybrid k=12 | 1 | 80% ± 0% | 49%–94% | 33% | — |
| pilot · gpt-oss-120b · zero_shot · hybrid k=12 | 1 | 80% ± 0% | 49%–94% | 33% | — |
| pilot · gpt-oss-20b · cot · hybrid k=12 | 1 | 90% ± 0% | 60%–98% | 67% | — |
| pilot · gpt-oss-20b · zero_shot · hybrid k=12 | 1 | 70% ± 0% | 40%–89% | 33% | — |
| pilot · qwen3.8-27b · cot · hybrid k=12 | 1 | 90% ± 0% | 60%–98% | 67% | — |
| pilot · qwen3.8-27b · facts · hybrid k=12 | 1 | 90% ± 0% | 60%–98% | 67% | — |
| pilot · qwen3.8-27b · zero_shot · hybrid k=12 | 1 | 80% ± 0% | 49%–94% | 67% | — |
| pilot · rules engine | 1 | 100% ± 0% | 72%–100% | 100% | — |

## Disagreement guard (simulated)

If the LLM and the rules engine disagree, escalate to manual review. Simulated from the cross-check stored with every prediction — no new model calls. Caveat: the rules engine was written with the pilot cases visible, so pilot rows are in-sample; counterfactual rows are the fairer test.

| Configuration | n | Accuracy before → after | Escalation recall before → after | Escalated by guard | Errors fixed | Correct decisions sent to review |
|---|---|---|---|---|---|---|
| pilot · qwen3.8-27b · zero_shot · hybrid k=12 | 10 | 80% → 90% | 67% → 100% | 1 | 1 | 0 |
| pilot · gpt-oss-20b · zero_shot · hybrid k=12 | 10 | 70% → 90% | 33% → 100% | 2 | 2 | 0 |
| pilot · qwen3.8-27b · facts · hybrid k=12 | 10 | 90% → 100% | 67% → 100% | 1 | 1 | 0 |
| counterfactual · qwen3.8-27b · cot · hybrid k=12 | 16 | 69% → 81% | 50% → 100% | 3 | 2 | 0 |
| pilot · gpt-oss-20b · cot · hybrid k=12 | 10 | 90% → 100% | 67% → 100% | 1 | 1 | 0 |
| pilot · qwen3.8-27b · cot · hybrid k=12 | 10 | 90% → 100% | 67% → 100% | 1 | 1 | 0 |
| counterfactual · gpt-oss-120b · zero_shot · hybrid k=12 | 16 | 81% → 94% | 50% → 100% | 2 | 2 | 0 |
| pilot · gpt-oss-120b · cot · hybrid k=12 | 10 | 90% → 100% | 67% → 100% | 1 | 1 | 0 |
| pilot · gpt-oss-120b · facts · hybrid k=12 | 10 | 80% → 100% | 33% → 100% | 2 | 2 | 0 |
| pilot · gpt-oss-120b · zero_shot · hybrid k=12 | 10 | 80% → 100% | 33% → 100% | 2 | 2 | 0 |

## Confidence floor (simulated)

Escalate any LLM ruling whose own confidence is below the floor. Pooled over every unguarded LLM run above. A floor only helps if the model is less confident when it is wrong — compare the two right-hand columns.

| Floor | Predictions | Accuracy before → after | Escalated | Errors fixed | Correct rulings sent to review |
|---|---|---|---|---|---|
| 0.50 | 112 | 81% → 81% | 0 | 0 | 0 |
| 0.60 | 112 | 81% → 81% | 0 | 0 | 0 |
| 0.70 | 112 | 81% → 81% | 0 | 0 | 0 |
| 0.80 | 112 | 81% → 82% | 3 | 2 | 1 |
| 0.90 | 112 | 81% → 79% | 11 | 4 | 6 |
| 0.95 | 112 | 81% → 77% | 16 | 5 | 10 |

## Error taxonomy

| Error kind | Count | Share |
|---|---|---|
| Forced a decision where the reference escalates | 15 | 71% |
| Escalated where the reference decides | 5 | 24% |
| Approved where the reference rejects, or the reverse | 1 | 5% |

The rules-engine cross-check reached the reference decision on **21 of 21** LLM errors — the share a disagreement flag would have routed to review.

Cases most often wrong: COD-005 (8), DG-002 (2), CF-104 (2), CF-106 (2), DG-004 (2), DG-003 (1)

## Every error

| Case | Configuration | Kind | Predicted → Reference | Cited primary | Reference clauses | Missed decisive evidence | Conf. | Rules engine |
|---|---|---|---|---|---|---|---|---|
| CF-101 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-01 | — | 0.95 | REJECT |
| CF-103 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | polarity | APPROVE → REJECT | SLA-DG-06 | SLA-DG-01, SLA-DG-02 | — | 0.85 | REJECT |
| CF-104 | counterfactual · gpt-oss-120b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.96 | ESCALATE |
| CF-104 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.95 | ESCALATE |
| CF-105 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09 | DELIVERY-901 | 0.95 | ESCALATE |
| CF-106 | counterfactual · gpt-oss-120b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04 | — | 0.95 | REJECT |
| CF-106 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04 | — | 0.95 | REJECT |
| CF-107 | counterfactual · gpt-oss-120b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | — | 0.78 | ESCALATE |
| COD-005 | pilot · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | — | 0.96 | ESCALATE |
| COD-005 | pilot · gpt-oss-120b · facts · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | CUSTOMER-014 | 0.96 | ESCALATE |
| COD-005 | pilot · gpt-oss-120b · zero_shot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | AGENT-009 | 0.96 | ESCALATE |
| COD-005 | pilot · gpt-oss-20b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | CUSTOMER-014 | 0.85 | ESCALATE |
| COD-005 | pilot · gpt-oss-20b · zero_shot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | CUSTOMER-014 | 0.95 | ESCALATE |
| COD-005 | pilot · qwen3.8-27b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | AGENT-009 | 0.95 | ESCALATE |
| COD-005 | pilot · qwen3.8-27b · facts · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | — | 0.95 | ESCALATE |
| COD-005 | pilot · qwen3.8-27b · zero_shot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | — | 0.95 | ESCALATE |
| DG-002 | pilot · gpt-oss-20b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-01 | — | 0.85 | REJECT |
| DG-002 | pilot · qwen3.8-27b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-01 | — | 0.95 | REJECT |
| DG-003 | pilot · gpt-oss-20b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | — | 0.75 | ESCALATE |
| DG-004 | pilot · gpt-oss-120b · facts · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-DG-03 | SLA-DG-03, SLA-DG-05, SLA-DG-08 | AGENT-004 | 0.92 | ESCALATE |
| DG-004 | pilot · gpt-oss-120b · zero_shot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-DG-03 | SLA-DG-03, SLA-DG-05, SLA-DG-08 | — | 0.85 | ESCALATE |

## Model rationales for the errors

**CF-101 · counterfactual · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 60 hours after delivery, missing the 48-hour window in SLA-DG-01, and the PoD photo (POD-003) shows an intact package, so the SLA-DG-02 extension does not apply. Under SLA-DG-05, when the PoD shows an intact package and no unboxing evidence is provided, the claim shifts to agent discretion. The customer's specific description (CUSTOMER-005) satisfies SLA-DG-04, but the conflict between the intact PoD (POD-003) and the reported internal damage requires manual review to determine fault.

**CF-103 · counterfactual · qwen3.8-27b · cot · hybrid k=12** (APPROVE, reference REJECT)

> The PoD photo (POD-001) shows visible external damage (crushed corner, torn flap), which extends the reporting window to 7 days under SLA-DG-02. Although the customer reported the issue at 200 hours (exceeding the 168-hour window), the SLA does not provide an automatic rejection for late reporting when the 7-day exception is triggered by visible pre-existing damage. The customer's photo (CUSTOMER-002) and description (CUSTOMER-001) are consistent with the external damage shown in the PoD, satisfying the conditions of SLA-DG-06. Therefore, the claim is approved for a free replacement under SLA-DG-07.

**CF-104 · counterfactual · gpt-oss-120b · zero_shot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD timestamp (2026-08-01T11:20) to the first customer message (2026-08-01T19:05) is within 48 hours, satisfying SLA-DG-01, and SLA-DG-02 extends the window to 7 days because the PoD photo shows external damage. The claim includes a photo of the damaged lamp and the crushed box (CUSTOMER-002) meeting SLA-DG-04 and the required unboxing evidence for a high‑value order per SLA-DG-03. Since the PoD photo’s visible damage matches the customer’s description and photo, SLA-DG-06 mandates approval. The approved claim is resolved with a free replacement as per SLA-DG-07.

**CF-104 · counterfactual · qwen3.8-27b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD photo (POD-001) shows visible external damage (crushed corner, torn flap), which extends the reporting window to 7 days under SLA-DG-02. The customer reported the damage within 7.8 hours (CUSTOMER-001), well within the extended window. The customer's description and photo (CUSTOMER-002) are consistent with the external damage shown in the PoD, satisfying the conditions of SLA-DG-06. Therefore, the claim is approved for a free replacement as per SLA-DG-07.

**CF-105 · counterfactual · qwen3.8-27b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD photo (POD-001) shows visible external damage (crushed corner, torn flap), which extends the reporting window to 7 days under SLA-DG-02. The customer reported the damage within 7.8 hours (CUSTOMER-001) and provided a post-delivery photo (CUSTOMER-002) that is consistent with the external damage shown in the PoD. Under SLA-DG-06, the claim is approved without further evidence because the PoD shows damage and the customer's claim is consistent with it. The resolution is a free replacement as the default under SLA-DG-07.

**CF-106 · counterfactual · gpt-oss-120b · zero_shot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 14h35m after the PoD, within the 48‑hour window (SLA-DG-01). The PoD photo shows an undamaged package and no unboxing evidence is provided, so the claim shifts to agent discretion (SLA-DG-05). The claim also fails the minimum evidence requirement of SLA-DG-04 (no unboxing photo, no damage photo, and only a vague description). Because structured evidence (intact PoD, agent statement) conflicts with the customer's vague claim and there is insufficient proof of fault, SLA-DG-08 requires escalation to manual review.

**CF-106 · counterfactual · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported within the 48-hour window (SLA-DG-01) based on the PoD timestamp (POD-003) and the first customer message (CUSTOMER-005). The PoD photo (POD-003) shows an intact package, and the customer failed to provide the specific damage description or unboxing evidence required by SLA-DG-04. Under SLA-DG-05, the case shifts to agent discretion, but the lack of specific evidence and the conflict with the structured PoD record make the evidence insufficient to determine fault. Therefore, SLA-DG-08 requires the case to be escalated to manual review rather than auto-approved or rejected.

**CF-107 · counterfactual · gpt-oss-120b · zero_shot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD timestamp (2026-08-03T10:15) to the first customer message (2026-08-04T12:15) is 26 hours, within the 48‑hour SLA‑DG‑01 window. The PoD photo shows an undamaged package, so SLA‑DG‑02 does not extend the window. The claim includes a photo of the damaged glass carafe (CUSTOMER-004) satisfying SLA‑DG‑04(b). Because there is no unboxing evidence, SLA‑DG‑05 applies, shifting the decision to agent discretion; based on the credible damage photo and specific description, we exercise discretion to approve. Approved claims default to a free replacement per SLA‑DG‑07.

**COD-005 · pilot · gpt-oss-120b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported 14.8 hours after PoD, satisfying SLA-COD-01. The reconciliation log (RECON-005) matches the invoice amount, and under SLA-PRI-01 structured evidence prevails over the unverified photo. SLA-COD-03 therefore presumes rejection because the customer’s photo does not provide sufficient corroboration. Consequently the claim is rejected with no refund.

**COD-005 · pilot · gpt-oss-120b · facts · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported 14.8 hours after the PoD, within the 24‑hour window of SLA-COD-01, so it is eligible. The reconciliation log (RECON-005) records the collected amount as ₹3,200, matching the invoice, which triggers the presumptive rejection in SLA-COD-03. The customer’s photo (CUSTOMER-014) lacks verifiable metadata and does not meet the corroborating‑evidence requirement, so the presumption stands. Structured evidence (the log) therefore overrides the unstructured claim, leading to rejection.

**COD-005 · pilot · gpt-oss-120b · zero_shot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was filed 14h45m after the PoD, within the 24‑hour window (SLA-COD-01). The reconciliation log (RECON-005) records the collected amount as ₹3200, matching the order total, so under SLA-COD-03 the overcharge claim is presumptively rejected unless corroborating evidence disproves the log. The customer’s photo and chat lack verifiable metadata and do not outweigh the structured log, and SLA-PRI-01 gives priority to the log. Hence the claim is rejected.

**COD-005 · pilot · gpt-oss-20b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported 14.8 h after PoD, within the 24‑hour window of SLA‑COD‑01. Structured evidence (reconciliation log and agent statement) is reliable per SLA‑PRI‑01 and shows the amount collected matched the order total. The customer’s photo lacks verifiable metadata and does not rebut the structured evidence, so SLA‑COD‑03’s presumption of rejection applies. No refund is warranted.

**COD-005 · pilot · gpt-oss-20b · zero_shot · hybrid k=12** (REJECT, reference ESCALATE)

> The PoD timestamp is 2026-08-16T18:35:00+05:30 and the first customer message is 2026-08-17T09:20:00+05:30, a 14 h 45 m interval well within the 24‑hour reporting window of SLA‑COD‑01. SLA‑COD‑03 presumes rejection when the reconciliation log matches the order total unless the customer supplies corroborating evidence. The reconciliation log (RECON‑005) shows 3200 INR collected, matching the order total, and the agent statement (AGENT‑009) confirms the same. Structured evidence (reconciliation log and agent statement) takes priority over unstructured evidence per SLA‑PRI‑01, and there is no doubt about its validity. Therefore the claim is rejected.

**COD-005 · pilot · qwen3.8-27b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported within the 24-hour window (14.8 hours) as per SLA-COD-01. Under SLA-COD-03, the reconciliation log (RECON-005) matching the order total of ₹3,200 creates a presumption of rejection for the customer's overcharge claim. The customer's photo (CUSTOMER-014) is not considered valid corroborating evidence because it lacks verifiable metadata and a link to the specific delivery event. Per SLA-PRI-01, the structured reconciliation log takes priority over the unstructured customer narrative. Therefore, the claim is rejected as the customer failed to provide the necessary evidence to rebut the presumption.

**COD-005 · pilot · qwen3.8-27b · facts · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported 14.8 hours after the PoD timestamp, which is within the 24-hour eligibility window mandated by SLA-COD-01. The reconciliation log (RECON-005) records a remittance of ₹3,200, which exactly matches the order total, triggering the presumptive rejection under SLA-COD-03. The customer's provided photo (CUSTOMER-014) lacks verifiable capture metadata and does not link the currency notes to the specific handover event, failing to provide the corroborating evidence required to rebut the presumption. Under SLA-PRI-01, the structured reconciliation log takes priority over the unstructured customer narrative and unverifiable photo.

**COD-005 · pilot · qwen3.8-27b · zero_shot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim is eligible for review as it was reported within 24 hours of the Proof-of-Delivery timestamp (SLA-COD-01). The primary evidence source, the delivery partner's cash reconciliation log (RECON-005), records an amount of ₹3200, which matches the order total. Under SLA-COD-03, this match presumptively rejects the customer's claim of overcharge unless corroborating evidence is provided. The customer's photo (CUSTOMER-014) lacks verifiable metadata and does not show the transaction context, while the agent's statement (AGENT-009) is unstructured and conflicts with the structured reconciliation log; per SLA-PRI-01, the structured evidence takes priority in the absence of a documented reason to doubt the log.

**DG-002 · pilot · gpt-oss-20b · zero_shot · hybrid k=12** (ESCALATE, reference REJECT)

> The PoD timestamp is 2026-08-03T10:15:00+05:30 and the first customer message is 2026-08-06T09:30:00+05:30, a 3 days 23 hours 15 minutes interval, exceeding the 48‑hour eligibility window of SLA‑DG‑01. The PoD photo shows an intact package while the customer photo shows a chip on the glass rim, creating contradictory evidence that prevents a clear determination of fault. SLA‑DG‑08 mandates escalation to manual review in such cases, overriding the presumptive ineligibility. The claim also satisfies the evidence requirement of SLA‑DG‑04 (photo of damaged product) and the structured evidence (PoD) is prioritized per SLA‑PRI‑01.

**DG-002 · pilot · qwen3.8-27b · zero_shot · hybrid k=12** (ESCALATE, reference REJECT)

> The reporting window is calculated from the PoD timestamp (2026-08-03T10:15:00+05:30) to the first customer message (2026-08-06T09:30:00+05:30), which is approximately 72 hours and 15 minutes. This exceeds the 48-hour limit in SLA-DG-01, and SLA-DG-02 does not apply because the PoD photo (POD-002) shows an intact package. The customer provided a specific description and a photo of the damage (CUSTOMER-003, CUSTOMER-004), satisfying the evidence requirements of SLA-DG-04. However, because the PoD shows an intact package and no unboxing evidence was provided, SLA-DG-05 shifts the claim to agent discretion rather than auto-approval or auto-rejection. Since the SLA explicitly routes this scenario to discretion and the record does not settle the question of fault (intact external package vs. internal damage), the case must be escalated to manual review.

**DG-003 · pilot · gpt-oss-20b · zero_shot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD timestamp is 2026-08-05T18:40:00+05:30 and the first customer message is 2026-08-06T09:15:00+05:30, a 14 h 35 m interval well within the 48‑hour window of SLA‑DG‑01. The claim includes a specific written description satisfying SLA‑DG‑04. The PoD photo shows an intact package, so per SLA‑DG‑05 the case falls to agent discretion. No contradictory evidence exists, and the narrative is credible for a small appliance, so the claim is approved. Structured evidence (PoD) is not in doubt, so SLA‑PRI‑01 does not override the discretion clause.

**DG-004 · pilot · gpt-oss-120b · facts · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported 18.6 hours after PoD, within the 48‑hour window (SLA-DG-01). Because the order value is ₹7,499 (≥₹5,000), SLA-DG-03 mandates unboxing evidence, which the customer did not provide. The more specific high‑value requirement overrides the general discretion clause (SLA-DG-05) per SLA-PRI-03, so the claim fails the mandatory evidence condition and must be rejected.

**DG-004 · pilot · gpt-oss-120b · zero_shot · hybrid k=12** (REJECT, reference ESCALATE)

> The PoD timestamp (2026-08-08T15:50) to the first customer message (2026-08-09T10:25) is ~18.5 hours, within the 48‑hour window (SLA-DG-01). The PoD photo shows an intact package, and the customer provides a specific written description (SLA-DG-04). However, the order value is ₹7,499 (≥₹5,000), so SLA-DG-03 mandates unboxing evidence, which is absent. Without the required unboxing proof, the claim cannot be approved, leading to rejection.

