# Held-out inter-annotator agreement

- Cases labelled by both annotators: **34**
- Raw decision agreement: **91%**
- Cohen's κ (decision): **0.86** (almost perfect, Landis & Koch)
- Governing clauses — mean Jaccard: 0.87; identical sets: 71% (SLA-PRI-02 excluded; sub-clause letters ignored)
- Decisive evidence — mean Jaccard: 0.96
- Resolution type agreement: 91%

## Per-clause citation agreement

| Clause | Cited by A | Cited by B | Both | κ |
|---|---|---|---|---|
| SLA-COD-01 | 2 | 3 | 2 | 0.78 |
| SLA-COD-02 | 1 | 1 | 1 | 1.00 |
| SLA-COD-03 | 7 | 7 | 7 | 1.00 |
| SLA-COD-04 | 4 | 4 | 4 | 1.00 |
| SLA-COD-05 | 2 | 2 | 2 | 1.00 |
| SLA-COD-06 | 3 | 3 | 3 | 1.00 |
| SLA-COD-07 | 2 | 2 | 2 | 1.00 |
| SLA-COD-08 | 0 | 1 | 0 | 0.00 |
| SLA-COD-09 | 2 | 2 | 2 | 1.00 |
| SLA-DEF-03 | 1 | 0 | 0 | 0.00 |
| SLA-DG-01 | 8 | 7 | 6 | 0.74 |
| SLA-DG-02 | 3 | 5 | 3 | 0.72 |
| SLA-DG-03 | 2 | 2 | 2 | 1.00 |
| SLA-DG-04 | 4 | 4 | 4 | 1.00 |
| SLA-DG-05 | 2 | 2 | 2 | 1.00 |
| SLA-DG-06 | 7 | 8 | 7 | 0.91 |
| SLA-DG-07 | 2 | 2 | 2 | 1.00 |
| SLA-DG-08 | 2 | 2 | 2 | 1.00 |
| SLA-DG-09 | 2 | 2 | 2 | 1.00 |
| SLA-PRI-01 | 7 | 4 | 4 | 0.68 |

## Cases needing adjudication

Resolve each in `adjudication.csv` (third person, blind to model output and to the design-intent file).

| Case | Issues | A | B | A clauses | B clauses |
|---|---|---|---|---|---|
| HO-002 | clauses | APPROVE | APPROVE | SLA-DG-01, SLA-DG-02, SLA-DG-06 | SLA-DG-02, SLA-DG-06 |
| HO-003 | clauses | REJECT | REJECT | SLA-DG-01 | SLA-DG-01, SLA-DG-02 |
| HO-007 | decision, resolution | APPROVE | ESCALATE | SLA-DG-06, SLA-DG-09 | SLA-DG-06, SLA-DG-09 |
| HO-010 | decision, clauses, resolution | REJECT | APPROVE | SLA-DG-03 | SLA-DG-03, SLA-DG-06 |
| HO-011 | clauses | APPROVE | APPROVE | SLA-DG-03, SLA-DG-04 | SLA-DG-01, SLA-DG-03, SLA-DG-04 |
| HO-013 | clauses | APPROVE | APPROVE | SLA-DG-01, SLA-DG-04, SLA-PRI-01 | SLA-DG-04, SLA-PRI-01 |
| HO-014 | clauses | ESCALATE | ESCALATE | SLA-DG-04, SLA-DG-08, SLA-PRI-01 | SLA-DG-04, SLA-DG-08 |
| HO-015 | clauses | REJECT | REJECT | SLA-DG-01 | SLA-DG-01, SLA-DG-02 |
| HO-024 | clauses | APPROVE | APPROVE | SLA-COD-05, SLA-DEF-03 | SLA-COD-01, SLA-COD-05 |
| HO-025 | decision, resolution | REJECT | ESCALATE | SLA-COD-05, SLA-PRI-01 | SLA-COD-05, SLA-PRI-01 |
| HO-030 | clauses | APPROVE | APPROVE | SLA-COD-03, SLA-PRI-01 | SLA-COD-03, SLA-COD-08 |
| HO-033 | clauses | ESCALATE | ESCALATE | SLA-COD-06, SLA-COD-09, SLA-PRI-01 | SLA-COD-06, SLA-COD-09 |
