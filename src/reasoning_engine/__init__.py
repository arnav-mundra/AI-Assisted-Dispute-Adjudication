"""Phase 4 slot — SLA-grounded adjudication.

Builds the prompt from a case plus its retrieved clauses, calls a provider from
`src.llm`, and validates the structured response against the SLA and the case
before returning it. Multi-model comparison is a loop over registered providers;
nothing here is vendor-specific.
"""
