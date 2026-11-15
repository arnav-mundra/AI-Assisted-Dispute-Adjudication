# Error analysis and consistency

Generated from 5 saved run(s) in `results/runs/`. Confidence intervals are 95% Wilson intervals over all predictions pooled per configuration.

## Accuracy and stability by configuration

| Configuration | Runs | Accuracy (mean ± sd) | 95% CI | Escalation recall | Pairwise agreement |
|---|---|---|---|---|---|
| heldout · gpt-oss-120b · cot · hybrid k=12 | 1 | 71% ± 0% | 54%–83% | 29% | — |
| heldout · gpt-oss-20b · cot · hybrid k=12 | 1 | 59% ± 0% | 42%–74% | 0% | — |
| heldout · qwen3.8-27b · cot · hybrid k=12 | 1 | 62% ± 0% | 45%–76% | 43% | — |
| heldout · qwen3.8-27b · facts · hybrid k=12 | 1 | 79% ± 0% | 63%–90% | 71% | — |
| heldout · rules engine | 1 | 59% ± 0% | 42%–74% | 43% | — |

## Disagreement guard (simulated)

If the LLM and the rules engine disagree, escalate to manual review. Simulated from the cross-check stored with every prediction — no new model calls. Caveat: the rules engine was written with the pilot cases visible, so pilot rows are in-sample; counterfactual rows are the fairer test.

| Configuration | n | Accuracy before → after | Escalation recall before → after | Escalated by guard | Errors fixed | Correct decisions sent to review |
|---|---|---|---|---|---|---|
| heldout · qwen3.8-27b · facts · hybrid k=12 | 34 | 79% → 65% | 71% → 71% | 5 | 0 | 5 |
| heldout · gpt-oss-20b · cot · hybrid k=12 | 34 | 59% → 56% | 0% → 43% | 10 | 3 | 4 |
| heldout · gpt-oss-120b · cot · hybrid k=12 | 34 | 71% → 59% | 29% → 43% | 8 | 1 | 5 |
| heldout · qwen3.8-27b · cot · hybrid k=12 | 34 | 62% → 47% | 43% → 43% | 7 | 0 | 5 |

## Confidence floor (simulated)

Escalate any LLM ruling whose own confidence is below the floor. Pooled over every unguarded LLM run above. A floor only helps if the model is less confident when it is wrong — compare the two right-hand columns.

| Floor | Predictions | Accuracy before → after | Escalated | Errors fixed | Correct rulings sent to review |
|---|---|---|---|---|---|
| 0.50 | 136 | 68% → 68% | 0 | 0 | 0 |
| 0.60 | 136 | 68% → 68% | 0 | 0 | 0 |
| 0.70 | 136 | 68% → 68% | 0 | 0 | 0 |
| 0.80 | 136 | 68% → 67% | 1 | 0 | 1 |
| 0.90 | 136 | 68% → 66% | 9 | 2 | 4 |
| 0.95 | 136 | 68% → 66% | 12 | 3 | 5 |

## Error taxonomy

| Error kind | Count | Share |
|---|---|---|
| Forced a decision where the reference escalates | 22 | 38% |
| Escalated where the reference decides | 24 | 41% |
| Approved where the reference rejects, or the reverse | 12 | 21% |

The rules-engine cross-check reached the reference decision on **9 of 44** LLM errors — the share a disagreement flag would have routed to review.

Cases most often wrong: HO-005 (5), HO-024 (5), HO-028 (5), HO-030 (5), HO-033 (5), HO-034 (5)

## Every error

| Case | Configuration | Kind | Predicted → Reference | Cited primary | Reference clauses | Missed decisive evidence | Conf. | Rules engine |
|---|---|---|---|---|---|---|---|---|
| HO-002 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-DG-08 | SLA-DG-02, SLA-DG-06 | CUSTOMER-402 | 0.72 | — |
| HO-003 | heldout · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-01 | — | 0.95 | REJECT |
| HO-004 | heldout · qwen3.8-27b · cot · hybrid k=12 | polarity | APPROVE → REJECT | SLA-DG-06 | SLA-DG-01, SLA-DG-02 | — | 0.95 | REJECT |
| HO-005 | heldout · gpt-oss-120b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04, SLA-DG-05 | — | 0.92 | ESCALATE |
| HO-005 | heldout · gpt-oss-20b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04, SLA-DG-05 | — | 0.78 | ESCALATE |
| HO-005 | heldout · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04, SLA-DG-05 | — | 0.95 | ESCALATE |
| HO-005 | heldout · qwen3.8-27b · facts · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-04, SLA-DG-05 | — | 0.95 | ESCALATE |
| HO-005 | heldout · rules engine | over escalation | ESCALATE → REJECT | SLA-DG-08 | SLA-DG-04, SLA-DG-05 | — | 0.72 | — |
| HO-006 | heldout · gpt-oss-120b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-406 | 0.96 | APPROVE |
| HO-006 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-406 | 0.95 | APPROVE |
| HO-006 | heldout · qwen3.8-27b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-406 | 0.95 | APPROVE |
| HO-006 | heldout · rules engine | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-406 | 0.92 | — |
| HO-007 | heldout · gpt-oss-120b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-407 | 0.97 | APPROVE |
| HO-007 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-407 | 0.95 | APPROVE |
| HO-007 | heldout · qwen3.8-27b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-407 | 0.95 | APPROVE |
| HO-007 | heldout · rules engine | missed escalation | APPROVE → ESCALATE | SLA-DG-06 | SLA-DG-09, SLA-DG-06 | DELIVERY-407 | 0.92 | — |
| HO-010 | heldout · gpt-oss-120b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-DG-03 | SLA-DG-03, SLA-DEF-05, SLA-DG-06 | — | 0.92 | ESCALATE |
| HO-010 | heldout · gpt-oss-20b · cot · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-DG-03 | SLA-DG-03, SLA-DEF-05, SLA-DG-06 | — | 0.70 | ESCALATE |
| HO-010 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-DG-03 | SLA-DG-03, SLA-DEF-05, SLA-DG-06 | CUSTOMER-410, DELIVERY-310 | 0.70 | — |
| HO-012 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-04 | SLA-DG-05, SLA-DG-08 | — | 0.85 | ESCALATE |
| HO-013 | heldout · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-DG-08 | SLA-DG-01, SLA-DG-04, SLA-PRI-01 | AGENT-313 | 0.95 | ESCALATE |
| HO-013 | heldout · qwen3.8-27b · facts · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-DG-08 | SLA-DG-01, SLA-DG-04, SLA-PRI-01 | — | 0.95 | ESCALATE |
| HO-013 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-DG-08 | SLA-DG-01, SLA-DG-04, SLA-PRI-01 | AGENT-313, CUSTOMER-413, DELIVERY-313 | 0.72 | — |
| HO-014 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-DG-04 | SLA-DG-04, SLA-DG-08, SLA-PRI-01 | AGENT-314 | 0.85 | ESCALATE |
| HO-015 | heldout · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-01 | — | 0.95 | REJECT |
| HO-016 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-DG-08 | SLA-DG-01, SLA-DG-06 | CUSTOMER-416 | 0.72 | — |
| HO-017 | heldout · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-DG-05 | SLA-DG-01, SLA-DG-02 | AGENT-317 | 0.95 | REJECT |
| HO-019 | heldout · gpt-oss-20b · cot · hybrid k=12 | over escalation | ESCALATE → REJECT | SLA-COD-09 | SLA-COD-03 | — | 0.95 | REJECT |
| HO-022 | heldout · gpt-oss-20b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-07 | SLA-COD-06, SLA-COD-07 | AGENT-322 | 0.85 | ESCALATE |
| HO-022 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-COD-06 | SLA-COD-06, SLA-COD-07 | AGENT-322 | 0.60 | — |
| HO-023 | heldout · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | — | 0.96 | ESCALATE |
| HO-023 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | — | 0.95 | ESCALATE |
| HO-024 | heldout · gpt-oss-120b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-05 | SLA-COD-01, SLA-DEF-03, SLA-COD-05 | — | 0.96 | REJECT |
| HO-024 | heldout · gpt-oss-20b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-05 | SLA-COD-01, SLA-DEF-03, SLA-COD-05 | — | 0.95 | REJECT |
| HO-024 | heldout · qwen3.8-27b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-05 | SLA-COD-01, SLA-DEF-03, SLA-COD-05 | AGENT-324 | 0.95 | REJECT |
| HO-024 | heldout · qwen3.8-27b · facts · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-05 | SLA-COD-01, SLA-DEF-03, SLA-COD-05 | — | 0.95 | REJECT |
| HO-024 | heldout · rules engine | polarity | REJECT → APPROVE | SLA-COD-05 | SLA-COD-01, SLA-DEF-03, SLA-COD-05 | — | 0.85 | — |
| HO-028 | heldout · gpt-oss-120b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-09, SLA-COD-03 | AGENT-328, CUSTOMER-328 | 0.96 | REJECT |
| HO-028 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-09, SLA-COD-03 | AGENT-328, DELIVERY-428 | 0.95 | REJECT |
| HO-028 | heldout · qwen3.8-27b · cot · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-09, SLA-COD-03 | AGENT-328, CUSTOMER-328 | 0.95 | REJECT |
| HO-028 | heldout · qwen3.8-27b · facts · hybrid k=12 | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-09, SLA-COD-03 | — | 0.95 | REJECT |
| HO-028 | heldout · rules engine | missed escalation | REJECT → ESCALATE | SLA-COD-03 | SLA-COD-09, SLA-COD-03 | AGENT-328, DELIVERY-428 | 0.85 | — |
| HO-030 | heldout · gpt-oss-120b · cot · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-COD-08, SLA-PRI-01 | — | 0.78 | ESCALATE |
| HO-030 | heldout · gpt-oss-20b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-COD-08, SLA-PRI-01 | — | 0.85 | ESCALATE |
| HO-030 | heldout · qwen3.8-27b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-04 | SLA-COD-03, SLA-COD-08, SLA-PRI-01 | — | 0.95 | ESCALATE |
| HO-030 | heldout · qwen3.8-27b · facts · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-COD-08, SLA-PRI-01 | — | 0.95 | ESCALATE |
| HO-030 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-COD-08, SLA-PRI-01 | — | 0.62 | — |
| HO-032 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-COD-06 | SLA-COD-06 | AGENT-332 | 0.60 | — |
| HO-033 | heldout · gpt-oss-120b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-COD-06 | SLA-COD-06, SLA-COD-09 | AGENT-333, CUSTOMER-333 | 0.96 | APPROVE |
| HO-033 | heldout · gpt-oss-20b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-COD-06 | SLA-COD-06, SLA-COD-09 | — | 0.92 | APPROVE |
| HO-033 | heldout · qwen3.8-27b · cot · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-COD-06 | SLA-COD-06, SLA-COD-09 | AGENT-333, CUSTOMER-333 | 0.95 | APPROVE |
| HO-033 | heldout · qwen3.8-27b · facts · hybrid k=12 | missed escalation | APPROVE → ESCALATE | SLA-COD-06 | SLA-COD-06, SLA-COD-09 | AGENT-333, CUSTOMER-333 | 0.95 | APPROVE |
| HO-033 | heldout · rules engine | missed escalation | APPROVE → ESCALATE | SLA-COD-06 | SLA-COD-06, SLA-COD-09 | AGENT-333 | 0.85 | — |
| HO-034 | heldout · gpt-oss-120b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-PRI-01 | SLA-COD-03, SLA-PRI-01 | DELIVERY-334 | 0.88 | ESCALATE |
| HO-034 | heldout · gpt-oss-20b · cot · hybrid k=12 | polarity | REJECT → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | DELIVERY-334 | 0.95 | ESCALATE |
| HO-034 | heldout · qwen3.8-27b · cot · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | DELIVERY-334 | 0.95 | ESCALATE |
| HO-034 | heldout · qwen3.8-27b · facts · hybrid k=12 | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | DELIVERY-334 | 0.95 | ESCALATE |
| HO-034 | heldout · rules engine | over escalation | ESCALATE → APPROVE | SLA-COD-03 | SLA-COD-03, SLA-PRI-01 | DELIVERY-334 | 0.62 | — |

## Model rationales for the errors

**HO-002 · heldout · rules engine** (ESCALATE, reference APPROVE)

> The claim was reported within the window (151.7 h). The PoD photo cannot be relied on and nothing independently corroborates transit damage and there is no unboxing evidence, so SLA-DG-05 removes auto-approval. The customer's description is specific and plausible, so fault cannot be determined from the record: under SLA-DG-08 the case is escalated to manual review.

**HO-003 · heldout · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 90.4 hours after delivery, exceeding the 48-hour window in SLA-DG-01. The PoD photo (POD-303) shows an intact package, and the customer provided no unboxing evidence, triggering the agent discretion clause SLA-DG-05. Although the customer provided a specific damage description and photo (CUSTOMER-303, CUSTOMER-403) satisfying SLA-DG-04, the SLA does not provide an automatic outcome for this scenario. The case is escalated to manual review to determine if the damage is attributable to the customer or the delivery process.

**HO-004 · heldout · qwen3.8-27b · cot · hybrid k=12** (APPROVE, reference REJECT)

> The PoD photo (POD-304) shows visible external damage, which extends the reporting window to 7 days under SLA-DG-02. Although the customer reported the issue at 199.8 hours (exceeding the 168-hour window), the claim is still eligible for review because the SLA-DG-02 exception applies to the nature of the damage. The customer provided a specific description (CUSTOMER-304) and a post-delivery photo (CUSTOMER-404) that are consistent with the external damage shown in the PoD, satisfying SLA-DG-06. Under SLA-DG-06, the claim is approved without further evidence. The resolution is a free replacement as per SLA-DG-07.

**HO-005 · heldout · gpt-oss-120b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was filed 7.4 hours after delivery, within the 48‑hour window (SLA-DG-01). Structured PoD evidence is reliable (SLA-PRI-01). The customer provided no unboxing or post‑delivery photos and the description lacks specific damage details, so SLA-DG-04 is not satisfied. With an intact PoD photo and no unboxing evidence, the case moves to agent discretion per SLA-DG-05, but the evidence remains insufficient to decide fault, invoking SLA-DG-08 to escalate for manual review.

**HO-005 · heldout · gpt-oss-20b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was filed 7.4 h after PoD, within the 48‑hour window (SLA‑DG‑01). The PoD record is clear and untainted (SLA‑PRI‑01). The customer’s narrative lacks a specific damage location, so the required evidence per SLA‑DG‑04 is missing. With PoD intact and no unboxing evidence, the claim falls under SLA‑DG‑05, leaving the outcome to agent discretion. Because the evidence is insufficient to determine fault, SLA‑DG‑08 mandates escalation to manual review.

**HO-005 · heldout · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported within the 48-hour window (SLA-DG-01) and the PoD photo (POD-305) is reliable (SLA-PRI-01). However, the PoD shows an intact package and the customer provided no unboxing or post-delIVERY photographic proof (CUSTOMER-305, CUSTOMER-405). The narrative is too vague to satisfy the specificity requirement of SLA-04. As the evidence is contradictory (intact PoD vs. damage claim) and insufficient to determine fault, SLA-DG-08 mandates escalation to manual review.

**HO-005 · heldout · qwen3.8-27b · facts · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 7.4 hours after the PoD timestamp, which is within the 48-hour eligibility window under SLA-DG-01. The PoD photo (POD-305) clearly shows the package as intact and undamaged, and the customer has not provided any unboxing evidence or post-delivery photos as required by SLA-DG-04. Under SLA-DG-05, when the PoD shows an intact package and no unboxing evidence is provided, the claim shifts to agent discretion rather than being auto-approved or auto-rejected. Because the customer's narrative is generic ('damaged', 'bad quality') and lacks the specific details required to establish fault or damage location, the case is escalated to manual review for an agent to evaluate narrative credibility and product category.

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

**HO-012 · heldout · gpt-oss-20b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was reported 13.7 h after PoD, within the 48‑hour window of SLA‑DG‑01. The PoD photo is clear and reliable per SLA‑PRI‑01. The customer’s post‑delivery photo (CUSTOMER‑412) satisfies the evidence requirement of SLA‑DG‑04, providing a specific description of the damage. Thus the claim meets the eligibility criteria and is approved. SLA‑DG‑07 prescribes a free replacement as the default resolution.

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

**HO-016 · heldout · rules engine** (ESCALATE, reference APPROVE)

> The claim was reported within the window (2.8 h). The PoD shows the package intact at handover and there is no unboxing evidence, so SLA-DG-05 removes auto-approval. The customer's description is specific and plausible, so fault cannot be determined from the record: under SLA-DG-08 the case is escalated to manual review.

**HO-017 · heldout · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The reporting window of 100.4 hours exceeds the 48-hour limit in SLA-DG-01, and the 7-day extension in SLA-DG-02 does not apply because the PoD photo (POD-317) shows an intact package. Under SLA-DG-05, when the PoD photo shows the package intact and no unboxing evidence is provided, the claim shifts to agent discretion. The customer's narrative (CUSTOMER-317) and photo (CUSTOMER-417) are specific but conflict with the structured PoD evidence (POD-317), which takes priority under SLA-PRI-01. The case is escalated to manual review to resolve the conflict between the customer's claim of transit damage and the delivery partner's record of an intact package.

**HO-019 · heldout · gpt-oss-20b · cot · hybrid k=12** (ESCALATE, reference REJECT)

> The claim was reported 8.2 hours after PoD, within the 24‑hour window of SLA‑COD‑01. Structured evidence (reconciliation log and agent statement) is reliable per SLA‑PRI‑01. The reconciliation log matches the order total, and the agent statement confirms the same amount, so the claim lacks corroborating evidence and is presumptively rejected under SLA‑COD‑03. However, SLA‑COD‑09 overrides this by flagging the claim as fraudulent when at least two independent sources confirm the correct amount, requiring account‑level review. Thus the case is escalated with no refund.

**HO-022 · heldout · gpt-oss-20b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported within 3.6 hours of PoD, satisfying SLA-COD-01. Structured evidence (PoD) is reliable per SLA-PRI-01, but the reconciliation log is unavailable. The customer alleges a ₹10 overcharge, which falls under SLA-COD-07’s rule that discrepancies ≤ ₹10 are not eligible for formal dispute resolution and should be handled directly by the agent. Therefore the claim is rejected and no refund is issued.

**HO-022 · heldout · rules engine** (ESCALATE, reference APPROVE)

> No reconciliation record exists, so SLA-COD-06 would default to a customer-favourable refund — but the customer has not stated the amount collected (SLA-COD-02), so the disputed excess cannot be computed. Escalated to obtain the amount.

**HO-023 · heldout · gpt-oss-120b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was filed 5.4 hours after delivery, satisfying SLA-COD-01. The reconciliation log (RECON-323) records the collected amount as ₹2,999, matching the invoice, which triggers the presumptive rejection under SLA-COD-03. The customer’s chat and screenshot do not provide corroborating evidence of a higher amount handed over, and structured evidence prevails per SLA-PRI-01. Therefore the claim is rejected.

**HO-023 · heldout · gpt-oss-20b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported within 5.4 h of PoD, well within the 24‑hour window of SLA‑COD‑01. Structured evidence (reconciliation log and PoD) is reliable per SLA‑PRI‑01. The reconciliation log shows ₹2,999, matching the order total, so per SLA‑COD‑03 the overcharge claim is presumptively rejected; the customer’s corroborating screenshot confirms the order total but provides no evidence of an actual overcharge. The claim also satisfies SLA‑COD‑02 by referencing the order ID and amounts. Therefore the claim is rejected with no refund.

**HO-024 · heldout · gpt-oss-120b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported within 24 hours (3.7 h) per SLA-COD-01. Structured reconciliation log (RECON-324) is trusted over chat per SLA-PRI-01. The log shows ₹1,850 collected, which is lower than the ₹1,950 invoice, meeting SLA-COD-05 criteria for an undercharge. SLA-COD-05 dictates no customer‑facing action, so the claim is rejected. No refund is due.

**HO-024 · heldout · gpt-oss-20b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported 3.7 hours after PoD, within the 24‑hour window of SLA‑COD‑01. Structured evidence from the reconciliation log (RECON‑324) is considered reliable per SLA‑PRI‑01, and it shows the amount collected was ₹1,850, which is ₹100 lower than the order total. SLA‑COD‑05 states that a lower reconciliation amount indicates an undercharge, requiring no customer‑facing action. Therefore the claim is rejected and no refund is issued.

**HO-024 · heldout · qwen3.8-27b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported within the 24-hour window (SLA-COD-01). The reconciliation log (RECON-324) confirms the agent remitted ₹1,850, which is lower than the ₹1,950 order total. Under SLA-COD-05, an undercharge is an internal operational issue where the company absorbs the loss, and no customer-facing action or refund is required.

**HO-024 · heldout · qwen3.8-27b · facts · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported 3.7 hours after the PoD timestamp, satisfying the 24-hour eligibility window in SLA-COD-01. The reconciliation log (RECON-324) shows an amount of ₹1,850, which is lower than the order total of ₹1,950. Under SLA-COD-05, a reconciliation amount lower than the order total indicates an undercharge or data entry error, which is an internal operational matter and does not constitute a customer dispute requiring a refund or customer-facing action. The customer's claim of an overcharge is factually incorrect based on the structured evidence, and SLA-COD-03 presumes rejection of overcharge claims when the log does not corroborate an excess collection.

**HO-024 · heldout · rules engine** (REJECT, reference APPROVE)

> The claim was reported within 24 hours. The reconciliation log shows ₹1,850 collected against an invoice of ₹1,950 — an undercharge, not an overcharge. Under SLA-COD-05 this needs no customer-facing action; the company absorbs or audits the shortfall internally.

**HO-028 · heldout · gpt-oss-120b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was filed 0.3 hours after PoD, satisfying SLA-COD-01's 24‑hour window. Structured records (reconciliation log and digital receipt) both show the collected amount as ₹2,500, matching the invoice. Under SLA-COD-03, when the log matches the order total, the overcharge claim is presumptively rejected unless the customer supplies corroborating evidence, which is absent. Therefore the claim is rejected with no refund.

**HO-028 · heldout · gpt-oss-20b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was filed 0.3 h after PoD, well within the 24‑hour window of SLA‑COD‑01. Structured evidence (reconciliation log RECON‑328) matches the order total and is deemed reliable per SLA‑PRI‑01, outweighing the unstructured customer chat. SLA‑COD‑03 presumes rejection of an overcharge claim when the log matches the invoice and no corroborating evidence exists, which is the case here. Thus the claim is rejected with no refund.

**HO-028 · heldout · qwen3.8-27b · cot · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported within the 24-hour window (SLA-COD-01) based on the PoD timestamp (POD-328) and the first customer message (CUSTOMER-428). The reconciliation log (RECON-328) shows an amount of ₹2,500, which matches the order total. Under SLA-COD-03, this match creates a presumption of rejection for the customer's overcharge claim. The customer failed to provide the required corroborating evidence (e.g., a photo of the cash or a chat screenshot) to rebut this presumption. Therefore, the structured evidence (RECON-328) prevails over the customer's unstructured claim (CUSTOMER-428) per SLA-PRI-01.

**HO-028 · heldout · qwen3.8-27b · facts · hybrid k=12** (REJECT, reference ESCALATE)

> The claim was reported within the 24-hour window (PoD 14:00 IST, first report 14:20 IST). The reconciliation log (RECON-328) shows the agent remitted exactly ₹2,500, matching the order total. Under SLA-COD-03, a matching reconciliation log presumptively rejects an overcharge claim unless the customer provides corroborating evidence (e.g., photo of cash or chat screenshot), which is absent. The customer's claim is further contradicted by the digital receipt (DELIVERY-428) and the agent's statement (AGENT-328), and the customer's own initial message (CUSTOMER-328) confirms paying exactly ₹2,500.

**HO-028 · heldout · rules engine** (REJECT, reference ESCALATE)

> The reconciliation log records ₹2,500, matching the invoice total. The customer offers no corroborating evidence of the amount handed over, so under SLA-COD-03 the overcharge claim is presumptively rejected.

**HO-030 · heldout · gpt-oss-120b · cot · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim was reported within the 24‑hour window (SLA-COD-01). Structured evidence (reconciliation log) is primary (SLA-PRI-01). Although the log matches the invoice, the customer provided corroborating chat evidence, lifting the presumptive rejection per SLA-COD-03. No clause then mandates a refund, leaving the outcome discretionary, so the case is escalated for manual review.

**HO-030 · heldout · gpt-oss-20b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was filed 2.4 h after PoD, within the 24‑hour window of SLA‑COD‑01. Structured evidence (the reconciliation log) is primary per SLA‑PRI‑01, and it shows the amount collected matched the invoice (₹2,250). SLA‑COD‑03 presumes rejection when the log matches the order total, and the presence of customer corroborating evidence does not override the structured record. Therefore the claim is rejected with no refund.

**HO-030 · heldout · qwen3.8-27b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim is eligible as it was reported within 24 hours of the PoD timestamp (SLA-COD-01). Although the customer provided corroborating evidence (CUSTOMER-430) and the agent admitted to the overcharge (AGENT-330), the reconciliation log (RECON-330) shows the company received the full order total of ₹2,250. According to SLA-COD-04, the refund amount is calculated as the reconciliation amount minus the order total (₹2,250 - ₹2,250 = ₹0). Since the calculated refund is zero, the claim for a refund of the excess amount is rejected.

**HO-030 · heldout · qwen3.8-27b · facts · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim is eligible for review as it was reported 2.4 hours after the PoD timestamp, well within the 24-hour window mandated by SLA-COD-01. Under SLA-COD-03, the reconciliation log (RECON-330) matching the order total of ₹2,250 presumptively rejects the overcharge claim unless the customer provides corroborating evidence. The customer provided a WhatsApp screenshot (CUSTOMER-430) where the agent (identified by the matching phone number ending in 4417 per AGENT-330) explicitly confirms collecting an extra ₹200 'floor charge'. This evidence directly rebuts the presumption in SLA-COD-03, creating a conflict between the structured reconciliation log and the corroborating unstructured evidence. Because the SLA does not provide an automatic resolution mechanism for this specific conflict where the presumption is rebutted, the case requires manual review to determine the final liability.

**HO-030 · heldout · rules engine** (ESCALATE, reference APPROVE)

> The reconciliation log (₹2,250) matches the invoice, which would ordinarily reject the claim under SLA-COD-03 — but the customer has supplied corroborating evidence, which displaces the presumption. Whether the claim is mistaken or knowingly false (SLA-COD-09 account-level review) is a factual question the record cannot settle, so the case is escalated to manual review.

**HO-032 · heldout · rules engine** (ESCALATE, reference APPROVE)

> No reconciliation record exists, so SLA-COD-06 would default to a customer-favourable refund — but the customer has not stated the amount collected (SLA-COD-02), so the disputed excess cannot be computed. Escalated to obtain the amount.

**HO-033 · heldout · gpt-oss-120b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was reported 0.4 h after PoD, satisfying SLA-COD-01's 24‑hour window. No reconciliation log exists (RECON-333), invoking SLA-COD-06 which defaults to a customer‑favorable outcome regardless of other evidence. Accordingly the disputed excess of ₹500 is refunded.

**HO-033 · heldout · gpt-oss-20b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was filed 0.4 hours after PoD, well within the 24‑hour window of SLA‑COD‑01. Structured evidence (RECON‑333) is missing, so per SLA‑PRI‑01 the agent statement (AGENT‑333) is reliable. SLA‑COD‑06 applies because the reconciliation log is unavailable, mandating a customer‑favorable refund of the disputed ₹500 as stated in CUSTOMER‑433.

**HO-033 · heldout · qwen3.8-27b · cot · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim is eligible for review as it was reported within the 24-hour window of the PoD timestamp (SLA-COD-01). The reconciliation log is unavailable due to agent non-compliance (RECON-333), which triggers the customer-favorable resolution mandated by SLA-COD-06. This clause takes precedence over other provisions because the absence of records is an operational failure on the Company's side. The refund amount is calculated as the disputed excess of ₹500 (₹3,650 claimed - ₹3,150 order total).

**HO-033 · heldout · qwen3.8-27b · facts · hybrid k=12** (APPROVE, reference ESCALATE)

> The claim was reported within the 24-hour window mandated by SLA-COD-01, as the first customer message (CUSTOMER-433) occurred approximately 8.75 hours after the Proof-of-Delivery timestamp (POD-333). The reconciliation log (RECON-333) is explicitly marked as UNAVAILABLE due to agent non-compliance, which triggers the default customer-favorable resolution under SLA-COD-06. Although the agent's statement (AGENT-333) claims the correct amount was collected, SLA-COD-06 takes precedence over other clauses when the reconciliation log is absent, attributing the lack of records to an operational failure on the company's side. Consequently, the disputed excess amount of ₹500 (₹3,650 claimed collected minus ₹3,150 order total) must be refunded to the customer.

**HO-033 · heldout · rules engine** (APPROVE, reference ESCALATE)

> The claim was reported 0.4 h after delivery, within 24 hours. The delivery partner has no reconciliation record for this order (system failure), which SLA-COD-06 treats as an operational failure on the company side: the claim defaults to a customer-favourable refund of the disputed excess, ₹3,650 − ₹3,150 = ₹500.00. SLA-COD-06 takes precedence over the ₹10 tolerance in SLA-COD-07. Refund within 5 business days (SLA-COD-08).

**HO-034 · heldout · gpt-oss-120b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was filed 15.7 hours after PoD, satisfying SLA-COD-01. The reconciliation log matches the order total and is reliable; under SLA-PRI-01 structured evidence overrides the customer's photo. Although SLA-COD-03 allows a claim if corroborating evidence exists, SLA-PRI-01 dictates that the unchallenged structured record prevails, so the overcharge claim is rejected.

**HO-034 · heldout · gpt-oss-20b · cot · hybrid k=12** (REJECT, reference APPROVE)

> The claim was reported 15.7 hours after PoD, within the 24‑hour window of SLA‑COD‑01. Structured evidence from the reconciliation log (RECON‑334) matches the order total and is deemed reliable under SLA‑PRI‑01, with no reason to doubt it. SLA‑COD‑03 presumes rejection when the log matches the invoice, and the customer’s photo (CUSTOMER‑434) is corroborating but does not prove an overcharge. Therefore the claim is rejected with no refund.

**HO-034 · heldout · qwen3.8-27b · cot · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim is eligible as it was reported within 24 hours of the PoD timestamp (SLA-COD-01). The reconciliation log (RECON-334) matches the order total, which presumptively rejects the claim under SLA-COD-03. However, the customer provided a photo (CUSTOMER-434) showing a different amount, which serves as the corroborating evidence required to rebut that presumption. Since the structured evidence (RECON-334) and the customer's corroborating evidence (CUSTOMER-434) are in direct conflict and the SLA does not specify a tie-breaker for this scenario, the case is escalated for manual review to determine the actual amount collected.

**HO-034 · heldout · qwen3.8-27b · facts · hybrid k=12** (ESCALATE, reference APPROVE)

> The claim is eligible for review as it was reported 15.7 hours after the PoD timestamp, well within the 24-hour window mandated by SLA-COD-01. Under SLA-COD-03, the reconciliation log (RECON-334) matching the order total of ₹1,940 creates a presumption of rejection for the customer's overcharge claim. However, this presumption is rebutted because the customer provided corroborating evidence (CUSTOMER-434), a photo of the device screen showing ₹2,140, which is a specific exception to the presumption. Because the structured evidence (reconciliation log) and the customer's corroborating evidence are in direct conflict, and SLA-PRI-01 does not provide a specific documented reason to doubt the structured log, the case is escalated for manual review to resolve the factual discrepancy.

**HO-034 · heldout · rules engine** (ESCALATE, reference APPROVE)

> The reconciliation log (₹1,940) matches the invoice, which would ordinarily reject the claim under SLA-COD-03 — but the customer has supplied corroborating evidence, which displaces the presumption. Whether the claim is mistaken or knowingly false (SLA-COD-09 account-level review) is a factual question the record cannot settle, so the case is escalated to manual review.

