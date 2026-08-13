# Phase 0 — Evaluation Protocol v0.1

## Primary research question

Can an LLM-based reasoning pipeline resolve D2C damaged-goods and COD-mismatch disputes as accurately and consistently as a human/reference adjudication while grounding decisions in the SLA?

## Primary metrics

1. **Overall decision accuracy** — exact match of `APPROVE`, `REJECT`, or `ESCALATE`.
2. **Macro-F1** — balances performance across the three decision classes.
3. **SLA clause accuracy** — exact match of the governing clause set, with a clearly defined partial-credit rule only if the experiment later requires it.
4. **Escalation accuracy** — whether ambiguous/insufficient-evidence cases are correctly escalated.
5. **Sub-decision accuracy** — exact correctness of structured fields such as refund amount or resolution type where applicable.
6. **Consistency** — agreement across repeated runs on the same case under fixed settings.
7. **Latency** — wall-clock inference time per case.
8. **Explanation quality** — primarily manual rubric-based assessment; ROUGE/BERTScore may be reported as secondary descriptive measures, not as proof of factual correctness.

## Baselines

- Random baseline.
- Majority-class baseline.
- Human/reference adjudication.
- LLM variants using different prompting strategies/models.

## Evaluation split

The project will maintain separate development, validation, and held-out test sets.
The held-out test labels must not be used to tune prompts, thresholds, retrieval settings, or model selection.

## Leakage controls

- Keep test ground truth in a separate file from model input.
- Do not place test labels in prompts or retrieval indexes.
- Do not tune on held-out cases after inspecting predictions.
- Record the exact SLA version used by each experiment.
- Record model name/version, prompt version, retrieval configuration, and run timestamp.

## Error categories

Every incorrect or unsafe result should be assigned one or more categories:
- evidence extraction error
- timestamp reasoning error
- clause retrieval error
- clause interpretation error
- contradiction handling error
- missing-evidence error
- hallucinated fact
- unjustified confidence / failure to escalate
- incorrect sub-decision
- formatting/schema error

## Hypothesis framing

The existing project brief proposes approximately 75–80% agreement with the human/reference baseline as a research target. This is a hypothesis, not a guaranteed acceptance threshold.
