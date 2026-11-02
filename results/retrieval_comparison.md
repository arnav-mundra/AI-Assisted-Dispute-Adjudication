# Clause retrieval comparison

Reference governing clauses (SLA-PRI-02 excluded) vs. what each retriever returns. The SLA has 29 clauses. Dense embeddings were available.

**Ranker recall** is the method's own top-k. **Context recall** is what reaches the prompt after pinned rules, gates, fact triggers and cross-references are added; *mean context* is what that costs in clauses.

## counterfactual

| Retriever | k | Ranker recall | Context recall | Mean context (clauses) |
|---|---|---|---|---|
| lexical | 4 | 41% | 73% | 11.4 |
| lexical | 8 | 55% | 86% | 14.1 |
| lexical | 12 | 73% | 91% | 17.1 |
| bm25 | 4 | 41% | 73% | 11.4 |
| bm25 | 8 | 55% | 86% | 14.2 |
| bm25 | 12 | 77% | 95% | 17.2 |
| dense | 4 | 45% | 64% | 11.3 |
| dense | 8 | 86% | 91% | 14.4 |
| dense | 12 | 95% | 100% | 17.6 |
| hybrid | 4 | 45% | 100% | 13.6 |
| hybrid | 8 | 68% | 100% | 15.6 |
| hybrid | 12 | 95% | 100% | 16.6 |

Reference clauses that never reached the prompt:

- lexical k=4: CF-104 → SLA-DG-03; CF-106 → SLA-DG-04; CF-107 → SLA-DG-08; CF-113 → SLA-COD-04; CF-115 → SLA-COD-04; CF-116 → SLA-DG-08
- lexical k=8: CF-104 → SLA-DG-03; CF-106 → SLA-DG-04; CF-107 → SLA-DG-08
- lexical k=12: CF-104 → SLA-DG-03; CF-107 → SLA-DG-08
- bm25 k=4: CF-104 → SLA-DG-03; CF-106 → SLA-DG-04; CF-107 → SLA-DG-08; CF-113 → SLA-COD-04; CF-115 → SLA-COD-04; CF-116 → SLA-DG-08
- bm25 k=8: CF-104 → SLA-DG-03; CF-107 → SLA-DG-08; CF-116 → SLA-DG-08
- bm25 k=12: CF-104 → SLA-DG-03
- dense k=4: CF-104 → SLA-DG-03; CF-105 → SLA-DG-09; CF-107 → SLA-DG-08; CF-112 → SLA-COD-03; CF-113 → SLA-COD-04; CF-114 → SLA-COD-03; CF-115 → SLA-COD-04; CF-116 → SLA-DG-08
- dense k=8: CF-104 → SLA-DG-03; CF-116 → SLA-DG-08

## pilot

| Retriever | k | Ranker recall | Context recall | Mean context (clauses) |
|---|---|---|---|---|
| lexical | 4 | 44% | 64% | 11.2 |
| lexical | 8 | 68% | 80% | 14.1 |
| lexical | 12 | 88% | 96% | 16.9 |
| bm25 | 4 | 36% | 56% | 11.2 |
| bm25 | 8 | 68% | 80% | 14.4 |
| bm25 | 12 | 84% | 92% | 17.3 |
| dense | 4 | 28% | 52% | 11.4 |
| dense | 8 | 76% | 88% | 14.5 |
| dense | 12 | 88% | 100% | 17.8 |
| hybrid | 4 | 36% | 100% | 13.7 |
| hybrid | 8 | 72% | 100% | 15.7 |
| hybrid | 12 | 92% | 100% | 17.1 |

Reference clauses that never reached the prompt:

- lexical k=4: COD-001 → SLA-COD-04, SLA-COD-08; COD-002 → SLA-COD-05; COD-003 → SLA-COD-04; COD-005 → SLA-COD-09; DG-003 → SLA-DG-08; DG-004 → SLA-DG-08; DG-005 → SLA-DG-03, SLA-DG-04
- lexical k=8: COD-001 → SLA-COD-08; COD-005 → SLA-COD-09; DG-003 → SLA-DG-08; DG-005 → SLA-DG-03, SLA-DG-04
- lexical k=12: COD-005 → SLA-COD-09
- bm25 k=4: COD-001 → SLA-COD-04, SLA-COD-08; COD-002 → SLA-COD-05; COD-003 → SLA-COD-04; COD-005 → SLA-COD-09; DG-003 → SLA-DG-05, SLA-DG-08; DG-004 → SLA-DG-03, SLA-DG-08; DG-005 → SLA-DG-03, SLA-DG-04
- bm25 k=8: COD-001 → SLA-COD-08; COD-005 → SLA-COD-09; DG-003 → SLA-DG-08; DG-004 → SLA-DG-08; DG-005 → SLA-DG-03
- bm25 k=12: COD-005 → SLA-COD-09; DG-003 → SLA-DG-08
- dense k=4: COD-001 → SLA-COD-03, SLA-COD-04, SLA-COD-08; COD-003 → SLA-COD-03, SLA-COD-04; COD-005 → SLA-COD-03, SLA-COD-09; DG-003 → SLA-DG-05, SLA-DG-08; DG-004 → SLA-DG-03, SLA-DG-08; DG-005 → SLA-DG-03
- dense k=8: COD-001 → SLA-COD-08; COD-005 → SLA-COD-09; DG-004 → SLA-DG-08

## Did the escalation cases see their clauses? (hybrid, k=12, as in the experiments)

| Case | Reference clause | In the prompt | Why it was included |
|---|---|---|---|
| DG-003 | SLA-DG-05 | yes | hybrid rank (lexical + BM25 + dense) |
| DG-003 | SLA-DG-08 | yes | hybrid rank (lexical + BM25 + dense) |
| DG-004 | SLA-DG-03 | yes | hybrid rank (lexical + BM25 + dense) |
| DG-004 | SLA-DG-05 | yes | hybrid rank (lexical + BM25 + dense) |
| DG-004 | SLA-DG-08 | yes | hybrid rank (lexical + BM25 + dense) |
| COD-005 | SLA-COD-03 | yes | hybrid rank (lexical + BM25 + dense) |
| COD-005 | SLA-COD-09 | yes | fact: contested amount with corroboration on both sides |
| COD-005 | SLA-PRI-01 | yes | always in context (adjudication rule) |
