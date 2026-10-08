"""Dispute Adjudicator — application entry point.

    python -m streamlit run app/main.py

Pipeline (each stage is its own package and can be replaced independently):

    case evidence ─► evidence extraction  src/evidence_extraction/   (Phase 2)
                  ─► clause retrieval     src/clause_matching/       (Phase 3)
                  ─► reasoning engine     src/reasoning_engine/ + src/llm/  (Phase 4)
                  ─► validation + rules cross-check
                  ─► evaluation           src/evaluation/            (Phase 6)
"""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Dispute Adjudicator", page_icon="⚖️", layout="wide",
                   initial_sidebar_state="expanded")

from app.ui import theme  # noqa: E402
from app.ui import (  # noqa: E402
    adjudication_page, evaluation_page, new_dispute_page, overview_page, policy_page, whatif_page,
)
from app.ui.settings import Settings  # noqa: E402
from src.clause_matching.clause_retrieval import dense_available  # noqa: E402
from src.clause_matching.sla_clauses import load_clauses, sla_version  # noqa: E402
from src.evidence_extraction.case_loader import load_cases  # noqa: E402
from src.llm import all_models, available_models, provider_status  # noqa: E402
from src.reasoning_engine.adjudicator import PROMPT_STYLES, default_model  # noqa: E402

theme.inject_css()

PAGES = {
    "Overview": overview_page,
    "Adjudicate a case": adjudication_page,
    "New dispute": new_dispute_page,
    "What-if explorer": whatif_page,
    "Evaluation": evaluation_page,
    "SLA policy": policy_page,
}
ENGINE_LABELS = {
    "auto": "Automatic (LLM if configured)",
    "llm": "LLM reasoning engine",
    "rules": "Rules engine (offline)",
}
STYLE_LABELS = {"zero_shot": "Zero-shot", "facts": "Fact-grounded", "cot": "Fact-grounded + reasoning steps"}

with st.sidebar:
    theme.brand()
    page = st.radio("Go to", list(PAGES), label_visibility="collapsed",
                    key="page")

    st.divider()
    usable = set(available_models())
    engine = st.selectbox("Decision engine", list(ENGINE_LABELS), format_func=ENGINE_LABELS.get,
                          help="The rules engine needs no API key and is used as the cross-check for the LLM.")
    models = all_models()
    preferred = default_model()
    model = st.selectbox("Model", models, index=models.index(preferred) if preferred in models else 0,
                         format_func=lambda m: m if m in usable else f"{m} (no key)",
                         disabled=engine == "rules")
    prompt_style = st.selectbox("Prompt style", list(PROMPT_STYLES), index=1, format_func=STYLE_LABELS.get,
                                disabled=engine == "rules")
    with st.expander("Retrieval settings"):
        methods = ["hybrid", "lexical", "bm25"] + (["dense"] if dense_available() else [])
        retrieval = st.selectbox("Clause retriever", methods)
        top_k = st.slider("Clauses ranked into context", 2, 20, 8,
                          help="Priority rules, eligibility gates, fact-triggered and cross-referenced "
                               "clauses are always added on top.")

    settings = Settings(engine=engine, model=model, prompt_style=prompt_style, retrieval=retrieval,
                        top_k=top_k, llm_ready=model in usable)

    st.divider()
    for row in provider_status():
        theme.status(row["label"], bool(row["available"]), str(row["status"]))
    theme.status("Rules engine", True, "ready")
    theme.status(f"SLA v{sla_version()}", True, f"{len(load_clauses())} clauses")
    theme.status("Pilot dataset", True, f"{len(load_cases())} cases")
    if engine != "rules" and not settings.llm_ready:
        theme.md('<div class="side-note">No LLM key is configured, so cases are decided by the rules '
                 'engine. Add GROQ_API_KEY to .env (or Streamlit secrets) to use the model.</div>')

PAGES[page].render(settings)
