# Rules engine — suspected issues log

`src/reasoning_engine/rules_engine.py` is frozen at git tag `rules-engine-frozen-v1`
(blob `9016d663`), enforced by `tests/test_rules_engine_frozen.py`. Suspected bugs are
recorded here and **not fixed**, so that the held-out evaluation measures the engine as it
stood before the held-out cases existed.

Each entry: date, who, the clause involved, a minimal description of the suspected
behaviour, and how it was noticed. Do not note how the engine scores on any held-out case
until the held-out labels are final.

| Date | Reporter | Clause(s) | Suspected issue | How noticed |
|---|---|---|---|---|
| — | — | — | None recorded. | During held-out case construction (2026-10-22) the engine was deliberately neither opened nor run, so that the cases could not be shaped around it. |
| 2026-10-25 | Code audit | SLA-DG-01/02, SLA-COD-01 | The reporting-window rule stops only when `within_window` is `False`. When the reporting time is unknown (`None`, e.g. missing timestamps) it continues as if the claim were on time, so a case can reach APPROVE with no window check. No current pilot or counterfactual case has an unknown window. | Code reading; confirmed by removing the timestamps from a pilot damaged-goods case. |
