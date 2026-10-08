"""Phase 2 — evidence access and extraction.

`case_loader` exposes cases and their evidence items; `extractor` reads that
evidence into typed, source-linked facts (timing, PoD state, damage
specificity, unboxing, COD amounts) that retrieval, the prompts and the rules
engine all consume. `manual_case` builds a case from the New dispute form.
"""
