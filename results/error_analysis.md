# Error analysis and consistency

Generated from 23 saved run(s) in `results/runs/`. Confidence intervals are 95% Wilson intervals over all predictions pooled per configuration.

## Accuracy and stability by configuration

| Configuration | Runs | Accuracy (mean ± sd) | 95% CI | Escalation recall | Pairwise agreement |
|---|---|---|---|---|---|
| counterfactual · gpt-oss-120b · cot · hybrid k=12 | 1 | 81% ± 0% | 57%–93% | 75% | — |
| counterfactual · gpt-oss-120b · facts · hybrid k=12 | 1 | 81% ± 0% | 57%–93% | 75% | — |
| counterfactual · gpt-oss-120b · zero_shot · hybrid k=12 | 1 | 81% ± 0% | 57%–93% | 50% | — |
| counterfactual · gpt-oss-20b · cot · hybrid k=12 | 1 | 69% ± 0% | 44%–86% | 25% | — |
| counterfactual · gpt-oss-20b · facts · hybrid k=12 | 1 | 62% ± 0% | 39%–82% | 25% | — |
| counterfactual · gpt-oss-20b · zero_shot · hybrid k=12 | 1 | 75% ± 0% | 51%–90% | 25% | — |
| counterfactual · qwen3.8-27b · cot · hybrid k=12 | 1 | 69% ± 0% | 44%–86% | 50% | — |
| counterfactual · qwen3.8-27b · facts · hybrid k=12 | 1 | 94% ± 0% | 72%–99% | 100% | — |
| counterfactual · qwen3.8-27b · zero_shot · hybrid k=12 | 1 | 69% ± 0% | 44%–86% | 75% | — |
| counterfactual · rules engine | 1 | 100% ± 0% | 81%–100% | 100% | — |
| pilot · gpt-oss-120b · cot · hybrid k=12 | 4 | 82% ± 5% | 68%–91% | 42% | 95% |
| pilot · gpt-oss-120b · facts · hybrid k=12 | 1 | 80% ± 0% | 49%–94% | 33% | — |
| pilot · gpt-oss-120b · zero_shot · hybrid k=12 | 1 | 80% ± 0% | 49%–94% | 33% | — |
| pilot · gpt-oss-20b · cot · hybrid k=12 | 1 | 90% ± 0% | 60%–98% | 67% | — |
| pilot · gpt-oss-20b · facts · hybrid k=12 | 1 | 90% ± 0% | 60%–98% | 67% | — |
| pilot · gpt-oss-20b · zero_shot · hybrid k=12 | 1 | 70% ± 0% | 40%–89% | 33% | — |
| pilot · qwen3.8-27b · cot · hybrid k=12 | 1 | 90% ± 0% | 60%–98% | 67% | — |
| pilot · qwen3.8-27b · facts · hybrid k=12 | 1 | 90% ± 0% | 60%–98% | 67% | — |
| pilot · qwen3.8-27b · zero_shot · hybrid k=12 | 1 | 80% ± 0% | 49%–94% | 67% | — |
| pilot · rules engine | 1 | 100% ± 0% | 72%–100% | 100% | — |

Cases whose decision changed between repeats of the same configuration:

- **pilot · gpt-oss-120b · cot · hybrid k=12** · DG-004: ESCALATE×1, REJECT×3

## Disagreement guard (simulated)

If the LLM and the rules engine disagree, escalate to manual review. Simulated from the cross-check stored with every prediction — no new model calls. Caveat: the rules engine was written with the pilot cases visible, so pilot rows are in-sample; counterfactual rows are the fairer test.

| Configuration | n | Accuracy before → after | Escalation recall before → after | Escalated by guard | Errors fixed | Correct decisions sent to review |
|---|---|---|---|---|---|---|
| pilot · gpt-oss-20b · facts · hybrid k=12 | 10 | 90% → 100% | 67% → 100% | 1 | 1 | 0 |
| counterfactual · gpt-oss-20b · zero_shot · hybrid k=12 | 16 | 75% → 94% | 25% → 100% | 3 | 3 | 0 |
| pilot · gpt-oss-120b · cot · hybrid k=12 | 10 | 80% → 100% | 33% → 100% | 2 | 2 | 0 |
| counterfactual · gpt-oss-20b · facts · hybrid k=12 | 16 | 62% → 81% | 25% → 100% | 4 | 3 | 0 |
| pilot · gpt-oss-120b · cot · hybrid k=12 | 10 | 80% → 100% | 33% → 100% | 2 | 2 | 0 |
| counterfactual · gpt-oss-20b · cot · hybrid k=12 | 16 | 69% → 88% | 25% → 100% | 4 | 3 | 0 |
| pilot · gpt-oss-120b · cot · hybrid k=12 | 10 | 80% → 100% | 33% → 100% | 2 | 2 | 0 |
| counterfactual · qwen3.8-27b · zero_shot · hybrid k=12 | 16 | 69% → 75% | 75% → 100% | 2 | 1 | 0 |
| counterfactual · gpt-oss-120b · facts · hybrid k=12 | 16 | 81% → 88% | 75% → 100% | 2 | 1 | 0 |
| counterfactual · qwen3.8-27b · facts · hybrid k=12 | 16 | 94% → 94% | 100% → 100% | 0 | 0 | 0 |
| counterfactual · gpt-oss-120b · cot · hybrid k=12 | 16 | 81% → 88% | 75% → 100% | 2 | 1 | 0 |
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
| 0.50 | 264 | 79% → 79% | 0 | 0 | 0 |
| 0.60 | 264 | 79% → 79% | 0 | 0 | 0 |
| 0.70 | 264 | 79% → 79% | 0 | 0 | 0 |
| 0.80 | 264 | 79% → 80% | 4 | 3 | 1 |
| 0.90 | 264 | 79% → 81% | 22 | 13 | 8 |
| 0.95 | 264 | 79% → 78% | 38 | 17 | 19 |

## Error taxonomy

| Error kind | Count | Share |
|---|---|---|
| Forced a decision where the reference escalates | 34 | 62% |
| Escalated where the reference decides | 15 | 27% |
| Approved where the reference rejects, or the reverse | 6 | 11% |

The rules-engine cross-check reached the reference decision on **55 of 55** LLM errors — the share a disagreement flag would have routed to review.

Cases most often wrong: COD-005 (11), CF-106 (9), CF-104 (8), DG-004 (5), CF-107 (4), CF-110 (4)

## Every error

| Case | Configuration | Kind | Predicted → Reference | Cited primary | Reference clauses | Missed decisive evidence | Conf. | Rules engine |
|---|---|---|---|---|---|---|---|---|
| CF-101 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-01 | — | 0.95 | REJECT |
| CF-101 | counterfactual · qwen3.8-27b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-01 | — | 0.95 | REJECT |
| CF-103 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | polarity | APPROVE → REJECT | SLA-DG-06 | SLA-DG-01, SLA-DG-02 | — | 0.85 | REJECT |
| CF-103 | counterfactual · qwen3.8-27b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-01 | SLA-DG-01, SLA-DG-02 | — | 0.95 | REJECT |
| CF-104 | counterfactual · gpt-oss-120b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.96 | ESCALATE |
| CF-104 | counterfactual · gpt-oss-120b · facts · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.96 | ESCALATE |
| CF-104 | counterfactual · gpt-oss-120b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.96 | ESCALATE |
| CF-104 | counterfactual · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.85 | ESCALATE |
| CF-104 | counterfactual · gpt-oss-20b · facts · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.95 | ESCALATE |
| CF-104 | counterfactual · gpt-oss-20b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.95 | ESCALATE |
| CF-104 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.95 | ESCALATE |
| CF-104 | counterfactual · qwen3.8-27b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.95 | ESCALATE |
| CF-105 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09 | DELIVERY-901 | 0.95 | ESCALATE |
| CF-106 | counterfactual · gpt-oss-120b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04 | — | 0.95 | REJECT |
| CF-106 | counterfactual · gpt-oss-120b · facts · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04 | — | 0.92 | REJECT |
| CF-106 | counterfactual · gpt-oss-120b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04 | — | 0.95 | REJECT |
| CF-106 | counterfactual · gpt-oss-20b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04 | — | 0.85 | REJECT |
| CF-106 | counterfactual · gpt-oss-20b · facts · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04 | — | 0.85 | REJECT |
| CF-106 | counterfactual · gpt-oss-20b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04 | — | 0.85 | REJECT |
| CF-106 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04 | — | 0.95 | REJECT |
| CF-106 | counterfactual · qwen3.8-27b · facts · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-04 | — | 0.95 | REJECT |
| CF-106 | counterfactual · qwen3.8-27b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-04 | — | 0.95 | REJECT |
| CF-107 | counterfactual · gpt-oss-120b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | — | 0.78 | ESCALATE |
| CF-107 | counterfactual · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | — | 0.85 | ESCALATE |
| CF-107 | counterfactual · gpt-oss-20b · facts · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | — | 0.80 | ESCALATE |
| CF-107 | counterfactual · gpt-oss-20b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | — | 0.80 | ESCALATE |
| CF-109 | counterfactual · qwen3.8-27b · zero_shot · hybrid k=12 | polarity | APPROVE → REJECT | SLA-COD-04 | SLA-COD-01 | — | 0.95 | REJECT |
| CF-110 | counterfactual · gpt-oss-120b · cot · hybrid k=12 | polarity | APPROVE → REJECT | SLA-COD-04 | SLA-COD-07 | — | 0.93 | REJECT |
| CF-110 | counterfactual · gpt-oss-120b · facts · hybrid k=12 | polarity | APPROVE → REJECT | SLA-COD-04 | SLA-COD-07 | — | 0.96 | REJECT |
| CF-110 | counterfactual · gpt-oss-20b · cot · hybrid k=12 | polarity | APPROVE → REJECT | SLA-COD-04 | SLA-COD-07 | — | 0.95 | REJECT |
| CF-110 | counterfactual · gpt-oss-20b · facts · hybrid k=12 | polarity | APPROVE → REJECT | SLA-COD-04 | SLA-COD-07 | — | 0.95 | REJECT |
| CF-114 | counterfactual · gpt-oss-20b · facts · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-COD-09 | SLA-COD-03 | — | 0.85 | REJECT |
| CF-116 | counterfactual · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | AGENT-004 | 0.85 | ESCALATE |
| CF-116 | counterfactual · gpt-oss-20b · facts · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | — | 0.85 | ESCALATE |
| CF-116 | counterfactual · gpt-oss-20b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | AGENT-004 | 0.85 | ESCALATE |
| COD-005 | pilot · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | AGENT-009 | 0.96 | ESCALATE |
| COD-005 | pilot · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | AGENT-009 | 0.96 | ESCALATE |
| COD-005 | pilot · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | — | 0.94 | ESCALATE |
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
| DG-003 | pilot · gpt-oss-20b · facts · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-04 | SLA-DG-05, SLA-DG-08 | AGENT-003 | 0.75 | ESCALATE |
| DG-003 | pilot · gpt-oss-20b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | — | 0.75 | ESCALATE |
| DG-004 | pilot · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-DG-03 | SLA-DG-03, SLA-DG-05, SLA-DG-08 | AGENT-004 | 0.86 | ESCALATE |
| DG-004 | pilot · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-DG-03 | SLA-DG-03, SLA-DG-05, SLA-DG-08 | — | 0.92 | ESCALATE |
| DG-004 | pilot · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-DG-03 | SLA-DG-03, SLA-DG-05, SLA-DG-08 | — | 0.93 | ESCALATE |
| DG-004 | pilot · gpt-oss-120b · facts · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-DG-03 | SLA-DG-03, SLA-DG-05, SLA-DG-08 | AGENT-004 | 0.92 | ESCALATE |
| DG-004 | pilot · gpt-oss-120b · zero_shot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-DG-03 | SLA-DG-03, SLA-DG-05, SLA-DG-08 | — | 0.85 | ESCALATE |

## Model rationales for the errors

**CF-101 · counterfactual · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 60 hours after delivery, missing the 48-hour window in SLA-DG-01, and the PoD photo (POD-003) shows an intact package, so the SLA-DG-02 extension does not apply. Under SLA-DG-05, when the PoD shows an intact package and no unboxing evidence is provided, the claim shifts to agent discretion. The customer's specific description (CUSTOMER-005) satisfies SLA-DG-04, but the conflict between the intact PoD (POD-003) and the reported internal damage requires manual review to determine fault.

**CF-101 · counterfactual · qwen3.8-27b · zero_shot · hybrid k=12** (ESCALATE, reference REJECT)

> The reporting window is calculated from the PoD timestamp (2026-08-05T18:40:00+05:30) to the first customer message (2026-08-08T06:40:00+05:30), which is approximately 60 hours. This exceeds the 48-hour limit in SLA-DG-01, but the claim remains eligible for review because the PoD photo (POD-003) shows an intact package, failing the condition for the 7-day extension in SLA-DG-02. The customer provided a specific written description of the damage (satisfying SLA-DG-04(c)) but explicitly stated they did not record an unboxing video. Since the PoD photo shows the package intact and no unboxing evidence is provided, SLA-DG-05 applies, shifting the claim to agent discretion rather than auto-approval or auto-rejection. As the adjudicator must exercise discretion based on narrative credibility and product category, and the evidence does not automatically settle the question of fault, the case is escalated to manual review.

**CF-103 · counterfactual · qwen3.8-27b · cot · hybrid k=12** (APPROVE, reference REJECT)

> The PoD photo (POD-001) shows visible external damage (crushed corner, torn flap), which extends the reporting window to 7 days under SLA-DG-02. Although the customer reported the issue at 200 hours (exceeding the 168-hour window), the SLA does not provide an automatic rejection for late reporting when the 7-day exception is triggered by visible pre-existing damage. The customer's photo (CUSTOMER-002) and description (CUSTOMER-001) are consistent with the external damage shown in the PoD, satisfying the conditions of SLA-DG-06. Therefore, the claim is approved for a free replacement under SLA-DG-07.

**CF-103 · counterfactual · qwen3.8-27b · zero_shot · hybrid k=12** (ESCALATE, reference REJECT)

> The PoD timestamp is 2026-08-01T11:20:00+05:30 and the first customer message is 2026-08-09T19:20:00+05:30, resulting in a reporting interval of 8 days and 8 hours. Although the PoD photo (POD-001) shows visible external damage (crushed corner, torn flap) which triggers the 7-day extension under SLA-DG-02, the claim was filed after this extended window, making it presumptively ineligible under SLA-DG-01. While the customer provided sufficient evidence of damage (CUSTOMER-002) consistent with the PoD (SLA-DG-06), the strict failure of the reporting window prevents an automatic approval. Because the SLA does not provide an automatic exception for late claims with strong evidence, and the agent's statement (AGENT-001) does not resolve the timing discrepancy, the case is escalated to agent discretion.

**CF-104 · counterfactual · gpt-oss-120b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim is within the 7‑day window extended by SLA-DG-02 as PoD shows package damage; PoD is reliable per SLA-PRI-01; the customer provided required unboxing evidence (photo) satisfying SLA-DG-03 and SLA-DG-04; SLA-DG-06 then auto‑approves the claim because the PoD damage matches the customer's photo; thus a free replacement is granted per SLA-DG-07.

**CF-104 · counterfactual · gpt-oss-120b · facts · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD timestamp is 01 Aug 2026 11:20 IST and the first customer report arrived at 01 Aug 2026 19:05 IST (7.8 h), within the 7‑day window extended by SLA-DG-02 because the PoD photo shows visible external damage. SLA-DG-06 applies as the PoD damage matches the customer's description and photo, mandating approval without further evidence. Although SLA-DG-03 normally requires unboxing evidence for high‑value orders, SLA-DG-06 is more specific and overrides that requirement per SLA-PRI-03. The claim also satisfies SLA-DG-04 with a post‑delivery damage photo and specific description.

**CF-104 · counterfactual · gpt-oss-120b · zero_shot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD timestamp (2026-08-01T11:20) to the first customer message (2026-08-01T19:05) is within 48 hours, satisfying SLA-DG-01, and SLA-DG-02 extends the window to 7 days because the PoD photo shows external damage. The claim includes a photo of the damaged lamp and the crushed box (CUSTOMER-002) meeting SLA-DG-04 and the required unboxing evidence for a high‑value order per SLA-DG-03. Since the PoD photo’s visible damage matches the customer’s description and photo, SLA-DG-06 mandates approval. The approved claim is resolved with a free replacement as per SLA-DG-07.

**CF-104 · counterfactual · gpt-oss-20b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> Reporting window is 7 days per SLA-DG-02 because the PoD photo (POD-001) shows visible external damage and the customer reported within 7.8 hours. The governing clause is SLA-DG-06, which overrides the high‑value unboxing requirement (SLA-DG-03) because it is more specific. The PoD photo and the customer’s post‑delivery photo (CUSTOMER-002) are consistent with the package damage, satisfying SLA-DG-06. Therefore the claim is approved and the default resolution is a free replacement per SLA-DG-07.

**CF-104 · counterfactual · gpt-oss-20b · facts · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD photo (POD-001) shows visible external damage (crushed corner, torn flap). The customer’s post‑delivery photo (CUSTOMER-002) depicts a crack consistent with that damage. SLA‑DG‑06 states that when PoD shows external damage and the customer’s evidence is consistent, the claim is approved without further evidence. The claim was reported 7.8 h after PoD, well within the 48‑hour window (SLA‑DG‑01) and the 7‑day extension (SLA‑DG‑02). Although SLA‑DG‑03 requires unboxing evidence for high‑value orders, SLA‑DG‑06 is a more specific clause and overrides the general requirement. Thus the claim is approved.

**CF-104 · counterfactual · gpt-oss-20b · zero_shot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD timestamp is 2026-08-01T11:20:00+05:30 and the first customer message is 2026-08-01T19:05:00+05:30, a 7 h 45 m interval well within the 48‑hour reporting window (SLA‑DG‑01). The order value ₹6200 qualifies as high‑value, so unboxing evidence is required (SLA‑DG‑03); the customer photo (CUSTOMER‑002) shows the package and product condition at delivery, satisfying SLA‑DEF‑05. The PoD photo (POD‑001) shows visible external damage, and the customer’s claim/photo is consistent with that damage, triggering automatic approval under SLA‑DG‑06. Structured evidence (PoD and photo) takes priority over narrative (SLA‑PRI‑01).

**CF-104 · counterfactual · qwen3.8-27b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD photo (POD-001) shows visible external damage (crushed corner, torn flap), which extends the reporting window to 7 days under SLA-DG-02. The customer reported the damage within 7.8 hours (CUSTOMER-001), well within the extended window. The customer's description and photo (CUSTOMER-002) are consistent with the external damage shown in the PoD, satisfying the conditions of SLA-DG-06. Therefore, the claim is approved for a free replacement as per SLA-DG-07.

**CF-104 · counterfactual · qwen3.8-27b · zero_shot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD timestamp is 2026-08-01T11:20:00+05:30 and the first customer message is 2026-08-01T19:05:00+05:30, an interval of 7 hours 45 minutes, which is within the 48-hour window of SLA-DG-01. The PoD photo (POD-001) clearly shows visible external package damage (crushed corner and torn flap), satisfying the condition for SLA-DG-02 and SLA-DG-06. The customer's photo (CUSTOMER-002) and description (CUSTOMER-001) show a cracked ceramic base consistent with the external crush damage, and the photo serves as unboxing evidence under SLA-DEF-05, satisfying the high-value item requirement of SLA-DG-03. Under SLA-DG-06, the claim is approved without further evidence. The resolution is a free replacement as the default under SLA-DG-07.

**CF-105 · counterfactual · qwen3.8-27b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD photo (POD-001) shows visible external damage (crushed corner, torn flap), which extends the reporting window to 7 days under SLA-DG-02. The customer reported the damage within 7.8 hours (CUSTOMER-001) and provided a post-delivery photo (CUSTOMER-002) that is consistent with the external damage shown in the PoD. Under SLA-DG-06, the claim is approved without further evidence because the PoD shows damage and the customer's claim is consistent with it. The resolution is a free replacement as the default under SLA-DG-07.

**CF-106 · counterfactual · gpt-oss-120b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported within the 48‑hour window (SLA-DG-01). Structured PoD and delivery logs are reliable (SLA-PRI-01). The customer provided no unboxing evidence nor a specific damage description, failing SLA-DG-04. PoD and agent statements show the package intact, moving the claim to agent discretion per SLA-DG-05, but the evidence remains contradictory and insufficient, so SLA-DG-08 requires escalation to manual review.

**CF-106 · counterfactual · gpt-oss-120b · facts · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 14.6 hours after the PoD, satisfying the 48‑hour window of SLA‑DG‑01. However, SLA‑DG‑04 requires unboxing evidence, a post‑delivery damage photo, or a specific written description, none of which are present; the customer description is not specific and no photos were provided. With the PoD showing an intact package (SLA‑DG‑05) and insufficient evidence, SLA‑DG‑08 mandates escalation to manual review.

**CF-106 · counterfactual · gpt-oss-120b · zero_shot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 14h35m after the PoD, within the 48‑hour window (SLA-DG-01). The PoD photo shows an undamaged package and no unboxing evidence is provided, so the claim shifts to agent discretion (SLA-DG-05). The claim also fails the minimum evidence requirement of SLA-DG-04 (no unboxing photo, no damage photo, and only a vague description). Because structured evidence (intact PoD, agent statement) conflicts with the customer's vague claim and there is insufficient proof of fault, SLA-DG-08 requires escalation to manual review.

**CF-106 · counterfactual · gpt-oss-20b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 14.6 h after PoD, within the 48‑hour window (SLA‑DG‑01). The PoD record is clear and trustworthy (SLA‑PRI‑01). However, the claim lacks required evidence: no unboxing photo, no photo of the damaged product, and the description is not specific (SLA‑DG‑04). With an intact PoD photo and no unboxing evidence, the claim falls to agent discretion (SLA‑DG‑05). Because the evidence is insufficient to determine fault, the SLA mandates escalation to manual review (SLA‑DG‑08).

**CF-106 · counterfactual · gpt-oss-20b · facts · hybrid k=12** (ESCALATE, reference REJECT)

> The PoD timestamp is 2026-08-05 18:40 IST and the first customer message is 2026-08-06 09:15 IST, a 14.6‑hour interval well within the 48‑hour window of SLA‑DG‑01, so the claim is eligible. However, SLA‑DG‑04 requires at least one of unboxing evidence, a post‑delivery photo of the damaged product, or a specific written description; the customer’s message is generic and no unboxing or damage photo is provided. With the PoD photo showing an intact package (SLA‑DG‑05) and no unboxing evidence, the case falls under “insufficient evidence” per SLA‑DG‑08, which mandates escalation to manual review. Thus the claim cannot be auto‑approved or auto‑rejected.

**CF-106 · counterfactual · gpt-oss-20b · zero_shot · hybrid k=12** (ESCALATE, reference REJECT)

> The PoD timestamp is 2026-08-05T18:40:00+05:30 and the first customer message is 2026-08-06T09:15:00+05:30, a 14 h 35 min interval, within the 48‑hour reporting window of SLA‑DG‑01. The PoD photo (POD‑003) shows an intact package with no visible external damage, so SLA‑DG‑02 does not extend the window. The claim lacks unboxing evidence, a photo of the damaged product, and a specific written description, violating SLA‑DG‑04. The customer’s narrative conflicts with the structured PoD evidence, and the agent statement confirms the package was in good condition. According to SLA‑DG‑08, contradictory or insufficient evidence warrants escalation to manual review rather than an automatic decision.

**CF-106 · counterfactual · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported within the 48-hour window (SLA-DG-01) based on the PoD timestamp (POD-003) and the first customer message (CUSTOMER-005). The PoD photo (POD-003) shows an intact package, and the customer failed to provide the specific damage description or unboxing evidence required by SLA-DG-04. Under SLA-DG-05, the case shifts to agent discretion, but the lack of specific evidence and the conflict with the structured PoD record make the evidence insufficient to determine fault. Therefore, SLA-DG-08 requires the case to be escalated to manual review rather than auto-approved or rejected.

**CF-106 · counterfactual · qwen3.8-27b · facts · hybrid k=12** (ESCALATE, reference REJECT)

> The claim is within the 48-hour reporting window (14.6 hours from PoD to first message), satisfying SLA-DG-01. However, the PoD photo (POD-003) clearly shows an intact package, and the customer provided no unboxing evidence or specific damage description, failing the requirements of SLA-DG-04. Under SLA-DG-05, when the PoD shows an intact package and no unboxing evidence is provided, the claim shifts to agent discretion rather than being auto-approved or auto-rejected. Because the customer's narrative is generic ('item is damaged') and contradicted by the structured PoD evidence, the case is escalated to manual review per SLA-DG-08 to allow an agent to assess credibility and product category.

**CF-106 · counterfactual · qwen3.8-27b · zero_shot · hybrid k=12** (ESCALATE, reference REJECT)

> The reporting window is satisfied as the first customer message (2026-08-06T09:15:00+05:30) occurred within 48 hours of the PoD timestamp (2026-08-05T18:40:00+05:30). The PoD photo (POD-003) shows the package intact and undamaged, and the customer provided no unboxing evidence or specific description of the damage, failing the requirements of SLA-DG-04. Under SLA-DG-05, this specific combination of an intact PoD and lack of unboxing evidence shifts the claim to agent discretion rather than auto-approval or auto-rejection. Because the record does not settle the question of fault and the evidence is insufficient to determine whether the damage occurred in transit or after delivery, SLA-DG-08 mandates escalation to manual review.

**CF-107 · counterfactual · gpt-oss-120b · zero_shot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD timestamp (2026-08-03T10:15) to the first customer message (2026-08-04T12:15) is 26 hours, within the 48‑hour SLA‑DG‑01 window. The PoD photo shows an undamaged package, so SLA‑DG‑02 does not extend the window. The claim includes a photo of the damaged glass carafe (CUSTOMER-004) satisfying SLA‑DG‑04(b). Because there is no unboxing evidence, SLA‑DG‑05 applies, shifting the decision to agent discretion; based on the credible damage photo and specific description, we exercise discretion to approve. Approved claims default to a free replacement per SLA‑DG‑07.

**CF-107 · counterfactual · gpt-oss-20b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was filed 26 h after PoD, within the 48‑hour window (SLA‑DG‑01). The PoD photo is clear and shows an intact package, so structured evidence is reliable (SLA‑PRI‑01). The customer provided a post‑delivery photo of the damaged carafe rim (SLA‑DG‑04), satisfying the evidence requirement. Because the PoD shows no external damage and no unboxing evidence, the claim falls under agent discretion (SLA‑DG‑05), which we approve based on the credible narrative and photo. The approved claim is resolved with a free replacement (SLA‑DG‑07).

**CF-107 · counterfactual · gpt-oss-20b · facts · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was filed 26 h after the PoD timestamp, within the 48‑hour reporting window (SLA‑DG‑01). The PoD photo shows an intact package, and the customer supplied a post‑delivery photo of the damaged glass carafe (SLA‑DG‑04). Because the PoD photo is intact and no unboxing evidence was provided, SLA‑DG‑05 shifts the case to agent discretion. Structured evidence (PoD) does not conflict with the narrative, so SLA‑PRI‑01 does not override the discretion. The evidence supports a credible claim of in‑transit damage, so the claim is approved under agent discretion.

**CF-107 · counterfactual · gpt-oss-20b · zero_shot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD timestamp is 2026-08-03T10:15:00+05:30 and the first customer message is 2026-08-04T12:15:00+05:30, a 26‑hour interval well within the 48‑hour eligibility window of SLA‑DG‑01. The PoD photo shows an intact package, and the customer supplied a photo of the damaged glass rim (SLA‑DG‑04). Because the PoD shows no external damage and no unboxing evidence is provided, SLA‑DG‑05 shifts the claim to agent discretion, but the evidence is sufficient and not contradictory, so the claim is approved. Structured evidence (PoD) is not in doubt, satisfying SLA‑PRI‑01. The default resolution for an approved damaged‑goods claim is a free replacement (SLA‑DG‑07).

**CF-109 · counterfactual · qwen3.8-27b · zero_shot · hybrid k=12** (APPROVE, reference REJECT)

> The claim is eligible for review as it was reported within 24 hours of the Proof-of-Delivery timestamp (2026-08-13T15:35:00+05:30 to 2026-08-14T21:35:00+05:30 is approximately 30 hours, but the SLA-COD-01 window is 24 hours; however, the reconciliation log is the primary evidence). The reconciliation log (RECON-001) shows an amount of ₹1700 collected, which is higher than the order total of ₹1500. Under SLA-COD-04, this corroborates the customer's overcharge claim, and the excess amount (₹1700 - ₹1500 = ₹200) must be refunded. The discrepancy exceeds the ₹10 threshold in SLA-COD-07, so it is eligible for formal resolution.

**CF-110 · counterfactual · gpt-oss-120b · cot · hybrid k=12** (APPROVE, reference REJECT)

> The claim was filed 4.6 hours after delivery, satisfying SLA-COD-01's 24‑hour window. The reconciliation log is structured evidence and, per SLA-PRI-01, takes precedence over the agent's unstructured statement. The log records a collection of ₹1505, which is higher than the invoice amount of ₹1500, triggering SLA-COD-04. That clause mandates refund of the excess amount, calculated as ₹1505‑₹1500 = ₹5. Hence the refund is approved.

**CF-110 · counterfactual · gpt-oss-120b · facts · hybrid k=12** (APPROVE, reference REJECT)

> The claim was reported 4.6 hours after the PoD, within the 24‑hour window of SLA‑COD‑01, making it eligible. The reconciliation log (RECON-001) records ₹1505 collected, which is higher than the invoice total ₹1500, triggering SLA‑COD‑04 that mandates refund of the excess ₹5. Structured reconciliation evidence overrides the conflicting agent statement per SLA‑PRI‑01, and no reason exists to doubt the log. Hence the overcharge is confirmed and refunded.

**CF-110 · counterfactual · gpt-oss-20b · cot · hybrid k=12** (APPROVE, reference REJECT)

> The claim was reported 4.6 h after PoD, within the 24‑hour window of SLA‑COD‑01. The reconciliation log is recorded and reliable per SLA‑PRI‑01. The log shows a higher amount (₹1,505) than the invoice (₹1,500), satisfying SLA‑COD‑04, which mandates a refund of the excess ₹5.00. Thus the claim is approved and the refund is issued.

**CF-110 · counterfactual · gpt-oss-20b · facts · hybrid k=12** (APPROVE, reference REJECT)

> The claim was reported 4.6 h after PoD, within the 24‑hour window of SLA‑COD‑01, making it eligible. The reconciliation log (RECON‑001) records ₹1,505, higher than the invoice ₹1,500, satisfying SLA‑COD‑04’s condition for an overcharge. SLA‑COD‑03 confirms the reconciliation log is the primary evidence source, and no corroborating evidence is required when the log shows a higher amount. Thus the excess ₹5 should be refunded.

**CF-114 · counterfactual · gpt-oss-20b · facts · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 15.4 h after PoD, within the 24‑hour window of SLA‑COD‑01, making it eligible. The reconciliation log (RECON‑003) and agent statement (AGENT‑008) both record ₹1,800, matching the order total, which per SLA‑COD‑03 presumptively rejects the claim unless corroborating evidence is provided. However, SLA‑COD‑09 overrides this by stating that if at least two independent sources confirm the correct amount and the claim is knowingly false, the case must be escalated for account‑level review. The evidence satisfies this fraud condition, so the appropriate outcome is escalation rather than a simple reject.

**CF-116 · counterfactual · gpt-oss-20b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was filed 18.6 hours after delivery, within the 48‑hour window of SLA‑DG‑01. Structured PoD evidence is trustworthy (SLA‑PRI‑01). The customer’s specific description meets the evidence requirement of SLA‑DG‑04. Because the PoD shows an intact package and no unboxing evidence is provided, SLA‑DG‑05 applies, giving agent discretion to approve based on narrative credibility. The claim is therefore approved and resolved with a free replacement under SLA‑DG‑07.

**CF-116 · counterfactual · gpt-oss-20b · facts · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was filed 18.6 h after PoD, within the 48‑hour window (SLA‑DG‑01). The PoD photo shows an intact package (SLA‑DEF‑01) and no unboxing evidence was provided, so the case falls under SLA‑DG‑05, which routes it to agent discretion. The customer’s written description is specific enough to satisfy the evidence requirement of SLA‑DG‑04. Structured evidence (PoD) does not conflict with the narrative, so SLA‑PRI‑01 does not override the discretionary approval. Therefore the claim is approved and resolved via free replacement per SLA‑DG‑07.

**CF-116 · counterfactual · gpt-oss-20b · zero_shot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was filed 18h35m after the PoD timestamp, well within the 48‑hour window of SLA‑DG‑01. PoD photo shows an intact package, and the customer supplied a specific written description of the internal damage, satisfying the evidence requirement of SLA‑DG‑04. Because the PoD shows no external damage and no unboxing evidence is provided, SLA‑DG‑05 applies, moving the case to agent discretion. Given the product is electronics (high‑fragility) and the narrative is credible, the claim is approved for a free replacement.

**COD-005 · pilot · gpt-oss-120b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported 14.8 hours after PoD, satisfying SLA-COD-01's 24‑hour window. Structured evidence (reconciliation log RECON-005) matches the invoice amount, and SLA-PRI-01 gives it priority over unstructured evidence. Since the log matches, SLA-COD-03 presumes rejection unless the customer provides corroborating evidence; the photo lacks verifiable metadata, so the presumption stands. Therefore the claim is rejected with no customer action required.

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

**DG-003 · pilot · gpt-oss-20b · facts · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was filed 14.6 h after PoD, well within the 48‑hour window of SLA‑DG‑01. The customer’s chat provides a specific written description of the damage, satisfying SLA‑DG‑04’s evidence requirement. PoD photo shows an intact package, so SLA‑DG‑05 applies, moving the case to agent discretion; the narrative credibility and product category (small appliance) support approval. No clause mandates rejection, and the evidence is not contradictory, so the claim is approved for replacement.

**DG-003 · pilot · gpt-oss-20b · zero_shot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD timestamp is 2026-08-05T18:40:00+05:30 and the first customer message is 2026-08-06T09:15:00+05:30, a 14 h 35 m interval well within the 48‑hour window of SLA‑DG‑01. The claim includes a specific written description satisfying SLA‑DG‑04. The PoD photo shows an intact package, so per SLA‑DG‑05 the case falls to agent discretion. No contradictory evidence exists, and the narrative is credible for a small appliance, so the claim is approved. Structured evidence (PoD) is not in doubt, so SLA‑PRI‑01 does not override the discretion clause.

**DG-004 · pilot · gpt-oss-120b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported 18.6 hours after delivery, within the 48‑hour window (SLA-DG-01). PoD data is reliable (SLA-PRI-01). Although the customer gave a specific written description satisfying SLA-DG-04, the order value exceeds ₹5,000, invoking SLA-DG-03 which mandates unboxing evidence; none was provided. As the more specific clause is unmet, the claim must be rejected.

**DG-004 · pilot · gpt-oss-120b · facts · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported 18.6 hours after PoD, within the 48‑hour window (SLA-DG-01). Because the order value is ₹7,499 (≥₹5,000), SLA-DG-03 mandates unboxing evidence, which the customer did not provide. The more specific high‑value requirement overrides the general discretion clause (SLA-DG-05) per SLA-PRI-03, so the claim fails the mandatory evidence condition and must be rejected.

**DG-004 · pilot · gpt-oss-120b · zero_shot · hybrid k=12** (REJECT, reference ESCALATE)

> The PoD timestamp (2026-08-08T15:50) to the first customer message (2026-08-09T10:25) is ~18.5 hours, within the 48‑hour window (SLA-DG-01). The PoD photo shows an intact package, and the customer provides a specific written description (SLA-DG-04). However, the order value is ₹7,499 (≥₹5,000), so SLA-DG-03 mandates unboxing evidence, which is absent. Without the required unboxing proof, the claim cannot be approved, leading to rejection.

