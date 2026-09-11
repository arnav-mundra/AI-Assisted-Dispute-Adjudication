"""Phase 3 slot — SLA clause parsing and retrieval.

Today: the SLA is split into addressable clauses and ranked lexically against
the case. Later: sentence-transformer embeddings + FAISS/Chroma. `retrieve()`
returns `RetrievedClause` either way, so the reasoning engine and UI are
unaffected by the swap.
"""
