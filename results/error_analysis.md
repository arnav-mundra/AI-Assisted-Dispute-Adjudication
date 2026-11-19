# Error analysis and consistency

Generated from 32 saved run(s) in `results/runs/`. Confidence intervals are 95% Wilson intervals over all predictions pooled per configuration.

## Accuracy and stability by configuration

| Configuration | Runs | Accuracy (mean ± sd) | 95% CI | Escalation recall | Pairwise agreement |
|---|---|---|---|---|---|
| counterfactual · gpt-oss-120b · cot · hybrid k=12 | 1 | 81% ± 0% | 57%–93% | 75% | — |
| counterfactual · gpt-oss-120b · cot · hybrid k=29 | 1 | 75% ± 0% | 51%–90% | 50% | — |
| counterfactual · gpt-oss-120b · facts · hybrid k=12 | 1 | 81% ± 0% | 57%–93% | 75% | — |
| counterfactual · gpt-oss-120b · zero_shot · hybrid k=12 | 1 | 81% ± 0% | 57%–93% | 50% | — |
| counterfactual · gpt-oss-20b · cot · hybrid k=12 | 1 | 69% ± 0% | 44%–86% | 25% | — |
| counterfactual · gpt-oss-20b · facts · hybrid k=12 | 1 | 62% ± 0% | 39%–82% | 25% | — |
| counterfactual · gpt-oss-20b · zero_shot · hybrid k=12 | 1 | 75% ± 0% | 51%–90% | 25% | — |
| counterfactual · qwen3.8-27b · cot · hybrid k=12 | 1 | 69% ± 0% | 44%–86% | 50% | — |
| counterfactual · qwen3.8-27b · facts · hybrid k=12 | 1 | 94% ± 0% | 72%–99% | 100% | — |
| counterfactual · qwen3.8-27b · zero_shot · hybrid k=12 | 1 | 69% ± 0% | 44%–86% | 75% | — |
| counterfactual · rules engine | 1 | 100% ± 0% | 81%–100% | 100% | — |
| heldout · gpt-oss-120b · cot · hybrid k=12 | 1 | 71% ± 0% | 54%–83% | 29% | — |
| heldout · gpt-oss-120b · facts · hybrid k=12 | 1 | 65% ± 0% | 48%–79% | 29% | — |
| heldout · gpt-oss-20b · cot · hybrid k=12 | 1 | 59% ± 0% | 42%–74% | 0% | — |
| heldout · qwen3.8-27b · cot · hybrid k=12 | 1 | 62% ± 0% | 45%–76% | 43% | — |
| heldout · qwen3.8-27b · facts · hybrid k=12 | 1 | 79% ± 0% | 63%–90% | 71% | — |
| heldout · qwen3.8-27b · zero_shot · hybrid k=12 | 1 | 68% ± 0% | 51%–81% | 71% | — |
| heldout · rules engine | 1 | 59% ± 0% | 42%–74% | 43% | — |
| pilot · gpt-oss-120b · cot · hybrid k=12 | 4 | 82% ± 5% | 68%–91% | 42% | 95% |
| pilot · gpt-oss-120b · cot · hybrid k=29 | 1 | 90% ± 0% | 60%–98% | 67% | — |
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
| heldout · gpt-oss-120b · facts · hybrid k=12 | 34 | 65% → 56% | 29% → 57% | 9 | 2 | 5 |
| heldout · qwen3.8-27b · zero_shot · hybrid k=12 | 34 | 68% → 53% | 71% → 71% | 7 | 0 | 5 |
| heldout · qwen3.8-27b · facts · hybrid k=12 | 34 | 79% → 65% | 71% → 71% | 5 | 0 | 5 |
| counterfactual · gpt-oss-120b · cot · hybrid k=29 | 16 | 75% → 88% | 50% → 100% | 3 | 2 | 0 |
| pilot · gpt-oss-120b · cot · hybrid k=29 | 10 | 90% → 100% | 67% → 100% | 1 | 1 | 0 |
| heldout · gpt-oss-20b · cot · hybrid k=12 | 34 | 59% → 56% | 0% → 43% | 10 | 3 | 4 |
| heldout · gpt-oss-120b · cot · hybrid k=12 | 34 | 71% → 59% | 29% → 43% | 8 | 1 | 5 |
| heldout · qwen3.8-27b · cot · hybrid k=12 | 34 | 62% → 47% | 43% → 43% | 7 | 0 | 5 |
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
| 0.50 | 494 | 74% → 74% | 0 | 0 | 0 |
| 0.60 | 494 | 74% → 74% | 0 | 0 | 0 |
| 0.70 | 494 | 74% → 74% | 0 | 0 | 0 |
| 0.80 | 494 | 74% → 74% | 5 | 3 | 2 |
| 0.90 | 494 | 74% → 75% | 35 | 16 | 14 |
| 0.95 | 494 | 74% → 73% | 63 | 24 | 32 |

## Error taxonomy

| Error kind | Count | Share |
|---|---|---|
| Forced a decision where the reference escalates | 66 | 47% |
| Escalated where the reference decides | 50 | 35% |
| Approved where the reference rejects, or the reverse | 25 | 18% |

The rules-engine cross-check reached the reference decision on **77 of 127** LLM errors — the share a disagreement flag would have routed to review.

Cases most often wrong: COD-005 (12), CF-106 (10), CF-104 (9), HO-005 (7), HO-024 (7), HO-028 (7)

## Every error

| Case | Configuration | Kind | Predicted → Reference | Cited primary | Reference clauses | Missed decisive evidence | Conf. | Rules engine |
|---|---|---|---|---|---|---|---|---|
| CF-101 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-01 | — | 0.95 | REJECT |
| CF-101 | counterfactual · qwen3.8-27b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-01 | — | 0.95 | REJECT |
| CF-103 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | polarity | APPROVE → REJECT | SLA-DG-06 | SLA-DG-01, SLA-DG-02 | — | 0.85 | REJECT |
| CF-103 | counterfactual · qwen3.8-27b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-01 | SLA-DG-01, SLA-DG-02 | — | 0.95 | REJECT |
| CF-104 | counterfactual · gpt-oss-120b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.96 | ESCALATE |
| CF-104 | counterfactual · gpt-oss-120b · cot · hybrid k=29 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.93 | ESCALATE |
| CF-104 | counterfactual · gpt-oss-120b · facts · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.96 | ESCALATE |
| CF-104 | counterfactual · gpt-oss-120b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.96 | ESCALATE |
| CF-104 | counterfactual · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.85 | ESCALATE |
| CF-104 | counterfactual · gpt-oss-20b · facts · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.95 | ESCALATE |
| CF-104 | counterfactual · gpt-oss-20b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.95 | ESCALATE |
| CF-104 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.95 | ESCALATE |
| CF-104 | counterfactual · qwen3.8-27b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-03 | — | 0.95 | ESCALATE |
| CF-105 | counterfactual · qwen3.8-27b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09 | DELIVERY-901 | 0.95 | ESCALATE |
| CF-106 | counterfactual · gpt-oss-120b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04 | — | 0.95 | REJECT |
| CF-106 | counterfactual · gpt-oss-120b · cot · hybrid k=29 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04 | — | 0.92 | REJECT |
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
| CF-110 | counterfactual · gpt-oss-120b · cot · hybrid k=29 | polarity | APPROVE → REJECT | SLA-COD-04 | SLA-COD-07 | — | 0.96 | REJECT |
| CF-110 | counterfactual · gpt-oss-120b · facts · hybrid k=12 | polarity | APPROVE → REJECT | SLA-COD-04 | SLA-COD-07 | — | 0.96 | REJECT |
| CF-110 | counterfactual · gpt-oss-20b · cot · hybrid k=12 | polarity | APPROVE → REJECT | SLA-COD-04 | SLA-COD-07 | — | 0.95 | REJECT |
| CF-110 | counterfactual · gpt-oss-20b · facts · hybrid k=12 | polarity | APPROVE → REJECT | SLA-COD-04 | SLA-COD-07 | — | 0.95 | REJECT |
| CF-114 | counterfactual · gpt-oss-20b · facts · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-COD-09 | SLA-COD-03 | — | 0.85 | REJECT |
| CF-116 | counterfactual · gpt-oss-120b · cot · hybrid k=29 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | — | 0.86 | ESCALATE |
| CF-116 | counterfactual · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | AGENT-004 | 0.85 | ESCALATE |
| CF-116 | counterfactual · gpt-oss-20b · facts · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | — | 0.85 | ESCALATE |
| CF-116 | counterfactual · gpt-oss-20b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | AGENT-004 | 0.85 | ESCALATE |
| COD-005 | pilot · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | AGENT-009 | 0.96 | ESCALATE |
| COD-005 | pilot · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | AGENT-009 | 0.96 | ESCALATE |
| COD-005 | pilot · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | — | 0.94 | ESCALATE |
| COD-005 | pilot · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | — | 0.96 | ESCALATE |
| COD-005 | pilot · gpt-oss-120b · cot · hybrid k=29 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-COD-09, SLA-PRI-01, SLA-PRI-02 | AGENT-009 | 0.93 | ESCALATE |
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
| HO-002 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-DG-08 | SLA-DG-02, SLA-DG-06 | CUSTOMER-402 | 0.72 | — |
| HO-003 | heldout · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-01 | — | 0.95 | REJECT |
| HO-003 | heldout · qwen3.8-27b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-01 | — | 0.95 | REJECT |
| HO-004 | heldout · qwen3.8-27b · cot · hybrid k=12 | polarity | APPROVE → REJECT | SLA-DG-06 | SLA-DG-01, SLA-DG-02 | — | 0.95 | REJECT |
| HO-004 | heldout · qwen3.8-27b · zero_shot · hybrid k=12 | polarity | APPROVE → REJECT | SLA-DG-06 | SLA-DG-01, SLA-DG-02 | — | 0.95 | REJECT |
| HO-005 | heldout · gpt-oss-120b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04, SLA-DG-05 | — | 0.92 | ESCALATE |
| HO-005 | heldout · gpt-oss-120b · facts · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04, SLA-DG-05 | — | 0.92 | ESCALATE |
| HO-005 | heldout · gpt-oss-20b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04, SLA-DG-05 | — | 0.78 | ESCALATE |
| HO-005 | heldout · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04, SLA-DG-05 | — | 0.95 | ESCALATE |
| HO-005 | heldout · qwen3.8-27b · facts · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-04, SLA-DG-05 | — | 0.95 | ESCALATE |
| HO-005 | heldout · qwen3.8-27b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-04, SLA-DG-05 | — | 0.95 | ESCALATE |
| HO-005 | heldout · rules engine | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04, SLA-DG-05 | — | 0.72 | — |
| HO-006 | heldout · gpt-oss-120b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-406 | 0.96 | APPROVE |
| HO-006 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-406 | 0.95 | APPROVE |
| HO-006 | heldout · qwen3.8-27b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-406 | 0.95 | APPROVE |
| HO-006 | heldout · rules engine | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-406 | 0.92 | — |
| HO-007 | heldout · gpt-oss-120b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-407 | 0.97 | APPROVE |
| HO-007 | heldout · gpt-oss-120b · facts · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-407 | 0.96 | APPROVE |
| HO-007 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-407 | 0.95 | APPROVE |
| HO-007 | heldout · qwen3.8-27b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-407 | 0.95 | APPROVE |
| HO-007 | heldout · rules engine | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-407 | 0.92 | — |
| HO-010 | heldout · gpt-oss-120b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-DG-03 | SLA-DG-03, SLA-DEF-05, SLA-DG-06 | — | 0.92 | ESCALATE |
| HO-010 | heldout · gpt-oss-20b · cot · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-DG-03 | SLA-DG-03, SLA-DEF-05, SLA-DG-06 | — | 0.70 | ESCALATE |
| HO-010 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-DG-03 | SLA-DG-03, SLA-DEF-05, SLA-DG-06 | CUSTOMER-410, DELIVERY-310 | 0.70 | — |
| HO-012 | heldout · gpt-oss-120b · facts · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-05 | SLA-DG-05, SLA-DG-08 | — | 0.92 | ESCALATE |
| HO-012 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-04 | SLA-DG-05, SLA-DG-08 | — | 0.85 | ESCALATE |
| HO-013 | heldout · gpt-oss-120b · facts · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-DG-08 | SLA-DG-01, SLA-DG-04, SLA-PRI-01 | — | 0.85 | ESCALATE |
| HO-013 | heldout · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-DG-08 | SLA-DG-01, SLA-DG-04, SLA-PRI-01 | AGENT-313 | 0.95 | ESCALATE |
| HO-013 | heldout · qwen3.8-27b · facts · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-DG-08 | SLA-DG-01, SLA-DG-04, SLA-PRI-01 | — | 0.95 | ESCALATE |
| HO-013 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-DG-08 | SLA-DG-01, SLA-DG-04, SLA-PRI-01 | AGENT-313, CUSTOMER-413, DELIVERY-313 | 0.72 | — |
| HO-014 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-04 | SLA-DG-04, SLA-DG-08, SLA-PRI-01 | AGENT-314 | 0.85 | ESCALATE |
| HO-015 | heldout · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-01 | — | 0.95 | REJECT |
| HO-015 | heldout · qwen3.8-27b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-01 | — | 0.95 | REJECT |
| HO-016 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-DG-08 | SLA-DG-01, SLA-DG-06 | CUSTOMER-416 | 0.72 | — |
| HO-017 | heldout · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-01, SLA-DG-02 | AGENT-317 | 0.95 | REJECT |
| HO-017 | heldout · qwen3.8-27b · zero_shot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-01, SLA-DG-02 | — | 0.95 | REJECT |
| HO-019 | heldout · gpt-oss-20b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-COD-09 | SLA-COD-03 | — | 0.95 | REJECT |
| HO-021 | heldout · gpt-oss-120b · facts · hybrid k=12 | polarity | APPROVE → REJECT | SLA-COD-04 | SLA-COD-07, SLA-COD-04 | AGENT-321 | 0.85 | REJECT |
| HO-022 | heldout · gpt-oss-20b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-07 | SLA-COD-06, SLA-COD-07 | AGENT-322 | 0.85 | ESCALATE |
| HO-022 | heldout · qwen3.8-27b · zero_shot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-07 | SLA-COD-06, SLA-COD-07 | AGENT-322 | 0.95 | ESCALATE |
| HO-022 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-COD-06 | SLA-COD-06, SLA-COD-07 | AGENT-322 | 0.60 | — |
| HO-023 | heldout · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | — | 0.96 | ESCALATE |
| HO-023 | heldout · gpt-oss-120b · facts · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | CUSTOMER-423 | 0.96 | ESCALATE |
| HO-023 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | — | 0.95 | ESCALATE |
| HO-024 | heldout · gpt-oss-120b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-05 | SLA-COD-01, SLA-DEF-03, SLA-COD-05 | — | 0.96 | REJECT |
| HO-024 | heldout · gpt-oss-120b · facts · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-05 | SLA-COD-01, SLA-DEF-03, SLA-COD-05 | — | 0.96 | REJECT |
| HO-024 | heldout · gpt-oss-20b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-05 | SLA-COD-01, SLA-DEF-03, SLA-COD-05 | — | 0.95 | REJECT |
| HO-024 | heldout · qwen3.8-27b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-05 | SLA-COD-01, SLA-DEF-03, SLA-COD-05 | AGENT-324 | 0.95 | REJECT |
| HO-024 | heldout · qwen3.8-27b · facts · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-05 | SLA-COD-01, SLA-DEF-03, SLA-COD-05 | — | 0.95 | REJECT |
| HO-024 | heldout · qwen3.8-27b · zero_shot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-05 | SLA-COD-01, SLA-DEF-03, SLA-COD-05 | — | 0.95 | REJECT |
| HO-024 | heldout · rules engine | polarity | REJECT → APPROVE | SLA-COD-05 | SLA-COD-01, SLA-DEF-03, SLA-COD-05 | — | 0.85 | — |
| HO-026 | heldout · gpt-oss-120b · facts · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-COD-09 | SLA-COD-02, SLA-COD-03 | CUSTOMER-426 | 0.86 | REJECT |
| HO-028 | heldout · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-09, SLA-COD-03 | AGENT-328, CUSTOMER-328 | 0.96 | REJECT |
| HO-028 | heldout · gpt-oss-120b · facts · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-09, SLA-COD-03 | CUSTOMER-328 | 0.96 | REJECT |
| HO-028 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-09, SLA-COD-03 | AGENT-328, DELIVERY-428 | 0.95 | REJECT |
| HO-028 | heldout · qwen3.8-27b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-09, SLA-COD-03 | AGENT-328, CUSTOMER-328 | 0.95 | REJECT |
| HO-028 | heldout · qwen3.8-27b · facts · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-09, SLA-COD-03 | — | 0.95 | REJECT |
| HO-028 | heldout · qwen3.8-27b · zero_shot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-09, SLA-COD-03 | — | 0.95 | REJECT |
| HO-028 | heldout · rules engine | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-09, SLA-COD-03 | AGENT-328, DELIVERY-428 | 0.85 | — |
| HO-030 | heldout · gpt-oss-120b · cot · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-COD-08, SLA-PRI-01 | — | 0.78 | ESCALATE |
| HO-030 | heldout · gpt-oss-120b · facts · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-COD-08, SLA-PRI-01 | — | 0.78 | ESCALATE |
| HO-030 | heldout · gpt-oss-20b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-COD-08, SLA-PRI-01 | — | 0.85 | ESCALATE |
| HO-030 | heldout · qwen3.8-27b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-04 | SLA-COD-03, SLA-COD-08, SLA-PRI-01 | — | 0.95 | ESCALATE |
| HO-030 | heldout · qwen3.8-27b · facts · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-COD-08, SLA-PRI-01 | — | 0.95 | ESCALATE |
| HO-030 | heldout · qwen3.8-27b · zero_shot · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-COD-08, SLA-PRI-01 | — | 0.95 | ESCALATE |
| HO-030 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-COD-08, SLA-PRI-01 | — | 0.62 | — |
| HO-032 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-COD-06 | SLA-COD-06 | AGENT-332 | 0.60 | — |
| HO-033 | heldout · gpt-oss-120b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-COD-06 | SLA-COD-06, SLA-COD-09 | AGENT-333, CUSTOMER-333 | 0.96 | APPROVE |
| HO-033 | heldout · gpt-oss-120b · facts · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-COD-06 | SLA-COD-06, SLA-COD-09 | AGENT-333, CUSTOMER-333 | 0.97 | APPROVE |
| HO-033 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-COD-06 | SLA-COD-06, SLA-COD-09 | — | 0.92 | APPROVE |
| HO-033 | heldout · qwen3.8-27b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-COD-06 | SLA-COD-06, SLA-COD-09 | AGENT-333, CUSTOMER-333 | 0.95 | APPROVE |
| HO-033 | heldout · qwen3.8-27b · facts · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-COD-06 | SLA-COD-06, SLA-COD-09 | AGENT-333, CUSTOMER-333 | 0.95 | APPROVE |
| HO-033 | heldout · qwen3.8-27b · zero_shot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-COD-06 | SLA-COD-06, SLA-COD-09 | AGENT-333, CUSTOMER-333 | 0.95 | APPROVE |
| HO-033 | heldout · rules engine | missed escalation | APPROVE → ESCALATE | SLA-COD-06 | SLA-COD-06, SLA-COD-09 | AGENT-333 | 0.85 | — |
| HO-034 | heldout · gpt-oss-120b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-PRI-01 | SLA-COD-03, SLA-PRI-01 | DELIVERY-334 | 0.88 | ESCALATE |
| HO-034 | heldout · gpt-oss-120b · facts · hybrid k=12 | polarity | REJECT → APPROVE | SLA-PRI-01 | SLA-COD-03, SLA-PRI-01 | DELIVERY-334 | 0.96 | ESCALATE |
| HO-034 | heldout · gpt-oss-20b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | DELIVERY-334 | 0.95 | ESCALATE |
| HO-034 | heldout · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | DELIVERY-334 | 0.95 | ESCALATE |
| HO-034 | heldout · qwen3.8-27b · facts · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | DELIVERY-334 | 0.95 | ESCALATE |
| HO-034 | heldout · qwen3.8-27b · zero_shot · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | DELIVERY-334 | 0.95 | ESCALATE |
| HO-034 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | DELIVERY-334 | 0.62 | — |

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

**CF-104 · counterfactual · gpt-oss-120b · cot · hybrid k=29** (APPROVE, reference ESCALATE)

> The claim was filed 7.8 hours after the PoD, well within the 7‑day window extended by SLA-DG-02. The PoD photo clearly shows external box damage and the customer’s photo (CUSTOMER-002) depicts the same damage and a cracked lamp, meeting SLA-DG-06 which requires approval without further evidence. Accordingly the claim is approved and resolved via the default free replacement per SLA-DG-07.

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

**CF-106 · counterfactual · gpt-oss-120b · cot · hybrid k=29** (ESCALATE, reference REJECT)

> The claim was filed 14.6 hours after delivery, meeting the 48‑hour window of SLA‑DG‑01. The PoD record is clear and unchallenged, satisfying SLA‑PRI‑01. However, the claim fails SLA‑DG‑04 because the customer provided neither unboxing evidence nor a specific damage description. With the PoD showing an intact package and no corroborating evidence, SLA‑DG‑08 mandates escalation due to insufficient evidence. Accordingly the case is escalated for manual review.

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

**CF-110 · counterfactual · gpt-oss-120b · cot · hybrid k=29** (APPROVE, reference REJECT)

> The claim was reported 4.6 hours after the PoD, meeting the 24‑hour window of SLA-COD-01. The reconciliation log (RECON-001) is structured evidence and, per SLA-PRI-01, overrides the conflicting agent statement. It records a collection amount of ₹1505, which is higher than the invoice total of ₹1500, triggering SLA-COD-04. Accordingly, the excess ₹5 must be refunded. No reason exists to doubt the log, so the refund is approved.

**CF-110 · counterfactual · gpt-oss-120b · facts · hybrid k=12** (APPROVE, reference REJECT)

> The claim was reported 4.6 hours after the PoD, within the 24‑hour window of SLA‑COD‑01, making it eligible. The reconciliation log (RECON-001) records ₹1505 collected, which is higher than the invoice total ₹1500, triggering SLA‑COD‑04 that mandates refund of the excess ₹5. Structured reconciliation evidence overrides the conflicting agent statement per SLA‑PRI‑01, and no reason exists to doubt the log. Hence the overcharge is confirmed and refunded.

**CF-110 · counterfactual · gpt-oss-20b · cot · hybrid k=12** (APPROVE, reference REJECT)

> The claim was reported 4.6 h after PoD, within the 24‑hour window of SLA‑COD‑01. The reconciliation log is recorded and reliable per SLA‑PRI‑01. The log shows a higher amount (₹1,505) than the invoice (₹1,500), satisfying SLA‑COD‑04, which mandates a refund of the excess ₹5.00. Thus the claim is approved and the refund is issued.

**CF-110 · counterfactual · gpt-oss-20b · facts · hybrid k=12** (APPROVE, reference REJECT)

> The claim was reported 4.6 h after PoD, within the 24‑hour window of SLA‑COD‑01, making it eligible. The reconciliation log (RECON‑001) records ₹1,505, higher than the invoice ₹1,500, satisfying SLA‑COD‑04’s condition for an overcharge. SLA‑COD‑03 confirms the reconciliation log is the primary evidence source, and no corroborating evidence is required when the log shows a higher amount. Thus the excess ₹5 should be refunded.

**CF-114 · counterfactual · gpt-oss-20b · facts · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 15.4 h after PoD, within the 24‑hour window of SLA‑COD‑01, making it eligible. The reconciliation log (RECON‑003) and agent statement (AGENT‑008) both record ₹1,800, matching the order total, which per SLA‑COD‑03 presumptively rejects the claim unless corroborating evidence is provided. However, SLA‑COD‑09 overrides this by stating that if at least two independent sources confirm the correct amount and the claim is knowingly false, the case must be escalated for account‑level review. The evidence satisfies this fraud condition, so the appropriate outcome is escalation rather than a simple reject.

**CF-116 · counterfactual · gpt-oss-120b · cot · hybrid k=29** (APPROVE, reference ESCALATE)

> The claim was filed 18.6 hours after PoD, within the 48‑hour window (SLA-DG-01). Structured PoD evidence is reliable with no doubt (SLA-PRI-01). The customer's specific written description meets the evidence requirement (SLA-DG-04). Because the PoD shows an intact package and no unboxing evidence, the claim shifts to agent discretion (SLA-DG-05); given the credible narrative and fragile electronics, we approve a free replacement per SLA-DG-07.

**CF-116 · counterfactual · gpt-oss-20b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was filed 18.6 hours after delivery, within the 48‑hour window of SLA‑DG‑01. Structured PoD evidence is trustworthy (SLA‑PRI‑01). The customer’s specific description meets the evidence requirement of SLA‑DG‑04. Because the PoD shows an intact package and no unboxing evidence is provided, SLA‑DG‑05 applies, giving agent discretion to approve based on narrative credibility. The claim is therefore approved and resolved with a free replacement under SLA‑DG‑07.

**CF-116 · counterfactual · gpt-oss-20b · facts · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was filed 18.6 h after PoD, within the 48‑hour window (SLA‑DG‑01). The PoD photo shows an intact package (SLA‑DEF‑01) and no unboxing evidence was provided, so the case falls under SLA‑DG‑05, which routes it to agent discretion. The customer’s written description is specific enough to satisfy the evidence requirement of SLA‑DG‑04. Structured evidence (PoD) does not conflict with the narrative, so SLA‑PRI‑01 does not override the discretionary approval. Therefore the claim is approved and resolved via free replacement per SLA‑DG‑07.

**CF-116 · counterfactual · gpt-oss-20b · zero_shot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was filed 18h35m after the PoD timestamp, well within the 48‑hour window of SLA‑DG‑01. PoD photo shows an intact package, and the customer supplied a specific written description of the internal damage, satisfying the evidence requirement of SLA‑DG‑04. Because the PoD shows no external damage and no unboxing evidence is provided, SLA‑DG‑05 applies, moving the case to agent discretion. Given the product is electronics (high‑fragility) and the narrative is credible, the claim is approved for a free replacement.

**COD-005 · pilot · gpt-oss-120b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported 14.8 hours after PoD, satisfying SLA-COD-01's 24‑hour window. Structured evidence (reconciliation log RECON-005) matches the invoice amount, and SLA-PRI-01 gives it priority over unstructured evidence. Since the log matches, SLA-COD-03 presumes rejection unless the customer provides corroborating evidence; the photo lacks verifiable metadata, so the presumption stands. Therefore the claim is rejected with no customer action required.

**COD-005 · pilot · gpt-oss-120b · cot · hybrid k=29** (REJECT, reference ESCALATE)

> The claim was filed 14.8 hours after PoD, satisfying SLA-COD-01's 24‑hour window. The reconciliation log (RECON-005) records the exact COD amount of ₹3,200, matching the invoice, and there is no system‑failure flag, so structured evidence prevails under SLA-PRI-01. The customer's photo does not provide verifiable proof of a higher amount collected. Accordingly SLA-COD-03 mandates a presumptive rejection of the overcharge claim. The case is therefore rejected with no refund.

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

**HO-002 · heldout · rules engine** (ESCALATE, reference APPROVE)

> The claim was reported within the window (151.7 h). The PoD photo cannot be relied on and nothing independently corroborates transit damage and there is no unboxing evidence, so SLA-DG-05 removes auto-approval. The customer's description is specific and plausible, so fault cannot be determined from the record: under SLA-DG-08 the case is escalated to manual review.

**HO-003 · heldout · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 90.4 hours after delivery, exceeding the 48-hour window in SLA-DG-01. The PoD photo (POD-303) shows an intact package, and the customer provided no unboxing evidence, triggering the agent discretion clause SLA-DG-05. Although the customer provided a specific damage description and photo (CUSTOMER-303, CUSTOMER-403) satisfying SLA-DG-04, the SLA does not provide an automatic outcome for this scenario. The case is escalated to manual review to determine if the damage is attributable to the customer or the delivery process.

**HO-003 · heldout · qwen3.8-27b · zero_shot · hybrid k=12** (ESCALATE, reference REJECT)

> The PoD timestamp is 2026-09-24T17:50:00+05:30 and the first customer message is 2026-09-28T12:15:00+05:30, resulting in a reporting interval of approximately 91.5 hours. This exceeds the 48-hour window in SLA-DG-01, but SLA-DG-02 extends the window to 7 days if the PoD photo shows visible external damage. The PoD photo (POD-303) shows the package intact with no visible external damage, so the 7-day extension does not apply, making the claim presumptively ineligible. However, the customer provided a specific description and photo of the damage (CUSTOMER-303, CUSTOMER-403) satisfying SLA-DG-04, while the agent statement (AGENT-303) confirms the parcel was fine at handover. Under SLA-DG-05, when the PoD shows an intact package and no unboxing evidence is provided, the claim shifts to agent discretion. SLA-DG-08 explicitly mandates escalation to manual review when evidence is contradictory or insufficient to determine fault, which applies here given the conflict between the intact PoD and the customer's damage claim without unboxing video.

**HO-004 · heldout · qwen3.8-27b · cot · hybrid k=12** (APPROVE, reference REJECT)

> The PoD photo (POD-304) shows visible external damage, which extends the reporting window to 7 days under SLA-DG-02. Although the customer reported the issue at 199.8 hours (exceeding the 168-hour window), the claim is still eligible for review because the SLA-DG-02 exception applies to the nature of the damage. The customer provided a specific description (CUSTOMER-304) and a post-delivery photo (CUSTOMER-404) that are consistent with the external damage shown in the PoD, satisfying SLA-DG-06. Under SLA-DG-06, the claim is approved without further evidence. The resolution is a free replacement as per SLA-DG-07.

**HO-004 · heldout · qwen3.8-27b · zero_shot · hybrid k=12** (APPROVE, reference REJECT)

> The PoD photo (POD-304) clearly shows visible external package damage (crushed corner, torn flap), which triggers the 7-day reporting window extension under SLA-DG-02. The customer reported the issue on 2026-10-03, which is 8 days after the PoD timestamp of 2026-09-25, falling within the extended window. The customer's photo (CUSTOMER-404) and description (CUSTOMER-304) of a crack near the base are consistent with the external damage shown in the PoD and corroborated by the delivery log (DELIVERY-304). Under SLA-DG-06, when the PoD shows visible external damage and the customer's claim is consistent with it, the claim is approved without further evidence. The resolution is a free replacement as the default outcome under SLA-DG-07.

**HO-005 · heldout · gpt-oss-120b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was filed 7.4 hours after delivery, within the 48‑hour window (SLA-DG-01). Structured PoD evidence is reliable (SLA-PRI-01). The customer provided no unboxing or post‑delivery photos and the description lacks specific damage details, so SLA-DG-04 is not satisfied. With an intact PoD photo and no unboxing evidence, the case moves to agent discretion per SLA-DG-05, but the evidence remains insufficient to decide fault, invoking SLA-DG-08 to escalate for manual review.

**HO-005 · heldout · gpt-oss-120b · facts · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 7.4 hours after the PoD (14:05 to 21:30), satisfying the 48‑hour window (SLA-DG-01). However, the customer provided no unboxing photo/video, no post‑delivery damage photo, and the narrative lacks a specific description of damage location, failing SLA-DG-04. With the PoD showing an intact package, the case falls to agent discretion per SLA-DG-05, but the evidence is insufficient to determine fault, triggering SLA-DG-08 to escalate for manual review.

**HO-005 · heldout · gpt-oss-20b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was filed 7.4 h after PoD, within the 48‑hour window (SLA‑DG‑01). The PoD record is clear and untainted (SLA‑PRI‑01). The customer’s narrative lacks a specific damage location, so the required evidence per SLA‑DG‑04 is missing. With PoD intact and no unboxing evidence, the claim falls under SLA‑DG‑05, leaving the outcome to agent discretion. Because the evidence is insufficient to determine fault, SLA‑DG‑08 mandates escalation to manual review.

**HO-005 · heldout · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported within the 48-hour window (SLA-DG-01) and the PoD photo (POD-305) is reliable (SLA-PRI-01). However, the PoD shows an intact package and the customer provided no unboxing or post-delIVERY photographic proof (CUSTOMER-305, CUSTOMER-405). The narrative is too vague to satisfy the specificity requirement of SLA-04. As the evidence is contradictory (intact PoD vs. damage claim) and insufficient to determine fault, SLA-DG-08 mandates escalation to manual review.

**HO-005 · heldout · qwen3.8-27b · facts · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 7.4 hours after the PoD timestamp, which is within the 48-hour eligibility window under SLA-DG-01. The PoD photo (POD-305) clearly shows the package as intact and undamaged, and the customer has not provided any unboxing evidence or post-delivery photos as required by SLA-DG-04. Under SLA-DG-05, when the PoD shows an intact package and no unboxing evidence is provided, the claim shifts to agent discretion rather than being auto-approved or auto-rejected. Because the customer's narrative is generic ('damaged', 'bad quality') and lacks the specific details required to establish fault or damage location, the case is escalated to manual review for an agent to evaluate narrative credibility and product category.

**HO-005 · heldout · qwen3.8-27b · zero_shot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported within the 48-hour window (PoD at 14:05 IST on 2026-09-26, first customer message at 21:30 IST on 2026-09-26, interval ~7.4 hours). The PoD photo (POD-305) shows the package intact and undamaged, and the customer provided no unboxing evidence or specific description of the damage, failing the requirements of SLA-DG-04. Under SLA-DG-05, when the PoD shows an intact package and no unboxing evidence is provided, the claim shifts to agent discretion rather than being auto-approved or auto-rejected. Because the SLA explicitly routes this scenario to discretion and the record does not settle the question of fault (intact external packaging vs. vague internal damage claim), the case must be escalated to manual review.

**HO-005 · heldout · rules engine** (ESCALATE, reference REJECT)

> The claim was reported within the window (7.4 h). The PoD shows the package intact at handover and there is no unboxing evidence, so SLA-DG-05 removes auto-approval. The customer's description is specific and plausible, so fault cannot be determined from the record: under SLA-DG-08 the case is escalated to manual review.

**HO-006 · heldout · gpt-oss-120b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD photo shows external damage, extending the reporting window to 7 days per SLA-DG-02; the customer reported within 6.3 hours, satisfying eligibility. No reason to doubt the PoD per SLA-PRI-01. The claim includes a post‑delivery photo and specific damage description, meeting SLA-DG-04. Because the PoD damage matches the customer's evidence, SLA-DG-06 mandates approval. The default resolution is a free replacement per SLA-DG-07.

**HO-006 · heldout · gpt-oss-20b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was reported 6.3 h after PoD, well within the 7‑day window granted by SLA‑DG‑02 because the PoD photo shows external damage. The PoD record is clear and trustworthy per SLA‑PRI‑01. The customer supplied a post‑delivery photo of the cracked bulbs, satisfying SLA‑DG‑04. SLA‑DG‑06 therefore triggers automatic approval as the PoD damage matches the customer’s claim. The default resolution per SLA‑DG‑07 is a free replacement.

**HO-006 · heldout · qwen3.8-27b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD photo (POD-306) shows visible external damage (crushed top, split seam), which extends the reporting window to 7 days under SLA-DG-02. The customer reported the issue within 6.3 hours (CUSTOMER-306) and provided a post-delivery photo (CUSTOMER-406) that is consistent with the PoD evidence. Under SLA-DG-06, when the PoD shows visible damage and the customer's claim is consistent, the claim is approved without further evidence. The resolution is a free replacement as the default under SLA-DG-07.

**HO-006 · heldout · rules engine** (APPROVE, reference ESCALATE)

> The claim was reported 6.3 h after delivery, within the window. The PoD photo itself shows visible external package damage, and the customer's description and photo of the product damage are consistent with it. Under SLA-DG-06 the claim is approved without further evidence; the default remedy under SLA-DG-07 is a free replacement.

**HO-007 · heldout · gpt-oss-120b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was reported 3.4 hours after delivery, satisfying the 48‑hour window and the 7‑day exception (SLA-DG-01, SLA-DG-02). Structured evidence is reliable (SLA-PRI-01). The customer provided a post‑delivery damage photo and a specific description, meeting SLA-DG-04. Because the PoD shows visible external damage and the customer's evidence matches it, SLA-DG-06 mandates approval. Accordingly, the claim is approved for a free replacement per SLA-DG-07.

**HO-007 · heldout · gpt-oss-120b · facts · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was reported 3.4 hours after PoD, within the 7‑day window granted by SLA-DG-02 because the PoD photo shows external damage. SLA-DG-04 is satisfied by the customer’s specific description and post‑delivery photo. SLA-DG-06 applies as the PoD damage matches the customer’s damage evidence, mandating approval. Accordingly, the claim is approved and resolved with a free replacement per SLA-DG-07.

**HO-007 · heldout · gpt-oss-20b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was filed 3.4 hours after PoD, well within the 7‑day window granted by SLA‑DG‑02 because the PoD photo shows external damage. Structured PoD evidence is trustworthy per SLA‑PRI‑01. The customer supplied a post‑delivery photo of the damaged bottle (CUSTOMER‑407), meeting the evidence requirement of SLA‑DG‑04. SLA‑DG‑06 therefore mandates approval without further evidence. The approved claim is resolved via free replacement per SLA‑DG‑07.

**HO-007 · heldout · qwen3.8-27b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD photo (POD-307) shows visible external damage to the package, which extends the reporting window to 7 days under SLA-DG-02. The customer reported the issue within 3.4 hours of delivery, well within this window. The customer's specific description (CUSTOMER-307) and photo (CUSTOMER-407) are consistent with the damage shown in the PoD, satisfying SLA-DG-06 for automatic approval. The resolution is a free replacement as per the default in SLA-DG-07.

**HO-007 · heldout · rules engine** (APPROVE, reference ESCALATE)

> The claim was reported 3.4 h after delivery, within the window. The PoD photo itself shows visible external package damage, and the customer's description and photo of the product damage are consistent with it. Under SLA-DG-06 the claim is approved without further evidence; the default remedy under SLA-DG-07 is a free replacement.

**HO-010 · heldout · gpt-oss-120b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was filed within the 7‑day window per SLA-DG-02, and structured PoD evidence is reliable (SLA-PRI-01). While SLA-DG-04 is satisfied by the post‑delivery photo and detailed description, SLA-DG-03 requires unboxing evidence for orders ≥₹5,000, which is missing, making the claim ineligible. Hence the claim is rejected with no standard resolution.

**HO-010 · heldout · gpt-oss-20b · cot · hybrid k=12** (ESCALATE, reference APPROVE)

> The PoD photo shows external damage, extending the reporting window to 7 days (SLA-DG-02). Structured evidence is reliable (SLA-PRI-01). The order is high‑value, so unboxing evidence is required (SLA-DG-03) and is missing. However, SLA‑DG‑06 states that visible external damage with consistent customer photo warrants approval. The two clauses conflict; the SLA does not provide a clear automatic outcome, so the case is escalated for manual review.

**HO-010 · heldout · rules engine** (ESCALATE, reference APPROVE)

> The claim was reported within the window (6.6 h). The order value of ₹14,500 meets the SLA-DG-03 high-value threshold, which requires unboxing evidence, and none was provided. The requirement is unmet but the narrative is specific, so the record cannot settle fault either way: under SLA-DG-08 the case goes to manual review rather than being auto-approved or auto-rejected.

**HO-012 · heldout · gpt-oss-120b · facts · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was reported 13.7 hours after the PoD (within the 48‑hour window of SLA‑DG‑01), making it eligible. The PoD photo shows an intact package and no unboxing evidence was provided, invoking SLA‑DG‑05 which shifts the case to agent discretion. The customer supplied a specific damage description and a post‑delivery photo, satisfying SLA‑DG‑04's evidence requirement. Given the credible narrative and fragile product category, we approve the claim and apply the default free replacement per SLA‑DG‑07.

**HO-012 · heldout · gpt-oss-20b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was reported 13.7 h after PoD, within the 48‑hour window of SLA‑DG‑01. The PoD photo is clear and reliable per SLA‑PRI‑01. The customer’s post‑delivery photo (CUSTOMER‑412) satisfies the evidence requirement of SLA‑DG‑04, providing a specific description of the damage. Thus the claim meets the eligibility criteria and is approved. SLA‑DG‑07 prescribes a free replacement as the default resolution.

**HO-013 · heldout · gpt-oss-120b · facts · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim was reported 4.8 hours after PoD, within the 48‑hour window (SLA-DG-01). PoD photo shows an intact box, but DELIVERY-313 notes a system‑failure that rendered all PoD images from that window unreliable, providing a documented reason to doubt the PoD (SLA-PRI-01). The customer supplied a specific damage description and a post‑delivery photo (SLA-DG-04), yet no unboxing evidence and the PoD is unreliable, creating contradictory evidence about package condition. Under SLA-DG-08, contradictory or insufficient evidence requires escalation to manual review.

**HO-013 · heldout · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim is within the 48-hour reporting window (SLA-DG-01). The PoD photo is deemed unreliable due to a documented system failure on the delivery route (SLA-PRI-01, DELIVERY-313), which prevents the application of SLA-DG-06 (auto-approval for visible external damage) or SLA-DG-05 (agent discretion for intact packages). The customer provided sufficient evidence of damage (SLA-DG-04), but because the structured PoD evidence is compromised and the agent's statement is unverified, the evidence is insufficient to determine fault automatically. Therefore, SLA-DG-08 requires the case to be escalated to manual review.

**HO-013 · heldout · qwen3.8-27b · facts · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim was reported 4.8 hours after the PoD timestamp, satisfying the 48-hour eligibility window under SLA-DG-01. The customer provided a post-delivery photo (CUSTOMER-413) and a specific written description (CUSTOMER-313), satisfying the evidence requirements of SLA-DG-04. However, the PoD photo (POD-313) shows an intact package, which conflicts with the customer's claim of external damage. Although DELIVERY-313 documents a system failure that renders the PoD image unreliable, the agent's statement (AGENT-313) is unstructured and self-serving, and the PoD photo itself shows a mismatched consignee label, creating contradictory evidence regarding the package's condition at handover. Under SLA-DG-08, when evidence is contradictory or insufficient to determine fault, the case must be escalated to manual review rather than auto-approved or rejected.

**HO-013 · heldout · rules engine** (ESCALATE, reference APPROVE)

> The claim was reported within the window (4.8 h). The PoD shows the package intact at handover and there is no unboxing evidence, so SLA-DG-05 removes auto-approval. The customer's description is specific and plausible, so fault cannot be determined from the record: under SLA-DG-08 the case is escalated to manual review.

**HO-014 · heldout · gpt-oss-20b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was filed 12.8 hours after PoD, well within the 48‑hour window of SLA‑DG‑01. The PoD photo is flagged unusable, so SLA‑PRI‑01 permits us to doubt the structured evidence and rely on the customer’s narrative. The narrative provides a specific description of the damage, satisfying SLA‑DG‑04’s evidence requirement. With sufficient evidence and no conflicting evidence, the claim is approved under SLA‑DG‑04 and resolved via free replacement per SLA‑DG‑07.

**HO-015 · heldout · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 124.8 hours after delivery, missing the 48-hour window in SLA-DG-01. The PoD photo (POD-315) shows the package was intact, so the 7-day extension in SLA-DG-02 is not triggered. Although the customer provided specific evidence of damage (CUSTOMER-315, CUSTOMER-415) satisfying SLA-DG-04, the combination of a missed window and an intact PoD photo shifts the case to agent discretion under SLA-DG-05. The SLA does not provide an automatic outcome for this specific combination of facts, requiring manual review.

**HO-015 · heldout · qwen3.8-27b · zero_shot · hybrid k=12** (ESCALATE, reference REJECT)

> The reporting window is calculated from the PoD timestamp (2026-10-07T12:00:00+05:30) to the first customer message (2026-10-12T16:45:00+05:30), resulting in an interval of 5 days and 4 hours and 45 minutes. This exceeds the standard 48-hour window in SLA-DG-01, but the claim remains eligible for review because the 7-day exception in SLA-DG-02 applies to visible pre-existing damage, although the PoD photo (POD-315) shows the package as intact and undamaged. Under SLA-DG-05, when the PoD photo shows an intact package and the customer provides no unboxing evidence (SLA-DEF-05), the claim shifts to agent discretion rather than being auto-approved or auto-rejected. The customer's photo (CUSTOMER-415) and description (CUSTOMER-315) satisfy the minimum evidence requirement of SLA-DG-04, but the conflict between the intact PoD and the reported internal damage, combined with the lack of unboxing video, necessitates manual review to determine fault.

**HO-016 · heldout · rules engine** (ESCALATE, reference APPROVE)

> The claim was reported within the window (2.8 h). The PoD shows the package intact at handover and there is no unboxing evidence, so SLA-DG-05 removes auto-approval. The customer's description is specific and plausible, so fault cannot be determined from the record: under SLA-DG-08 the case is escalated to manual review.

**HO-017 · heldout · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The reporting window of 100.4 hours exceeds the 48-hour limit in SLA-DG-01, and the 7-day extension in SLA-DG-02 does not apply because the PoD photo (POD-317) shows an intact package. Under SLA-DG-05, when the PoD photo shows the package intact and no unboxing evidence is provided, the claim shifts to agent discretion. The customer's narrative (CUSTOMER-317) and photo (CUSTOMER-417) are specific but conflict with the structured PoD evidence (POD-317), which takes priority under SLA-PRI-01. The case is escalated to manual review to resolve the conflict between the customer's claim of transit damage and the delivery partner's record of an intact package.

**HO-017 · heldout · qwen3.8-27b · zero_shot · hybrid k=12** (ESCALATE, reference REJECT)

> The reporting window is calculated from the PoD timestamp (2026-10-09T15:35:00+05:30) to the first customer message (2026-10-13T20:00:00+05:30), an interval of approximately 4 days and 4.5 hours. This falls within the 48-hour default window of SLA-DG-01, so the claim is eligible for review. However, the PoD photo (POD-317) shows the package intact and undamaged, which contradicts the customer's claim of a crushed box and prevents the application of the 7-day extension under SLA-DG-02 or the automatic approval under SLA-DG-06. Although the customer provided a photo of the damaged product (CUSTOMER-417) satisfying the evidence requirement of SLA-DG-04, the conflict between the structured PoD evidence and the unstructured customer narrative, combined with the absence of unboxing evidence, triggers SLA-DG-08. This clause mandates escalation to manual review when evidence is contradictory or insufficient to determine fault, rather than allowing a binary decision based on narrative credibility alone.

**HO-019 · heldout · gpt-oss-20b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 8.2 hours after PoD, within the 24‑hour window of SLA‑COD‑01. Structured evidence (reconciliation log and agent statement) is reliable per SLA‑PRI‑01. The reconciliation log matches the order total, and the agent statement confirms the same amount, so the claim lacks corroborating evidence and is presumptively rejected under SLA‑COD‑03. However, SLA‑COD‑09 overrides this by flagging the claim as fraudulent when at least two independent sources confirm the correct amount, requiring account‑level review. Thus the case is escalated with no refund.

**HO-021 · heldout · gpt-oss-120b · facts · hybrid k=12** (APPROVE, reference REJECT)

> The claim was reported 2.5 hours after the PoD (16:30 IST) which is within the 24‑hour window required by SLA‑COD‑01. The reconciliation log (RECON-321) records a collected amount of ₹1,400, which is higher than the invoice total of ₹1,394, triggering SLA‑COD‑04. Applying the formula gives a refund of ₹6. Structured evidence (reconciliation log) overrides unstructured chat, satisfying SLA‑PRI‑01. Hence the claim is approved for a ₹6 refund.

**HO-022 · heldout · gpt-oss-20b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported within 3.6 hours of PoD, satisfying SLA-COD-01. Structured evidence (PoD) is reliable per SLA-PRI-01, but the reconciliation log is unavailable. The customer alleges a ₹10 overcharge, which falls under SLA-COD-07’s rule that discrepancies ≤ ₹10 are not eligible for formal dispute resolution and should be handled directly by the agent. Therefore the claim is rejected and no refund is issued.

**HO-022 · heldout · qwen3.8-27b · zero_shot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported within the 24-hour window (PoD 10:45 IST to first message 14:20 IST is 3h 35m), satisfying SLA-COD-01. The customer's claim references the order ID and specifies the amount collected (₹700) versus the order total (₹690), satisfying SLA-COD-02. Although the reconciliation log is unavailable (RECON-322), which would normally trigger a customer-favorable resolution under SLA-COD-06, the disputed amount is ₹10. SLA-COD-07 explicitly states that discrepancies of ≤ ₹10 are not eligible for formal dispute resolution and should be resolved directly by the agent. Therefore, the claim is rejected as ineligible for formal resolution.

**HO-022 · heldout · rules engine** (ESCALATE, reference APPROVE)

> No reconciliation record exists, so SLA-COD-06 would default to a customer-favourable refund — but the customer has not stated the amount collected (SLA-COD-02), so the disputed excess cannot be computed. Escalated to obtain the amount.

**HO-023 · heldout · gpt-oss-120b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was filed 5.4 hours after delivery, satisfying SLA-COD-01. The reconciliation log (RECON-323) records the collected amount as ₹2,999, matching the invoice, which triggers the presumptive rejection under SLA-COD-03. The customer’s chat and screenshot do not provide corroborating evidence of a higher amount handed over, and structured evidence prevails per SLA-PRI-01. Therefore the claim is rejected.

**HO-023 · heldout · gpt-oss-120b · facts · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported 5.4 hours after the PoD (13:15 → 18:40), within the 24‑hour SLA‑COD‑01 window, and references the order ID and amounts as required by SLA‑COD‑02. The reconciliation log (RECON-323) matches the invoice amount (₹2,999) and, per SLA‑COD‑03, this structured evidence presumes the claim should be rejected unless the customer provides corroborating proof of a higher collection, which the provided screenshot (CUSTOMER-423) does not. Structured evidence outweighs the unstructured chat (SLA‑PRI‑01), and no reason to doubt the log is present, so the claim is rejected.

**HO-023 · heldout · gpt-oss-20b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported within 5.4 h of PoD, well within the 24‑hour window of SLA‑COD‑01. Structured evidence (reconciliation log and PoD) is reliable per SLA‑PRI‑01. The reconciliation log shows ₹2,999, matching the order total, so per SLA‑COD‑03 the overcharge claim is presumptively rejected; the customer’s corroborating screenshot confirms the order total but provides no evidence of an actual overcharge. The claim also satisfies SLA‑COD‑02 by referencing the order ID and amounts. Therefore the claim is rejected with no refund.

**HO-024 · heldout · gpt-oss-120b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported within 24 hours (3.7 h) per SLA-COD-01. Structured reconciliation log (RECON-324) is trusted over chat per SLA-PRI-01. The log shows ₹1,850 collected, which is lower than the ₹1,950 invoice, meeting SLA-COD-05 criteria for an undercharge. SLA-COD-05 dictates no customer‑facing action, so the claim is rejected. No refund is due.

**HO-024 · heldout · gpt-oss-120b · facts · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported 3.7 hours after PoD, within the 24‑hour window of SLA‑COD‑01, and references the order and amounts per SLA‑COD‑02. The reconciliation log (RECON-324) records ₹1,850 collected, which is lower than the invoice total ₹1,950, triggering SLA‑COD‑05 that classifies this as an undercharge handled internally with no customer‑facing action. Hence the claim is rejected.

**HO-024 · heldout · gpt-oss-20b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported 3.7 hours after PoD, within the 24‑hour window of SLA‑COD‑01. Structured evidence from the reconciliation log (RECON‑324) is considered reliable per SLA‑PRI‑01, and it shows the amount collected was ₹1,850, which is ₹100 lower than the order total. SLA‑COD‑05 states that a lower reconciliation amount indicates an undercharge, requiring no customer‑facing action. Therefore the claim is rejected and no refund is issued.

**HO-024 · heldout · qwen3.8-27b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported within the 24-hour window (SLA-COD-01). The reconciliation log (RECON-324) confirms the agent remitted ₹1,850, which is lower than the ₹1,950 order total. Under SLA-COD-05, an undercharge is an internal operational issue where the company absorbs the loss, and no customer-facing action or refund is required.

**HO-024 · heldout · qwen3.8-27b · facts · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported 3.7 hours after the PoD timestamp, satisfying the 24-hour eligibility window in SLA-COD-01. The reconciliation log (RECON-324) shows an amount of ₹1,850, which is lower than the order total of ₹1,950. Under SLA-COD-05, a reconciliation amount lower than the order total indicates an undercharge or data entry error, which is an internal operational matter and does not constitute a customer dispute requiring a refund or customer-facing action. The customer's claim of an overcharge is factually incorrect based on the structured evidence, and SLA-COD-03 presumes rejection of overcharge claims when the log does not corroborate an excess collection.

**HO-024 · heldout · qwen3.8-27b · zero_shot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported within the 24-hour eligibility window (PoD at 12:30 IST, first message at 16:10 IST) and correctly references the order ID and amounts. The reconciliation log (RECON-324) shows an amount of ₹1,850, which is lower than the order total of ₹1,950. Under SLA-COD-05, an undercharge indicates an internal operational issue or data entry error that is absorbed by the Company and does not constitute a customer dispute requiring a refund or further action. Therefore, the customer's request for confirmation is resolved by rejecting the formal dispute claim as no customer-facing action is needed.

**HO-024 · heldout · rules engine** (REJECT, reference APPROVE)

> The claim was reported within 24 hours. The reconciliation log shows ₹1,850 collected against an invoice of ₹1,950 — an undercharge, not an overcharge. Under SLA-COD-05 this needs no customer-facing action; the company absorbs or audits the shortfall internally.

**HO-026 · heldout · gpt-oss-120b · facts · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 4.8 hours after PoD, satisfying SLA-COD-01’s 24‑hour window. The reconciliation log (RECON-326) matches the invoice amount, and the agent statement (AGENT-326) confirms the exact amount was collected, providing two independent sources that the customer was not overcharged. Under SLA-COD-09, this constitutes a fraudulent claim and must be flagged for account‑level review, which requires escalation. Structured evidence overrides the customer’s unsubstantiated allegation per SLA-PRI-01.

**HO-028 · heldout · gpt-oss-120b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was filed 0.3 hours after PoD, satisfying SLA-COD-01's 24‑hour window. Structured records (reconciliation log and digital receipt) both show the collected amount as ₹2,500, matching the invoice. Under SLA-COD-03, when the log matches the order total, the overcharge claim is presumptively rejected unless the customer supplies corroborating evidence, which is absent. Therefore the claim is rejected with no refund.

**HO-028 · heldout · gpt-oss-120b · facts · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported 0.33 hours after the PoD, within the 24‑hour window of SLA‑COD‑01, so it is eligible. The reconciliation log (RECON-328) records the amount collected as ₹2,500, matching the invoice, and the digital COD receipt (DELIVERY-428) also confirms ₹2,500 was received with no change. Under SLA‑COD‑03, when the reconciliation log matches the order total, the customer’s overcharge claim is presumptively rejected unless corroborating evidence is provided, which the customer did not supply. Hence the claim is rejected.

**HO-028 · heldout · gpt-oss-20b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was filed 0.3 h after PoD, well within the 24‑hour window of SLA‑COD‑01. Structured evidence (reconciliation log RECON‑328) matches the order total and is deemed reliable per SLA‑PRI‑01, outweighing the unstructured customer chat. SLA‑COD‑03 presumes rejection of an overcharge claim when the log matches the invoice and no corroborating evidence exists, which is the case here. Thus the claim is rejected with no refund.

**HO-028 · heldout · qwen3.8-27b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported within the 24-hour window (SLA-COD-01) based on the PoD timestamp (POD-328) and the first customer message (CUSTOMER-428). The reconciliation log (RECON-328) shows an amount of ₹2,500, which matches the order total. Under SLA-COD-03, this match creates a presumption of rejection for the customer's overcharge claim. The customer failed to provide the required corroborating evidence (e.g., a photo of the cash or a chat screenshot) to rebut this presumption. Therefore, the structured evidence (RECON-328) prevails over the customer's unstructured claim (CUSTOMER-428) per SLA-PRI-01.

**HO-028 · heldout · qwen3.8-27b · facts · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported within the 24-hour window (PoD 14:00 IST, first report 14:20 IST). The reconciliation log (RECON-328) shows the agent remitted exactly ₹2,500, matching the order total. Under SLA-COD-03, a matching reconciliation log presumptively rejects an overcharge claim unless the customer provides corroborating evidence (e.g., photo of cash or chat screenshot), which is absent. The customer's claim is further contradicted by the digital receipt (DELIVERY-428) and the agent's statement (AGENT-328), and the customer's own initial message (CUSTOMER-328) confirms paying exactly ₹2,500.

**HO-028 · heldout · qwen3.8-27b · zero_shot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported at 22:40 IST on 2026-10-17, which is 8 hours and 40 minutes after the PoD timestamp of 14:00 IST, satisfying the 24-hour eligibility window in SLA-COD-01. The claim meets the specificity requirements of SLA-COD-02 by referencing the order ID and stating the collected amount (₹3,000) versus the order total (₹2,500). Under SLA-COD-03, the primary evidence source is the cash reconciliation log (RECON-328), which records an amount of ₹2,500, matching the order total. Since the reconciliation log matches the order total, the customer's claim of overcharge is presumptively rejected unless corroborating evidence is provided. The customer provided no corroborating evidence (such as a photo of the cash handed over or a chat screenshot with the agent showing the discrepancy); instead, the structured evidence (RECON-328, DELIVERY-428) and the customer's own initial chat message (CUSTOMER-328) confirm that ₹2,500 was paid and no change was due, contradicting the later complaint.

**HO-028 · heldout · rules engine** (REJECT, reference ESCALATE)

> The reconciliation log records ₹2,500, matching the invoice total. The customer offers no corroborating evidence of the amount handed over, so under SLA-COD-03 the overcharge claim is presumptively rejected.

**HO-030 · heldout · gpt-oss-120b · cot · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim was reported within the 24‑hour window (SLA-COD-01). Structured evidence (reconciliation log) is primary (SLA-PRI-01). Although the log matches the invoice, the customer provided corroborating chat evidence, lifting the presumptive rejection per SLA-COD-03. No clause then mandates a refund, leaving the outcome discretionary, so the case is escalated for manual review.

**HO-030 · heldout · gpt-oss-120b · facts · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim was reported 2.4 hours after PoD, within the 24‑hour SLA-COD-01 window. The reconciliation log (RECON-330) matches the invoice amount, so under SLA-COD-03 the claim is presumptively rejected, but the customer supplied corroborating chat evidence (CUSTOMER-330, CUSTOMER-430) of an extra ₹200 floor charge, which rebuts the presumption. No clause specifies a refund when the log matches but corroborating evidence exists, and SLA-PRI-01 gives structured evidence priority only absent a specific rule; SLA-COD-03 is the specific clause governing this scenario, leaving the outcome undecided, thus requiring manual review.

**HO-030 · heldout · gpt-oss-20b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was filed 2.4 h after PoD, within the 24‑hour window of SLA‑COD‑01. Structured evidence (the reconciliation log) is primary per SLA‑PRI‑01, and it shows the amount collected matched the invoice (₹2,250). SLA‑COD‑03 presumes rejection when the log matches the order total, and the presence of customer corroborating evidence does not override the structured record. Therefore the claim is rejected with no refund.

**HO-030 · heldout · qwen3.8-27b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim is eligible as it was reported within 24 hours of the PoD timestamp (SLA-COD-01). Although the customer provided corroborating evidence (CUSTOMER-430) and the agent admitted to the overcharge (AGENT-330), the reconciliation log (RECON-330) shows the company received the full order total of ₹2,250. According to SLA-COD-04, the refund amount is calculated as the reconciliation amount minus the order total (₹2,250 - ₹2,250 = ₹0). Since the calculated refund is zero, the claim for a refund of the excess amount is rejected.

**HO-030 · heldout · qwen3.8-27b · facts · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim is eligible for review as it was reported 2.4 hours after the PoD timestamp, well within the 24-hour window mandated by SLA-COD-01. Under SLA-COD-03, the reconciliation log (RECON-330) matching the order total of ₹2,250 presumptively rejects the overcharge claim unless the customer provides corroborating evidence. The customer provided a WhatsApp screenshot (CUSTOMER-430) where the agent (identified by the matching phone number ending in 4417 per AGENT-330) explicitly confirms collecting an extra ₹200 'floor charge'. This evidence directly rebuts the presumption in SLA-COD-03, creating a conflict between the structured reconciliation log and the corroborating unstructured evidence. Because the SLA does not provide an automatic resolution mechanism for this specific conflict where the presumption is rebutted, the case requires manual review to determine the final liability.

**HO-030 · heldout · qwen3.8-27b · zero_shot · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim was reported within the 24-hour window (PoD 12:40 IST to first message 15:05 IST) and meets the specificity requirements of SLA-COD-02. Under SLA-COD-03, the reconciliation log (RECON-330) matching the order total presumptively rejects the overcharge claim unless the customer provides corroborating evidence. The customer provided a WhatsApp screenshot (CUSTOMER-430) which corroborates the claim, thereby rebutting the presumption and leaving the parties' evidence in conflict. The agent's statement (AGENT-330) admits collecting the extra ₹200 but claims it was an agreed 'floor charge' not remitted to the partner, a factual question regarding the validity of the fee that the SLA does not automatically resolve, necessitating manual review.

**HO-030 · heldout · rules engine** (ESCALATE, reference APPROVE)

> The reconciliation log (₹2,250) matches the invoice, which would ordinarily reject the claim under SLA-COD-03 — but the customer has supplied corroborating evidence, which displaces the presumption. Whether the claim is mistaken or knowingly false (SLA-COD-09 account-level review) is a factual question the record cannot settle, so the case is escalated to manual review.

**HO-032 · heldout · rules engine** (ESCALATE, reference APPROVE)

> No reconciliation record exists, so SLA-COD-06 would default to a customer-favourable refund — but the customer has not stated the amount collected (SLA-COD-02), so the disputed excess cannot be computed. Escalated to obtain the amount.

**HO-033 · heldout · gpt-oss-120b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was reported 0.4 h after PoD, satisfying SLA-COD-01's 24‑hour window. No reconciliation log exists (RECON-333), invoking SLA-COD-06 which defaults to a customer‑favorable outcome regardless of other evidence. Accordingly the disputed excess of ₹500 is refunded.

**HO-033 · heldout · gpt-oss-120b · facts · hybrid k=12** (APPROVE, reference ESCALATE)

> The PoD at 12:15 and the first customer report at 12:40 give a 0.4‑hour window, well within the 24‑hour limit of SLA-COD-01, so the claim is eligible. The reconciliation log is unavailable (RECON-333), triggering SLA-COD-06 which mandates a customer‑favorable resolution by refunding the disputed excess. The excess is ₹3,650‑₹3,150 = ₹500, so the refund is approved.

**HO-033 · heldout · gpt-oss-20b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was filed 0.4 hours after PoD, well within the 24‑hour window of SLA‑COD‑01. Structured evidence (RECON‑333) is missing, so per SLA‑PRI‑01 the agent statement (AGENT‑333) is reliable. SLA‑COD‑06 applies because the reconciliation log is unavailable, mandating a customer‑favorable refund of the disputed ₹500 as stated in CUSTOMER‑433.

**HO-033 · heldout · qwen3.8-27b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim is eligible for review as it was reported within the 24-hour window of the PoD timestamp (SLA-COD-01). The reconciliation log is unavailable due to agent non-compliance (RECON-333), which triggers the customer-favorable resolution mandated by SLA-COD-06. This clause takes precedence over other provisions because the absence of records is an operational failure on the Company's side. The refund amount is calculated as the disputed excess of ₹500 (₹3,650 claimed - ₹3,150 order total).

**HO-033 · heldout · qwen3.8-27b · facts · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was reported within the 24-hour window mandated by SLA-COD-01, as the first customer message (CUSTOMER-433) occurred approximately 8.75 hours after the Proof-of-Delivery timestamp (POD-333). The reconciliation log (RECON-333) is explicitly marked as UNAVAILABLE due to agent non-compliance, which triggers the default customer-favorable resolution under SLA-COD-06. Although the agent's statement (AGENT-333) claims the correct amount was collected, SLA-COD-06 takes precedence over other clauses when the reconciliation log is absent, attributing the lack of records to an operational failure on the company's side. Consequently, the disputed excess amount of ₹500 (₹3,650 claimed collected minus ₹3,150 order total) must be refunded to the customer.

**HO-033 · heldout · qwen3.8-27b · zero_shot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was reported within the 24-hour eligibility window, as the first customer message (CUSTOMER-433) at 20:55 IST on 2026-10-20 occurred 8 hours and 40 minutes after the Proof-of-Delivery timestamp (POD-333) at 12:15 IST. The reconciliation log (RECON-333) is explicitly marked as UNAVAILABLE due to agent non-compliance, which triggers the default customer-favorable resolution under SLA-COD-06. Although the agent's statement (AGENT-333) contradicts the customer's claim of overcharge, SLA-COD-06 takes precedence over other clauses when the reconciliation log is absent, attributing the lack of records to an operational failure on the company's side. The refund amount is calculated as the disputed excess of ₹500 (₹3,650 claimed - ₹3,150 order total).

**HO-033 · heldout · rules engine** (APPROVE, reference ESCALATE)

> The claim was reported 0.4 h after delivery, within 24 hours. The delivery partner has no reconciliation record for this order (system failure), which SLA-COD-06 treats as an operational failure on the company side: the claim defaults to a customer-favourable refund of the disputed excess, ₹3,650 − ₹3,150 = ₹500.00. SLA-COD-06 takes precedence over the ₹10 tolerance in SLA-COD-07. Refund within 5 business days (SLA-COD-08).

**HO-034 · heldout · gpt-oss-120b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was filed 15.7 hours after PoD, satisfying SLA-COD-01. The reconciliation log matches the order total and is reliable; under SLA-PRI-01 structured evidence overrides the customer's photo. Although SLA-COD-03 allows a claim if corroborating evidence exists, SLA-PRI-01 dictates that the unchallenged structured record prevails, so the overcharge claim is rejected.

**HO-034 · heldout · gpt-oss-120b · facts · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported 15.7 hours after PoD, within the 24‑hour window (SLA-COD-01). The customer referenced the order and alleged a ₹2,140 collection (SLA-COD-02). The reconciliation log, a structured source, records the collected amount as ₹1,940, matching the invoice (SLA-COD-03). Although the customer supplied a photo of the agent’s device showing ₹2,140, SLA-PRI-01 gives priority to the structured reconciliation log absent any reason to doubt it, so the overcharge claim is rejected. No refund is due.

**HO-034 · heldout · gpt-oss-20b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported 15.7 hours after PoD, within the 24‑hour window of SLA‑COD‑01. Structured evidence from the reconciliation log (RECON‑334) matches the order total and is deemed reliable under SLA‑PRI‑01, with no reason to doubt it. SLA‑COD‑03 presumes rejection when the log matches the invoice, and the customer’s photo (CUSTOMER‑434) is corroborating but does not prove an overcharge. Therefore the claim is rejected with no refund.

**HO-034 · heldout · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim is eligible as it was reported within 24 hours of the PoD timestamp (SLA-COD-01). The reconciliation log (RECON-334) matches the order total, which presumptively rejects the claim under SLA-COD-03. However, the customer provided a photo (CUSTOMER-434) showing a different amount, which serves as the corroborating evidence required to rebut that presumption. Since the structured evidence (RECON-334) and the customer's corroborating evidence (CUSTOMER-434) are in direct conflict and the SLA does not specify a tie-breaker for this scenario, the case is escalated for manual review to determine the actual amount collected.

**HO-034 · heldout · qwen3.8-27b · facts · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim is eligible for review as it was reported 15.7 hours after the PoD timestamp, well within the 24-hour window mandated by SLA-COD-01. Under SLA-COD-03, the reconciliation log (RECON-334) matching the order total of ₹1,940 creates a presumption of rejection for the customer's overcharge claim. However, this presumption is rebutted because the customer provided corroborating evidence (CUSTOMER-434), a photo of the device screen showing ₹2,140, which is a specific exception to the presumption. Because the structured evidence (reconciliation log) and the customer's corroborating evidence are in direct conflict, and SLA-PRI-01 does not provide a specific documented reason to doubt the structured log, the case is escalated for manual review to resolve the factual discrepancy.

**HO-034 · heldout · qwen3.8-27b · zero_shot · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim is eligible for review as it was reported within 24 hours of the PoD timestamp (2026-10-20T18:25:00+05:30 to 2026-10-21T10:05:00+05:30 is approximately 15 hours 40 minutes). Under SLA-COD-03, the reconciliation log (RECON-334) shows the collected amount (₹1,940) matches the order total, which presumptively rejects the customer's claim of overcharge. However, the customer provided corroborating evidence (CUSTOMER-434), a photo of the device screen showing ₹2,140, which rebuts the presumption on its own terms. This creates a conflict between the structured evidence (reconciliation log) and the unstructured evidence (customer photo) that SLA-PRI-01 does not automatically resolve without a documented reason to doubt the structured log, leaving the factual question of the actual amount collected open for manual review.

**HO-034 · heldout · rules engine** (ESCALATE, reference APPROVE)

> The reconciliation log (₹1,940) matches the invoice, which would ordinarily reject the claim under SLA-COD-03 — but the customer has supplied corroborating evidence, which displaces the presumption. Whether the claim is mistaken or knowingly false (SLA-COD-09 account-level review) is a factual question the record cannot settle, so the case is escalated to manual review.

