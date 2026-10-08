"""Phase 3 — SLA clause parsing and retrieval.

`sla_clauses` splits the SLA into addressable clauses; `clause_retrieval`
ranks them (lexical, BM25, optional dense, hybrid + fact triggers). Every
method returns `RetrievedClause`, so the reasoning engine and UI are
unaffected by the choice.
"""
