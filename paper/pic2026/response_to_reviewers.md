# PIC 2026, Paper 325: response to reviewers and camera-ready change list

Paper: "AI-Assisted Dispute Adjudication for D2C Delivery Operations: An SLA-Grounded LLM Pipeline"
Status of this file: final (19 Nov 2026). All numbers match the 8-page camera-ready.

The submitted version reported the system, the evaluation protocol and clause-retrieval recall on 10 pilot
cases, and deferred end-to-end adjudication. All three reviewers accepted it; reviewers 1 and 5 asked mainly
for end-to-end results, more and independently labelled data, stronger baselines and ablations. The
camera-ready version adds those results. Every number comes from saved run files in the project repository.

## Reviewer 1 (Weak Accept)

| Comment | Change in camera-ready |
|---|---|
| W1. No end-to-end adjudication results; retrieval recall alone does not answer the research question. | New results section: three open-weight LLMs (gpt-oss-120b, qwen3.8-27b, gpt-oss-20b) × three prompting styles (zero-shot, facts, chain-of-thought), scored on decision accuracy with 95% Wilson intervals, macro-F1, escalation recall, clause F1, refund accuracy and grounding violations. |
| W2. Ten synthetic cases with single-annotator labels are insufficient. | Dataset grows to 60 cases: 10 pilot, 16 counterfactual (one decisive fact changed per pilot case) and 34 held-out cases written after the rules engine was frozen. The held-out cases were labelled blind by two independent annotators (Cohen's κ = 0.86, 91% decision agreement); the 12 disagreements were settled by a third person. |
| W3. Retrieval relies on lexical scoring; no comparison with BM25, dense, hybrid or full-context prompting; no rule-based baseline or ablations. | Retrieval now compared across lexical, BM25, dense (all-MiniLM-L6-v2) and hybrid (reciprocal rank fusion) at k = 4 and 12, with ranker recall and context recall. A full-context condition (all 29 clauses in the prompt) is run end to end: gpt-oss-120b with CoT scores 90% (pilot) and 75% (counterfactual) with the full SLA, against 82% (mean of four runs) and 81% with retrieval, so retrieval is not needed for accuracy at this policy size. The deterministic rules-engine baseline is completed and frozen before the held-out cases were written. Ablations: prompt style (zero-shot, facts, CoT; on the held-out set facts gave the best configuration, qwen3.8-27b at 79.4%, but scored below CoT for gpt-oss-120b, 64.7% vs 70.6%), pinned clauses and gates (ranker vs. context recall), and full context vs. retrieval. |

## Reviewer 4 (Strong Accept)

No changes requested.

## Reviewer 5 (Weak Accept)

| Comment | Change in camera-ready |
|---|---|
| 1. Report adjudication results: accuracy, macro-F1, escalation precision/recall, clause exact match and Jaccard, sub-decision accuracy, repeated-run consistency, latency with repair rounds; explanation quality; missed and unnecessary escalations. | Reported from saved runs: decision accuracy with 95% Wilson intervals, macro-F1, escalation precision and recall, clause F1 (partial credit, in place of exact match), refund accuracy, grounding violations and repair rounds, and repeated-run consistency (four runs of gpt-oss-120b, 95% pairwise decision agreement). The error analysis separates missed escalations (the dominant error), unnecessary escalations and approve/reject reversals, with a case study (COD-005). Latency is recorded per case in the saved runs but not reported for space. Explanation quality with a human rubric is not included and is listed as a limitation. |
| 2. Stronger comparisons: rule-based engine, human judgments, embedding retrieval, full-context prompt; ablations of pinned clauses, gates, expansion, validation and repair. | Rules engine, embedding and hybrid retrieval and full context added (see R1-W3). Human judgment enters through the two-annotator held-out labels and their agreement. The rules engine scores 100% in-sample but 58.8% on the held-out set, which we report as a central finding; the best LLM configuration (qwen3.8-27b with extracted facts) reaches 79.4% there. Validation/repair: none of 494 LLM rulings ended with an unresolved citation; the first answer needed one repair round in 24 (5%). |
| 3. Expand beyond ten cases; independent annotation with agreement; boundary cases, missing/ambiguous evidence, counterfactual pairs; independently sourced cases. | See R1-W2. The counterfactual set is built from one-fact edits. Held-out disagreements are analysed: all three decision disagreements stem from ambiguous SLA wording (how earlier claims are counted under SLA-DG-09, whether a same-day photo satisfies the unboxing requirement, and what makes a log implausible under SLA-COD-05). Independently sourced operational cases remain future work. |
| 4. Cross-family contamination from one-hop expansion. | Measured on all saved runs with retrieval: a wrong-family clause reached the prompt in all 468 LLM rulings, but none cited one. We report this and the family-restricted expansion as a recommended fix; it was not applied to the experiments, so that all runs share one retriever. |
| 5. Photographs handled as text descriptions. | Scope stated explicitly in the problem definition and limitations: the system adjudicates textualised evidence; image interpretation is out of scope. |

## Other changes

- Title, author list and affiliations as registered in CMT (six authors).
- Abstract, contributions and conclusion revised to report end-to-end results.
- Fig. 1 redrawn for the current pipeline (fact extraction, hybrid retrieval, grounding validation, rules-engine cross-check).
- Project-plan section, appendix, worked-example walk-throughs and descriptive tables (implementation, case schema,
  evidence types, scenario matrix, pilot labels, error taxonomy) removed to fit 8 pages; all results kept.
- References verified; new references for reciprocal rank fusion, Landis–Koch, MiniLM, Qwen3, Wilson intervals, McNemar and Holm.
